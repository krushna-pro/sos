# backend/app/routes/dashboard.py

from typing import List, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.student import Student, RiskLevel
from ..models.user import User
from ..schemas import (
    DashboardStats,
    DepartmentRisk,
    AtRiskStudent,
)
from ..auth.auth_handler import get_current_user
from ..ml.prediction import predictor

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Overall numbers for top cards:
    - total students
    - green/yellow/red counts
    - average attendance, cgpa
    - how many have backlogs, pending fees
    """
    total = db.query(Student).count()
    green = db.query(Student).filter(Student.final_risk == RiskLevel.GREEN).count()
    yellow = db.query(Student).filter(Student.final_risk == RiskLevel.YELLOW).count()
    red = db.query(Student).filter(Student.final_risk == RiskLevel.RED).count()

    avg_attendance = db.query(func.avg(Student.attendance_percentage)).scalar() or 0
    avg_cgpa = db.query(func.avg(Student.cgpa)).scalar() or 0

    students_with_backlogs = db.query(Student).filter(Student.backlogs > 0).count()
    fees_pending_count = db.query(Student).filter(Student.fees_pending == True).count()

    return DashboardStats(
        total_students=total,
        green_count=green,
        yellow_count=yellow,
        red_count=red,
        avg_attendance=round(avg_attendance, 2),
        avg_cgpa=round(avg_cgpa, 2),
        students_with_backlogs=students_with_backlogs,
        fees_pending_count=fees_pending_count,
    )


@router.get("/risk-distribution", response_model=List[DepartmentRisk])
def risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Department-wise count of green/yellow/red.
    Used for bar charts.
    """
    rows = (
        db.query(
            Student.department,
            Student.final_risk,
            func.count(Student.id),
        )
        .group_by(Student.department, Student.final_risk)
        .all()
    )

    by_dept: Dict[str, Dict[str, int]] = {}
    for dept, risk, count in rows:
        if dept not in by_dept:
            by_dept[dept] = {"green": 0, "yellow": 0, "red": 0}
        by_dept[dept][risk.value] = count

    result: List[DepartmentRisk] = []
    for dept, counts in by_dept.items():
        total = counts["green"] + counts["yellow"] + counts["red"]
        result.append(
            DepartmentRisk(
                department=dept,
                green=counts["green"],
                yellow=counts["yellow"],
                red=counts["red"],
                total=total,
            )
        )

    return result


@router.get("/at-risk", response_model=List[AtRiskStudent])
def at_risk_students(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Top N at-risk students sorted by dropout_probability.
    """
    students = (
        db.query(Student)
        .filter(Student.final_risk.in_([RiskLevel.YELLOW, RiskLevel.RED]))
        .order_by(Student.dropout_probability.desc())
        .limit(limit)
        .all()
    )

    result: List[AtRiskStudent] = []
    for s in students:
        # Simple heuristic for main issue:
        if s.backlogs >= 3:
            main_issue = "Multiple backlogs"
        elif s.attendance_percentage < 60:
            main_issue = "Very low attendance"
        elif s.fees_pending:
            main_issue = "Pending fees"
        else:
            main_issue = "Low academic performance"

        result.append(
            AtRiskStudent(
                student_id=s.student_id,
                name=s.name,
                department=s.department,
                risk=s.final_risk,
                probability=round(s.dropout_probability * 100, 1),
                main_issue=main_issue,
            )
        )

    return result


@router.get("/feature-importance")
def feature_importance(
    current_user: User = Depends(get_current_user),
):
    """
    Returns which features (attendance, cgpa, etc.)
    most influence the ML model.
    """
    return predictor.get_feature_importance()