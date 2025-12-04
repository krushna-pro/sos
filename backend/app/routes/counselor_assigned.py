# backend/app/routes/counselor_assigned.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.student import Student
from ..models.user import User
from ..auth.auth_handler import get_current_user
from .admin_counselors import build_specialized_assignment  # reuse logic

router = APIRouter(prefix="/counselor", tags=["Counselor"])


def require_counselor(current_user: User = Depends(get_current_user)) -> User:
  if current_user.role != "counselor":
      raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Counselor access required",
      )
  return current_user


@router.get("/assigned")
def get_my_assigned_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor),
):
    """
    Return students virtually assigned to the current counselor,
    using the same specialization-aware assignment logic.
    """
    counselors = (
        db.query(User)
        .filter(User.role == "counselor")
        .filter(User.is_active == True)
        .all()
    )
    students = db.query(Student).all()

    mapping = build_specialized_assignment(counselors, students)
    return mapping.get(current_user.id, [])