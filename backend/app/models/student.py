# backend/app/models/student.py

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Enum as SQLEnum,
)

from ..database import Base


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)

    # Academic & profile
    department = Column(String, nullable=True)
    semester = Column(Integer, default=0)

    # Academic indicators
    attendance_percentage = Column(Float, default=0.0)  # 0–100
    cgpa = Column(Float, default=0.0)                   # 0–10
    backlogs = Column(Integer, default=0)

    # Fees / financial indicators
    fees_pending = Column(Boolean, default=False)
    fees_amount_due = Column(Float, default=0.0)

    # Parent info (to match StudentCreate)
    parent_name = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    parent_email = Column(String, nullable=True)

    # Behavioural / engagement indicators
    quiz_score_avg = Column(Float, default=0.0)
    bot_engagement_score = Column(Float, default=0.0)
    counselling_sessions = Column(Integer, default=0)

    # Risk-related fields
    baseline_risk = Column(
        SQLEnum(RiskLevel),
        default=RiskLevel.GREEN,
        nullable=False,
    )
    ml_risk_score = Column(Float, default=0.0)         # 0–100
    final_risk = Column(
        SQLEnum(RiskLevel),
        default=RiskLevel.GREEN,
        nullable=False,
    )
    dropout_probability = Column(Float, default=0.0)   # 0–1

    # ML clustering info
    cluster_id = Column(Integer, nullable=True)

    # Intervention pipeline
    # 1 = normal, 2 = at-risk with automated support, 3 = high-risk
    stage = Column(Integer, default=1, nullable=False)

    # Telegram bot link
    telegram_chat_id = Column(String, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_risk_update = Column(DateTime, default=datetime.utcnow)