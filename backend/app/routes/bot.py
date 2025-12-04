# backend/app/routes/bot.py

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db, Base, engine
from ..models.student import Student, RiskLevel
from ..models import bot as bot_models  # StudentBotLink, BotActivityLog
from ..ml.prediction import predictor
from ..schemas import (
    BotRegisterRequest,
    BotActivityCreate,
    ActivityQuestion,
    DailyCheckupResponse,
)

# Dev convenience (for production use proper migrations)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/bot", tags=["Bot"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_daily_activities(student: Student) -> List[ActivityQuestion]:
    """
    Decide which questions/activities to send today.
    You can tune this logic by stage and cluster.
    """
    activities: List[ActivityQuestion] = []

    # Basic questions for all students
    activities.append(ActivityQuestion(
        activity_type="mood",
        activity_code="MOOD_1_5",
        question="On a scale 1-5, how is your mood today? (1=Very bad, 5=Great)",
        min_value=1,
        max_value=5,
    ))
    activities.append(ActivityQuestion(
        activity_type="study_hours",
        activity_code="STUDY_HOURS_0_10",
        question="How many hours did you study yesterday? (0-10)",
        min_value=0,
        max_value=10,
    ))
    activities.append(ActivityQuestion(
        activity_type="stress",
        activity_code="STRESS_1_5",
        question="On a scale 1-5, how stressed do you feel about studies? (1=No stress, 5=Very high)",
        min_value=1,
        max_value=5,
    ))

    # Cluster-specific extra questions (example)
    if student.cluster_id == 1:  # Academic strugglers
        activities.append(ActivityQuestion(
            activity_type="doubt_clearing",
            activity_code="DOUBT_0_1",
            question="Do you have unresolved doubts in any subject? (0=No, 1=Yes)",
            min_value=0,
            max_value=1,
        ))
    elif student.cluster_id == 2:  # Financially stressed
        activities.append(ActivityQuestion(
            activity_type="financial_worry",
            activity_code="FIN_WORRY_1_5",
            question="On a scale 1-5, how worried are you about fees/finances?",
            min_value=1,
            max_value=5,
        ))
    else:  # default extra
        activities.append(ActivityQuestion(
            activity_type="engagement",
            activity_code="ENG_1_5",
            question="On a scale 1-5, how motivated do you feel to attend classes today?",
            min_value=1,
            max_value=5,
        ))

    return activities


def _recompute_engagement_from_logs(student: Student, db: Session):
    """
    Update student's bot_engagement_score from recent bot logs.
    Assumes BotActivityLog has a created_at column.
    """
    week_ago = datetime.utcnow() - timedelta(days=7)

    logs_q = (
        db.query(bot_models.BotActivityLog)
        .filter(
            bot_models.BotActivityLog.student_id == student.student_id,
            bot_models.BotActivityLog.created_at >= week_ago,
        )
    )

    logs = logs_q.all()
    if not logs:
        return

    # Simple metric: number of answers in last 7 days
    engagement = len(logs)

    # Normalize to 0–100
    student.bot_engagement_score = min(100.0, engagement * 5.0)


def _compute_final_risk_and_stage(student: Student, probability: float):
    """
    Map dropout probability → final_risk + stage.
    Tune thresholds as needed.
    """
    student.dropout_probability = probability
    student.ml_risk_score = probability * 100.0

    if probability < 0.3:
        student.final_risk = RiskLevel.GREEN
        student.stage = 1
    elif probability < 0.6:
        student.final_risk = RiskLevel.YELLOW
        student.stage = 2
    else:
        student.final_risk = RiskLevel.RED
        student.stage = 3

    student.last_risk_update = datetime.utcnow()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/register")
def register_student_for_bot(
    payload: BotRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Link a Telegram chat to a student_id.
    Called when student does /register <student_id>.
    """
    student = (
        db.query(Student)
        .filter(Student.student_id == payload.student_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Save chat_id on Student for easy access
    student.telegram_chat_id = payload.chat_id

    # Also keep StudentBotLink table (history, multi-device etc.)
    link = (
        db.query(bot_models.StudentBotLink)
        .filter(bot_models.StudentBotLink.chat_id == payload.chat_id)
        .first()
    )
    if link:
        link.student_id = payload.student_id
        link.username = payload.username
    else:
        link = bot_models.StudentBotLink(
            student_id=payload.student_id,
            chat_id=payload.chat_id,
            username=payload.username,
        )
        db.add(link)

    db.commit()
    return {"ok": True, "student_id": payload.student_id}


@router.get("/daily_checkup/{student_id}", response_model=DailyCheckupResponse)
def get_daily_checkup(
    student_id: str,
    db: Session = Depends(get_db),
):
    """
    Return today's questions/activities for a student.
    Telegram bot will ask these one by one.
    """
    student = (
        db.query(Student)
        .filter(Student.student_id == student_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    activities = _build_daily_activities(student)

    return DailyCheckupResponse(
        student_id=student.student_id,
        stage=student.stage,
        cluster_id=student.cluster_id,
        activities=activities,
    )


@router.post("/activity")
def log_bot_activity(
    payload: BotActivityCreate,
    db: Session = Depends(get_db),
):
    """
    Log a student bot activity/response and update risk & stage.

    Example (from bot):

    {
      "student_id": "S001",
      "chat_id": "123456789",
      "activity_type": "mood",
      "activity_code": "MOOD_1_5",
      "answer_text": "4",
      "score": 4
    }
    """
    student = (
        db.query(Student)
        .filter(Student.student_id == payload.student_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Store activity log
    log_entry = bot_models.BotActivityLog(
        student_id=payload.student_id,
        chat_id=payload.chat_id,
        activity_type=payload.activity_type,
        activity_code=payload.activity_code,
        response_text=payload.answer_text,
        score=payload.score,
        created_at=datetime.utcnow(),
    )
    db.add(log_entry)

    # Update engagement from recent logs
    _recompute_engagement_from_logs(student, db)

    # Re-run ML predictor to update probability + cluster
    probability, cluster_id = predictor.predict(student)
    student.cluster_id = cluster_id
    _compute_final_risk_and_stage(student, probability)

    db.commit()
    db.refresh(student)

    return {
        "ok": True,
        "dropout_probability": student.dropout_probability,
        "final_risk": student.final_risk.value,
        "stage": student.stage,
        "cluster_id": student.cluster_id,
    }