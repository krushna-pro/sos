# backend/app/models/bot.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from ..database import Base


class StudentBotLink(Base):
    """
    Links a Telegram chat to a student_id.
    Used when student does /register <student_id>.
    """
    __tablename__ = "student_bot_links"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.student_id"), index=True)
    chat_id = Column(String, index=True)      # Telegram chat id as string
    username = Column(String, nullable=True)  # Telegram username
    created_at = Column(DateTime, default=datetime.utcnow)


class BotActivityLog(Base):
    """
    Stores each activity/response from the student bot.
    """
    __tablename__ = "bot_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.student_id"), index=True)
    chat_id = Column(String, index=True)
    activity_type = Column(String)        # e.g., "mood", "study_hours"
    activity_code = Column(String)        # e.g., "MOOD_1_5", "STUDY_HOURS_0_10"
    response_text = Column(String)        # raw response from student
    score = Column(Float, nullable=True)  # optional numeric score
    created_at = Column(DateTime, default=datetime.utcnow)