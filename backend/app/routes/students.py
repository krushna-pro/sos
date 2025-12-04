# backend/app/routes/students.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import TextIOWrapper

from ..database import get_db
from ..models.student import Student, RiskLevel
from ..models.user import User
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    RiskAnalysis,
    StudentBrief,
)
from ..auth.auth_handler import (
    get_current_user,
    require_counselor_or_admin,
)
from ..ml.rules import calculate_baseline_risk
from ..ml.prediction import predictor
from ..ml.recommendations import generate_recommendations

router = APIRouter(prefix="/students", tags=["Students"])


def parse_bool(value: str) -> bool:
    """
    Helper to parse CSV boolean-like values.
    Accepts: true/false, 1/0, yes/no, y/n (case-insensitive).
    """
    if value is None:
        return False
    v = value.strip().lower()
    return v in ("1", "true", "yes", "y")


def _set_risk_fields(
    student: Student,
    baseline_risk: RiskLevel,
    ml_prob: float,
    cluster_id: Optional[int] = None,
) -> None:
    """
    Central helper to update all risk-related fields on Student, including stage.
    """
    student.baseline_risk = baseline_risk
    student.ml_risk_score = ml_prob * 100.0
    student.dropout_probability = ml_prob
    if cluster_id is not None:
        student.cluster_id = cluster_id

    # Combine rule + ML into final risk (same thresholds as bot.py)
    if ml_prob >= 0.7 or baseline_risk == RiskLevel.RED:
        student.final_risk = RiskLevel.RED
        student.stage = 3
    elif ml_prob >= 0.4 or baseline_risk == RiskLevel.YELLOW:
        student.final_risk = RiskLevel.YELLOW
        student.stage = 2
    else:
        student.final_risk = RiskLevel.GREEN
        student.stage = 1


@router.post("/", response_model=StudentResponse)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Add a new student.
    Only admin/counselor can add.
    """
    # Check unique student_id and email
    if db.query(Student).filter(Student.student_id == student_in.student_id).first():
        raise HTTPException(status_code=400, detail="Student ID already exists")

    if db.query(Student).filter(Student.email == student_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    db_student = Student(**student_in.dict())

    # Basic baseline risk (rule-based), ML not run here yet
    baseline_risk, _ = calculate_baseline_risk(db_student)
    db_student.baseline_risk = baseline_risk
    db_student.final_risk = baseline_risk
    # stage stays at default=1

    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/", response_model=List[StudentResponse])
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    risk: Optional[RiskLevel] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get list of students.
    Optional filter: ?risk=green / yellow / red
    """
    query = db.query(Student)
    if risk:
        query = query.filter(Student.final_risk == risk)
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full details of a single student by student_id.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Update student academic/behavioural data.
    Recalculates baseline + ML risk + stage.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Apply updates
    for field, value in student_update.dict(exclude_unset=True).items():
        setattr(student, field, value)

    # Recalculate baseline (rules)
    baseline_risk, _ = calculate_baseline_risk(student)

    # ML prediction
    ml_prob, cluster_id = predictor.predict(student)

    # Update all risk fields including stage
    _set_risk_fields(student, baseline_risk, ml_prob, cluster_id)

    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}/analyze", response_model=RiskAnalysis)
def analyze_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform full risk analysis for a student:
    - rule-based risk
    - ML dropout probability
    - cluster profile
    - textual recommendations
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Rule-based analysis
    baseline_risk, risk_factors = calculate_baseline_risk(student)

    # ML prediction
    ml_prob, cluster_id = predictor.predict(student)
    cluster_info = predictor.get_cluster_info(cluster_id)

    # Update DB fields and stage
    _set_risk_fields(student, baseline_risk, ml_prob, cluster_id)
    db.commit()
    db.refresh(student)

    # Get recommendation text
    recommendations = generate_recommendations(student, risk_factors, cluster_info)

    return RiskAnalysis(
        student_id=student.student_id,
        name=student.name,
        baseline_risk=baseline_risk,
        ml_risk_score=ml_prob * 100,
        final_risk=student.final_risk,
        dropout_probability=ml_prob,
        risk_factors=risk_factors,
        recommendations=recommendations,
        cluster_id=cluster_id,
        cluster_name=cluster_info["name"],
        cluster_description=cluster_info["description"],
        stage=student.stage,
    )


@router.get("/brief/list", response_model=List[StudentBrief])
def list_brief(
    db: Session = Depends(get_db),
):
    """
    Simple list for dashboard tables.
    PUBLIC for demo: no auth required.
    """
    students = db.query(Student).all()
    return students


@router.post("/import-attendance-csv")
def import_attendance_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Bulk update attendance_percentage from CSV.

    Expected CSV header:
    student_id,attendance_percentage
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    wrapper = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.DictReader(wrapper)

    updated = 0
    not_found = []

    for idx, row in enumerate(reader, start=2):  # row 1 is header
        student_id = row.get("student_id")
        if not student_id:
            continue

        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            not_found.append(student_id)
            continue

        att_str = row.get("attendance_percentage")
        if att_str is None or att_str == "":
            continue

        try:
            student.attendance_percentage = float(att_str)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Row {idx}: invalid attendance_percentage '{att_str}': {e}",
            )

        updated += 1

    db.commit()
    return {"updated": updated, "not_found": not_found}


@router.post("/import-academics-csv")
def import_academics_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Bulk update academic + engagement fields from CSV.

    Expected CSV header (any subset is okay):
    student_id,cgpa,backlogs,quiz_score_avg,bot_engagement_score,counselling_sessions
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    wrapper = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.DictReader(wrapper)

    updated = 0
    not_found = []

    for idx, row in enumerate(reader, start=2):
        student_id = row.get("student_id")
        if not student_id:
            continue

        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            not_found.append(student_id)
            continue

        # Each field optional; if present and not empty, update
        cgpa = row.get("cgpa")
        if cgpa not in (None, ""):
            try:
                student.cgpa = float(cgpa)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid cgpa '{cgpa}': {e}",
                )

        backlogs = row.get("backlogs")
        if backlogs not in (None, ""):
            try:
                student.backlogs = int(backlogs)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid backlogs '{backlogs}': {e}",
                )

        quiz_score_avg = row.get("quiz_score_avg")
        if quiz_score_avg not in (None, ""):
            try:
                student.quiz_score_avg = float(quiz_score_avg)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid quiz_score_avg '{quiz_score_avg}': {e}",
                )

        bot_engagement_score = row.get("bot_engagement_score")
        if bot_engagement_score not in (None, ""):
            try:
                student.bot_engagement_score = float(bot_engagement_score)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid bot_engagement_score '{bot_engagement_score}': {e}",
                )

        counselling_sessions = row.get("counselling_sessions")
        if counselling_sessions not in (None, ""):
            try:
                student.counselling_sessions = int(counselling_sessions)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid counselling_sessions '{counselling_sessions}': {e}",
                )

        updated += 1

    db.commit()
    return {"updated": updated, "not_found": not_found}


@router.post("/import-fees-csv")
def import_fees_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Bulk update fees_pending and fees_amount_due from CSV.

    Expected CSV header:
    student_id,fees_pending,fees_amount_due
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    wrapper = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.DictReader(wrapper)

    updated = 0
    not_found = []

    for idx, row in enumerate(reader, start=2):
        student_id = row.get("student_id")
        if not student_id:
            continue

        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            not_found.append(student_id)
            continue

        fees_pending = row.get("fees_pending")
        if fees_pending not in (None, ""):
            student.fees_pending = parse_bool(fees_pending)

        fees_amount_due = row.get("fees_amount_due")
        if fees_amount_due not in (None, ""):
            try:
                student.fees_amount_due = float(fees_amount_due)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {idx}: invalid fees_amount_due '{fees_amount_due}': {e}",
                )

        updated += 1

    db.commit()
    return {"updated": updated, "not_found": not_found}


@router.post("/import-base-csv", response_model=List[StudentResponse])
def import_base_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Bulk create students from CSV.

    Expected CSV header:
    student_id,name,email,phone,department,semester,
    attendance_percentage,cgpa,backlogs,fees_pending,fees_amount_due,
    quiz_score_avg,bot_engagement_score,counselling_sessions
    (parent_name/parent_phone/parent_email optional)
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    wrapper = TextIOWrapper(file.file, encoding="utf-8")
    reader = csv.DictReader(wrapper)

    created_students = []

    for idx, row in enumerate(reader, start=2):  # row 1 is header
        student_id = row.get("student_id")
        email = row.get("email")
        name = row.get("name")

        if not student_id or not email or not name:
            raise HTTPException(
                status_code=400,
                detail=f"Row {idx}: student_id, name and email are required",
            )

        # Skip if student_id or email already exists
        if db.query(Student).filter(Student.student_id == student_id).first():
            continue
        if db.query(Student).filter(Student.email == email).first():
            continue

        try:
            # Note: StudentCreate must define these fields if you use them here
            student_in = StudentCreate(
                student_id=student_id,
                name=name,
                email=email,
                phone=row.get("phone", ""),
                department=row.get("department", ""),
                semester=int(row.get("semester", 0) or 0),
                attendance_percentage=float(
                    row.get("attendance_percentage", 0) or 0
                ),
                cgpa=float(row.get("cgpa", 0) or 0),
                backlogs=int(row.get("backlogs", 0) or 0),
                fees_pending=parse_bool(row.get("fees_pending", "false")),
                fees_amount_due=float(row.get("fees_amount_due", 0) or 0),
                # Parent info if present
                parent_name=row.get("parent_name") or None,
                parent_phone=row.get("parent_phone") or None,
                parent_email=row.get("parent_email") or None,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Row {idx}: invalid data - {e}",
            )

        # Create Student from schema
        db_student = Student(**student_in.dict())

        baseline_risk, _ = calculate_baseline_risk(db_student)
        db_student.baseline_risk = baseline_risk
        db_student.final_risk = baseline_risk

        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        created_students.append(db_student)

    return created_students