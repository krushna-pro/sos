"""
USER.PY - User Database Model
=============================
Defines the 'users' table for storing admin, counselor, and student accounts.
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum
from ..database import Base


class UserRole(str, enum.Enum):
    """
    Enum defining possible user roles.
    
    Using Enum ensures only valid roles can be assigned.
    str inheritance allows easy JSON serialization.
    """
    ADMIN = "admin"           # Full access: manage everything
    COUNSELOR = "counselor"   # Can view students, add notes
    STUDENT = "student"       # Limited access: own data only


class User(Base):
    """
    User model representing the 'users' table.
    
    Table Structure:
    ----------------
    | id | username | email | hashed_password | role | full_name | is_active |
    
    Example row:
    | 1 | admin | admin@college.edu | $2b$12... | admin | Admin User | True |
    """
    
    # Name of the table in database
    __tablename__ = "users"
    
    # ==========================================================================
    # COLUMNS
    # ==========================================================================
    
    # Primary Key: Unique identifier for each user
    # auto-increments: 1, 2, 3, ...
    id = Column(Integer, primary_key=True, index=True)
    
    # Username: Used for login
    # unique=True: No two users can have same username
    # index=True: Creates database index for faster searches
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Email: Contact email
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Password: Stored as encrypted hash (never plain text!)
    # Length 255 to accommodate hash length
    hashed_password = Column(String(255), nullable=False)
    
    # Role: What type of user (admin/counselor/student)
    # default=UserRole.STUDENT: New users are students by default
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    # Specialization: Area of counseling expertise (for counselors)
    specialization = Column(String, nullable=True)  # e.g. "academic", "mental", "financial"
    # Full Name: Display name
    full_name = Column(String(100), nullable=False)
    
    # Is Active: Can this user login?
    # Useful for disabling accounts without deleting
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"