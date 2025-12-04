# backend/app/routes/admin_counselors.py

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.student import Student, RiskLevel
from ..models.user import User
from ..schemas import CounselorSummary
from ..auth.auth_handler import get_current_user

router = APIRouter(prefix="/admin/counselors", tags=["Admin Counselors"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Allow only admin users to access these routes.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def classify_student_area(student: Student) -> str:
    """
    Classify student's primary issue area based on cluster and features.
    Used to match with counselor.specialization.
    Returns one of: "academic", "financial", "attendance", "mental",
                    "behavioural", "general"
    """
    # First, use cluster_id if present
    if student.cluster_id == 1:
        return "academic"
    if student.cluster_id == 2:
        return "financial"
    if student.cluster_id == 3:
        return "attendance"  # disengaged / low engagement

    # Heuristics if cluster not set
    if student.fees_pending or (student.fees_amount_due or 0) > 0:
        return "financial"

    if (student.backlogs or 0) >= 2 or (student.cgpa or 10.0) < 6.0:
        return "academic"

    if (student.attendance_percentage or 100.0) < 75.0 or (
        student.bot_engagement_score or 100.0
    ) < 40.0:
        return "attendance"

    # For now, we don't have strong mental/behavioural signals
    return "general"


def build_specialized_assignment(
    counselors: List[User], students: List[Student]
) -> Dict[int, List[Student]]:
    """
    Assign students to counselors in a specialization-aware way.

    - Group counselors by specialization (lowercase string).
    - For each student, compute an "area" (academic/financial/attendance/...).
    - If we have counselors for that area, assign in a deterministic way
      among that group (based on student.id).
    - Otherwise, assign among all counselors.

    This is a VIRTUAL assignment for dashboard/demo; it does NOT change DB.
    """
    mapping: Dict[int, List[Student]] = {c.id: [] for c in counselors}
    if not counselors:
        return mapping

    # Group counselors by specialization
    spec_map: Dict[str, List[User]] = {}
    for c in counselors:
        key = (c.specialization or "").strip().lower() or "general"
        spec_map.setdefault(key, []).append(c)

    all_pool = counselors

    for s in students:
        area = classify_student_area(s)  # e.g. "academic"
        pool = spec_map.get(area) or all_pool
        if not pool:
            continue
        # Deterministic index based on student.id
        idx = s.id % len(pool)
        assigned = pool[idx]
        mapping[assigned.id].append(s)

    return mapping


@router.get("/summary", response_model=List[CounselorSummary])
def get_counselor_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Admin view: summary per counselor using specialization-aware
    virtual assignment of students.
    """
    counselors = (
        db.query(User)
        .filter(User.role == "counselor")
        .filter(User.is_active == True)
        .all()
    )
    students = db.query(Student).all()

    mapping = build_specialized_assignment(counselors, students)
    results: List[CounselorSummary] = []

    for c in counselors:
        assigned = mapping.get(c.id, [])
        total = len(assigned)

        high = sum(1 for s in assigned if s.final_risk == RiskLevel.RED)
        medium = sum(1 for s in assigned if s.final_risk == RiskLevel.YELLOW)
        low = sum(1 for s in assigned if s.final_risk == RiskLevel.GREEN)

        unresolved = high + medium
        resolved = low

        total_sessions = sum(s.counselling_sessions or 0 for s in assigned)
        avg_prob = (
            float(
                sum((s.dropout_probability or 0.0) for s in assigned) / total
            )
            if total > 0
            else 0.0
        )

        results.append(
            CounselorSummary(
                id=c.id,
                username=c.username,
                full_name=c.full_name,
                email=c.email,
                specialization=c.specialization,
                total_students=total,
                high_risk=high,
                medium_risk=medium,
                low_risk=low,
                unresolved_cases=unresolved,
                resolved_cases=resolved,
                total_counselling_sessions=total_sessions,
                avg_dropout_probability=avg_prob,
            )
        )

    return results


@router.get("/{counselor_id}/students")
def get_counselor_students(
    counselor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    List students virtually assigned to a specific counselor,
    using the same specialization-aware logic as the summary.
    """
    counselors = (
        db.query(User)
        .filter(User.role == "counselor")
        .filter(User.is_active == True)
        .all()
    )
    students = db.query(Student).all()
    if not any(c.id == counselor_id for c in counselors):
        raise HTTPException(status_code=404, detail="Counselor not found")

    mapping = build_specialized_assignment(counselors, students)
    return mapping.get(counselor_id, [])