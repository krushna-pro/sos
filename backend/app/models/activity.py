from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class StudentActivity(Base):
    __tablename__ = "student_activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # e.g. "mood", "study_hours", "stress", "motivation", "quiz_score"
    activity_type = Column(String, nullable=False)

    # raw answer from student (text)
    answer_text = Column(String, nullable=True)

    # numeric score extracted from answer (0–10, 1–5 etc.), optional
    score = Column(Float, nullable=True)

    # optional: which activity template was used
    activity_code = Column(String, nullable=True)  # e.g. "MOOD_1_5"