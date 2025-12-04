"""
SCHEMAS.PY - Pydantic Schemas for API
=====================================
These schemas define:
1. What data the API accepts (request validation)
2. What data the API returns (response formatting)

Pydantic automatically validates data types and raises errors if invalid.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS (Must match database enums)
# =============================================================================

class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class UserRole(str, Enum):
    ADMIN = "admin"
    COUNSELOR = "counselor"
    STUDENT = "student"


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserCreate(BaseModel):
    """
    Schema for creating a new user (registration).
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.STUDENT
    full_name: str = Field(..., min_length=2, max_length=100)
    specialization: Optional[str] = None  # e.g. "academic", "mental", "financial"


class UserLogin(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class UserResponse(BaseModel):
    """
    Schema for user data in responses.
    Note: Password is NOT included for security!
    """
    id: int
    username: str
    email: str
    role: UserRole
    full_name: str
    is_active: bool
    specialization: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response after login"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""
    username: Optional[str] = None


# =============================================================================
# STUDENT SCHEMAS
# =============================================================================

class StudentCreate(BaseModel):
    """
    Schema for adding a new student.
    """
    student_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=15)
    department: str = Field(..., max_length=100)
    semester: int = Field(..., ge=1, le=8)

    # Academic data
    attendance_percentage: float = Field(default=0.0, ge=0, le=100)
    cgpa: float = Field(default=0.0, ge=0, le=10)
    backlogs: int = Field(default=0, ge=0)

    # Financial data
    fees_pending: bool = False
    fees_amount_due: float = Field(default=0.0, ge=0)

    # Parent info (optional)
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[EmailStr] = None


class StudentUpdate(BaseModel):
    """
    Schema for updating student data.
    All fields optional - only update what you send.
    """
    attendance_percentage: Optional[float] = Field(None, ge=0, le=100)
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    backlogs: Optional[int] = Field(None, ge=0)
    fees_pending: Optional[bool] = None
    fees_amount_due: Optional[float] = Field(None, ge=0)
    quiz_score_avg: Optional[float] = Field(None, ge=0, le=100)
    bot_engagement_score: Optional[float] = Field(None, ge=0, le=100)
    counselling_sessions: Optional[int] = Field(None, ge=0)
    counsellor_notes: Optional[str] = None
    # Optional: allow manual override by counselor
    stage: Optional[int] = Field(None, ge=1, le=3)
    final_risk: Optional[RiskLevel] = None


class StudentResponse(BaseModel):
    """Schema for student data in API responses"""
    id: int
    student_id: str
    name: str
    email: str
    phone: Optional[str]
    department: str
    semester: int
    attendance_percentage: float
    cgpa: float
    backlogs: int
    fees_pending: bool
    fees_amount_due: float
    quiz_score_avg: float
    bot_engagement_score: float
    counselling_sessions: int
    baseline_risk: RiskLevel
    ml_risk_score: float
    final_risk: RiskLevel
    dropout_probability: float
    cluster_id: Optional[int]
    stage: int
    telegram_chat_id: Optional[str]
    created_at: Optional[datetime]
    last_risk_update: Optional[datetime]

    class Config:
        from_attributes = True


class StudentBrief(BaseModel):
    """Brief student info for lists"""
    student_id: str
    name: str
    department: str
    final_risk: RiskLevel
    dropout_probability: float
    stage: int
    cluster_id: Optional[int] = None

    class Config:
        from_attributes = True


# =============================================================================
# RISK ANALYSIS SCHEMAS
# =============================================================================

class RiskAnalysis(BaseModel):
    """
    Detailed risk analysis for a student.
    Returned when analyzing a specific student.
    """
    student_id: str
    name: str
    baseline_risk: RiskLevel
    ml_risk_score: float
    final_risk: RiskLevel
    dropout_probability: float
    risk_factors: List[str]
    recommendations: List[str]
    cluster_id: Optional[int]
    cluster_name: str
    cluster_description: str
    stage: int


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================

class DashboardStats(BaseModel):
    """Overall statistics for dashboard"""
    total_students: int
    green_count: int
    yellow_count: int
    red_count: int
    avg_attendance: float
    avg_cgpa: float
    students_with_backlogs: int
    fees_pending_count: int


class DepartmentRisk(BaseModel):
    """Risk distribution for a department"""
    department: str
    green: int
    yellow: int
    red: int
    total: int


class AtRiskStudent(BaseModel):
    """Brief info about at-risk student for alerts"""
    student_id: str
    name: str
    department: str
    risk: RiskLevel
    probability: float
    main_issue: str
    stage: int

    class Config:
        from_attributes = True


# =============================================================================
# BOT SCHEMAS
# =============================================================================

class BotRegisterRequest(BaseModel):
    """
    Used by Telegram bot to link a chat to a student.
    `student_id` is the college roll/registration id (string),
    `chat_id` is the Telegram chat id (string).
    """
    student_id: str
    chat_id: str
    username: Optional[str] = None


class ActivityQuestion(BaseModel):
    """
    One question/activity that the bot will ask the student.
    """
    activity_type: str          # e.g. "mood", "study_hours"
    activity_code: str          # e.g. "MOOD_1_5"
    question: str               # text to send to Telegram
    min_value: Optional[int] = None
    max_value: Optional[int] = None


class DailyCheckupResponse(BaseModel):
    """
    Response for /bot/daily_checkup/{student_id}:
    list of today's questions for a student.
    """
    student_id: str
    stage: int
    cluster_id: Optional[int]
    activities: List[ActivityQuestion]


from typing import List  # already imported above, just ensure it exists

class ClusterOverview(BaseModel):
    cluster_id: int
    name: str
    description: str
    typical_issues: List[str]
    recommended_focus: str
    total_students: int
    green: int
    yellow: int
    red: int
    stage1: int
    stage2: int
    stage3: int


class ClusterBroadcastRequest(BaseModel):
    message_title: str
    message_body: str
    min_stage: int = 1
    max_stage: int = 3


class CounselorSummary(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    specialization: Optional[str] = None
    total_students: int
    high_risk: int
    medium_risk: int
    low_risk: int
    unresolved_cases: int          # medium + high
    resolved_cases: int            # low
    total_counselling_sessions: int
    avg_dropout_probability: float

    
class BotActivityCreate(BaseModel):
    """
    One answer from the student to a specific activity question.
    """
    student_id: str
    chat_id: str
    activity_type: str
    activity_code: str
    answer_text: str
    score: Optional[float] = None