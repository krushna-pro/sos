"""
RULES.PY - Rule-Based Risk Assessment (Stage 1)
===============================================
Simple threshold-based rules for initial risk classification.
This runs BEFORE ML prediction and provides instant results.

Why Rules First?
1. Works without training data
2. Easy to understand and explain
3. Based on domain expertise
4. Provides baseline for ML comparison
"""

from ..models.student import RiskLevel


def calculate_baseline_risk(student) -> tuple:
    """
    Calculate risk level using simple rules/thresholds.
    
    Args:
        student: Student model object with all attributes
    
    Returns:
        tuple: (RiskLevel, list of risk factors)
    
    Example:
        risk, factors = calculate_baseline_risk(student)
        # risk = RiskLevel.YELLOW
        # factors = ["Low attendance: 65%", "Has backlogs: 2 subjects"]
    """
    risk_factors = []
    risk_score = 0  # Accumulate points, higher = more risk
        # ------- SAFE DEFAULTS FOR NONE VALUES -------
    # Use neutral defaults if some fields are missing (None)
    
    if student.attendance_percentage is None:
        student.attendance_percentage = 0.0
    if student.cgpa is None:
        student.cgpa = 0.0
    if student.backlogs is None:
        student.backlogs = 0
    if student.fees_pending is None:
        student.fees_pending = False
    if student.fees_amount_due is None:
        student.fees_amount_due = 0.0
    if student.bot_engagement_score is None:
        student.bot_engagement_score = 50.0   # neutral engagement
    if student.quiz_score_avg is None:
        student.quiz_score_avg = 50.0         # neutral quiz score
    
    # =========================================================================
    # ATTENDANCE RULES
    # Most colleges require 75% minimum attendance
    # =========================================================================
    
    if student.attendance_percentage < 50:
        risk_score += 4  # Critical
        risk_factors.append(
            f"🚨 Critical attendance: {student.attendance_percentage:.1f}% (Need >75%)"
        )
    elif student.attendance_percentage < 65:
        risk_score += 3  # Serious
        risk_factors.append(
            f"⚠️ Very low attendance: {student.attendance_percentage:.1f}% (Need >75%)"
        )
    elif student.attendance_percentage < 75:
        risk_score += 2  # Concerning
        risk_factors.append(
            f"📉 Below minimum attendance: {student.attendance_percentage:.1f}% (Need >75%)"
        )
    elif student.attendance_percentage < 85:
        risk_score += 1  # Mild concern
        risk_factors.append(
            f"📊 Attendance could improve: {student.attendance_percentage:.1f}%"
        )
    
    # =========================================================================
    # CGPA RULES
    # Below 5.0 is typically failing, 6.0-7.0 is average
    # =========================================================================
    
    if student.cgpa < 4.0:
        risk_score += 4  # Critical - likely to fail
        risk_factors.append(
            f"🚨 Critical CGPA: {student.cgpa:.2f} (Failing)"
        )
    elif student.cgpa < 5.0:
        risk_score += 3  # At risk of failing
        risk_factors.append(
            f"⚠️ Very low CGPA: {student.cgpa:.2f} (At risk)"
        )
    elif student.cgpa < 6.0:
        risk_score += 2  # Below average
        risk_factors.append(
            f"📉 Below average CGPA: {student.cgpa:.2f}"
        )
    elif student.cgpa < 7.0:
        risk_score += 1  # Could improve
        risk_factors.append(
            f"📊 CGPA needs improvement: {student.cgpa:.2f}"
        )
    
    # =========================================================================
    # BACKLOG RULES
    # Backlogs accumulate stress and delay graduation
    # =========================================================================
    
    if student.backlogs >= 5:
        risk_score += 4  # Many backlogs
        risk_factors.append(
            f"🚨 High backlogs: {student.backlogs} subjects pending"
        )
    elif student.backlogs >= 3:
        risk_score += 3  # Several backlogs
        risk_factors.append(
            f"⚠️ Multiple backlogs: {student.backlogs} subjects pending"
        )
    elif student.backlogs >= 1:
        risk_score += 2  # Some backlogs
        risk_factors.append(
            f"📉 Has backlogs: {student.backlogs} subject(s) pending"
        )
    
    # =========================================================================
    # FINANCIAL RULES
    # Fee issues are major dropout predictor
    # =========================================================================
    
    if student.fees_pending:
        if student.fees_amount_due > 100000:  # > 1 Lakh
            risk_score += 4
            risk_factors.append(
                f"🚨 Major fee pending: ₹{student.fees_amount_due:,.0f}"
            )
        elif student.fees_amount_due > 50000:  # > 50K
            risk_score += 3
            risk_factors.append(
                f"⚠️ Significant fee pending: ₹{student.fees_amount_due:,.0f}"
            )
        elif student.fees_amount_due > 20000:  # > 20K
            risk_score += 2
            risk_factors.append(
                f"📉 Fee pending: ₹{student.fees_amount_due:,.0f}"
            )
        else:
            risk_score += 1
            risk_factors.append(
                f"📊 Minor fee pending: ₹{student.fees_amount_due:,.0f}"
            )
    
    # =========================================================================
    # ENGAGEMENT RULES
    # Low engagement often precedes dropout
    # =========================================================================
    
    if student.bot_engagement_score < 20:
        risk_score += 2
        risk_factors.append(
            f"📉 Very low engagement with support system"
        )
    elif student.bot_engagement_score < 40:
        risk_score += 1
        risk_factors.append(
            f"📊 Low engagement with support system"
        )
    
    if student.quiz_score_avg < 30:
        risk_score += 1
        risk_factors.append(
            f"📊 Poor quiz performance: {student.quiz_score_avg:.1f}%"
        )
    
    # =========================================================================
    # DETERMINE FINAL RISK LEVEL
    # =========================================================================
    
    if risk_score >= 8:
        return RiskLevel.RED, risk_factors
    elif risk_score >= 4:
        return RiskLevel.YELLOW, risk_factors
    else:
        if not risk_factors:
            risk_factors.append("✅ No significant risk factors identified")
        return RiskLevel.GREEN, risk_factors


def get_risk_summary(risk_level: RiskLevel) -> dict:
    """
    Get summary information about a risk level.
    
    Returns:
        dict with color, label, description, urgency
    """
    summaries = {
        RiskLevel.GREEN: {
            "color": "#22c55e",
            "label": "Low Risk",
            "description": "Student is performing well",
            "urgency": "Monitor periodically",
            "icon": "✅"
        },
        RiskLevel.YELLOW: {
            "color": "#eab308",
            "label": "Medium Risk",
            "description": "Student needs attention",
            "urgency": "Schedule counselling within 1 week",
            "icon": "⚠️"
        },
        RiskLevel.RED: {
            "color": "#ef4444",
            "label": "High Risk",
            "description": "Immediate intervention required",
            "urgency": "Contact today, involve parents",
            "icon": "🚨"
        }
    }
    return summaries.get(risk_level, summaries[RiskLevel.GREEN])