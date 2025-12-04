# backend/app/routes/clusters.py

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import requests

from ..database import get_db
from ..models.student import Student, RiskLevel
from ..models.user import User
from ..auth.auth_handler import require_counselor_or_admin
from ..ml.prediction import predictor
from ..schemas import ClusterOverview, ClusterBroadcastRequest, StudentBrief

router = APIRouter(prefix="/clusters", tags=["Clusters"])

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_API_BASE = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
    if TELEGRAM_BOT_TOKEN
    else None
)


def _send_telegram_message(chat_id: str, text: str):
    """
    Send a plain text message to a Telegram chat.
    Used for counselor-triggered broadcasts.
    """
    if not TG_API_BASE:
        # Bot token not configured in this process, just skip
        return
    try:
        requests.post(
            TG_API_BASE + "sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
    except Exception:
        # Don't crash if Telegram call fails
        pass


@router.get("/overview", response_model=List[ClusterOverview])
def get_cluster_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Return summary per cluster:
    - cluster info (name, description, issues, focus)
    - counts of students by risk and stage
    """
    results: List[ClusterOverview] = []

    # Assuming cluster IDs 0..3 from predictor
    for cid in range(4):
        info = predictor.get_cluster_info(cid)
        q = db.query(Student).filter(Student.cluster_id == cid)
        students = q.all()

        total = len(students)
        green = sum(1 for s in students if s.final_risk == RiskLevel.GREEN)
        yellow = sum(1 for s in students if s.final_risk == RiskLevel.YELLOW)
        red = sum(1 for s in students if s.final_risk == RiskLevel.RED)
        stage1 = sum(1 for s in students if s.stage == 1)
        stage2 = sum(1 for s in students if s.stage == 2)
        stage3 = sum(1 for s in students if s.stage == 3)

        results.append(
            ClusterOverview(
                cluster_id=cid,
                name=info["name"],
                description=info["description"],
                typical_issues=info.get("typical_issues", []),
                recommended_focus=info.get("intervention", ""),
                total_students=total,
                green=green,
                yellow=yellow,
                red=red,
                stage1=stage1,
                stage2=stage2,
                stage3=stage3,
            )
        )

    return results


@router.get("/{cluster_id}/students", response_model=List[StudentBrief])
def get_cluster_students(
    cluster_id: int,
    stage: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    List students belonging to a given cluster.
    Optional filter by stage: ?stage=2
    """
    q = db.query(Student).filter(Student.cluster_id == cluster_id)
    if stage is not None:
        q = q.filter(Student.stage == stage)
    students = q.all()
    # FastAPI + StudentBrief(from_attributes=True) will convert automatically
    return students


@router.post("/{cluster_id}/broadcast")
def broadcast_to_cluster(
    cluster_id: int,
    payload: ClusterBroadcastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_counselor_or_admin),
):
    """
    Counselor-triggered broadcast.
    Sends a short activity/message to all students in this cluster whose
    stage is between min_stage and max_stage (inclusive), and who have a
    linked Telegram chat (telegram_chat_id is set).
    """
    q = (
        db.query(Student)
        .filter(Student.cluster_id == cluster_id)
        .filter(Student.stage >= payload.min_stage)
        .filter(Student.stage <= payload.max_stage)
        .filter(Student.telegram_chat_id.isnot(None))
    )
    students = q.all()
    if not students:
        raise HTTPException(
            status_code=404,
            detail="No students found for this cluster / stage range",
        )

    text = f"{payload.message_title}\n\n{payload.message_body}"
    sent = 0
    for s in students:
        _send_telegram_message(s.telegram_chat_id, text)
        sent += 1

    return {"sent": sent}