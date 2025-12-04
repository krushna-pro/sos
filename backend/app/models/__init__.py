"""
MODELS PACKAGE
==============
This file imports all models so they can be easily accessed.

Usage:
    from app.models import User, Student, RiskLevel, UserRole
"""

from .user import User, UserRole
from .student import Student, RiskLevel

# This list tells Python what to export when someone does:
# from app.models import *
__all__ = ["User", "UserRole", "Student", "RiskLevel"]