"""
RECOMMENDATIONS.PY - AI-Powered Recommendations
===============================================
Generates personalized intervention recommendations
based on student's risk factors and cluster.
"""

from typing import List
from ..models.student import RiskLevel


def generate_recommendations(
    student, 
    risk_factors: List[str], 
    cluster_info: dict
) -> List[str]:
    """
    Generate personalized recommendations for a student.
    
    Args:
        student: Student model object
        risk_factors: List of identified risk factors
        cluster_info: Dictionary with cluster details
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # =========================================================================
    # ATTENDANCE-BASED RECOMMENDATIONS
    # =========================================================================
    
    if student.attendance_percentage < 50:
        recommendations.extend([
            "🚨 URGENT: Schedule immediate meeting with student",
            "📱 Set up daily attendance SMS alerts to parent",
            "👥 Assign a peer buddy to accompany student to classes",
            "📝 Investigate root cause (health, transport, family issues)",
            "📞 Parent phone call within 24 hours"
        ])
    elif student.attendance_percentage < 65:
        recommendations.extend([
            "⚠️ Schedule parent-teacher meeting within 3 days",
            "📊 Weekly attendance monitoring with class teacher",
            "💬 Counselling session to understand absence reasons",
            "📱 Enable attendance notification to student"
        ])
    elif student.attendance_percentage < 75:
        recommendations.extend([
            "📈 Weekly attendance check-ins",
            "🎯 Set attendance improvement target (80%)",
            "💡 Discuss importance of attendance with student"
        ])
    
    # =========================================================================
    # ACADEMIC RECOMMENDATIONS
    # =========================================================================
    
    if student.cgpa < 4.0:
        recommendations.extend([
            "🚨 Enroll in intensive remedial program",
            "👨‍🏫 Assign dedicated faculty mentor",
            "📚 Daily supervised study hours (2-3 hrs)",
            "🎯 Focus on clearing current subjects before backlogs"
        ])
    elif student.cgpa < 5.0:
        recommendations.extend([
            "📚 Mandatory remedial classes for weak subjects",
            "👥 Pair with high-performing peer tutor",
            "📝 Create personalized study timetable",
            "🎯 Set target: Clear all current subjects"
        ])
    elif student.cgpa < 6.0:
        recommendations.extend([
            "📊 Identify and focus on 2-3 weak subjects",
            "👨‍🏫 Connect with subject teachers for extra help",
            "📚 Recommend online resources and tutorials"
        ])
    
    # Backlog-specific recommendations
    if student.backlogs >= 5:
        recommendations.extend([
            "🚨 Create backlog clearance plan (prioritize by difficulty)",
            "📅 Register for upcoming supplementary exams",
            "👨‍🏫 Assign subject-specific mentors",
            "⚠️ Consider course load reduction if allowed"
        ])
    elif student.backlogs >= 3:
        recommendations.extend([
            "📝 Prioritize backlog subjects for next exam",
            "📚 Provide previous year question papers",
            "👥 Form study group with students having same backlogs"
        ])
    elif student.backlogs >= 1:
        recommendations.extend([
            f"📚 Focus on clearing {student.backlogs} backlog(s) in next attempt",
            "📅 Mark supplementary exam dates"
        ])
    
    # =========================================================================
    # FINANCIAL RECOMMENDATIONS
    # =========================================================================
    
    if student.fees_pending:
        if student.fees_amount_due > 100000:
            recommendations.extend([
                "💰 Urgent meeting with accounts department",
                "📋 Check eligibility for government scholarships",
                "🏦 Discuss education loan options",
                "📝 Apply for fee waiver/reduction (if eligible)",
                "💼 Connect with alumni assistance programs"
            ])
        elif student.fees_amount_due > 50000:
            recommendations.extend([
                "💰 Set up fee installment plan",
                "📋 Apply for merit/need-based scholarships",
                "📝 Check state government fee reimbursement schemes"
            ])
        else:
            recommendations.extend([
                "💰 Remind about fee payment deadline",
                "📋 Share scholarship/financial aid information"
            ])
    
    # =========================================================================
    # ENGAGEMENT RECOMMENDATIONS
    # =========================================================================
    
    if student.bot_engagement_score < 30:
        recommendations.extend([
            "🤖 Personalized bot outreach with interesting content",
            "🎮 Introduce gamified learning challenges",
            "🏆 Offer small rewards for engagement milestones",
            "📱 Send motivational messages and success stories"
        ])
    elif student.bot_engagement_score < 50:
        recommendations.extend([
            "🎯 Set daily engagement targets",
            "📱 Send reminders for pending activities",
            "🏆 Highlight leaderboard position to motivate"
        ])
    
    if student.quiz_score_avg < 40:
        recommendations.extend([
            "📝 Daily micro-quizzes on weak topics",
            "🎮 Quiz competitions with peers",
            "📊 Track quiz improvement weekly"
        ])
    
    # =========================================================================
    # COUNSELLING RECOMMENDATIONS
    # =========================================================================
    
    if student.counselling_sessions == 0:
        recommendations.append(
            "🗣️ Schedule first counselling session this week"
        )
    elif student.counselling_sessions < 3 and student.final_risk != RiskLevel.GREEN:
        recommendations.append(
            f"🗣️ Continue counselling (Session {student.counselling_sessions + 1} due)"
        )
    
    # =========================================================================
    # CLUSTER-BASED RECOMMENDATIONS
    # =========================================================================
    
    recommendations.append(f"\n📊 Student Profile: {cluster_info['name']}")
    recommendations.append(f"💡 Recommended Focus: {cluster_info['intervention']}")
    
    # =========================================================================
    # PRIORITY TAGGING
    # =========================================================================
    
    # Add priority if high risk
    if student.final_risk == RiskLevel.RED:
        recommendations.insert(0, "⏰ PRIORITY: HIGH - Action needed within 24 hours")
    elif student.final_risk == RiskLevel.YELLOW:
        recommendations.insert(0, "⏰ PRIORITY: MEDIUM - Action needed within 1 week")
    
    return recommendations


def get_intervention_stages(risk_level: RiskLevel) -> List[dict]:
    """
    Get intervention stages based on risk level.
    
    Returns list of stages with actions for counsellors.
    """
    if risk_level == RiskLevel.RED:
        return [
            {
                "stage": 1,
                "name": "Immediate Contact",
                "timeline": "Within 24 hours",
                "actions": [
                    "Call student",
                    "Call parent/guardian",
                    "Email class teacher",
                    "Document contact attempts"
                ]
            },
            {
                "stage": 2,
                "name": "Assessment Meeting",
                "timeline": "Within 48 hours",
                "actions": [
                    "Face-to-face meeting with student",
                    "Identify root causes",
                    "Assess mental health status",
                    "Create immediate action plan"
                ]
            },
            {
                "stage": 3,
                "name": "Parent Meeting",
                "timeline": "Within 1 week",
                "actions": [
                    "Schedule parent meeting",
                    "Discuss concerns and plan",
                    "Get parent commitment",
                    "Set up monitoring agreement"
                ]
            },
            {
                "stage": 4,
                "name": "Intensive Support",
                "timeline": "Ongoing - 1 month",
                "actions": [
                    "Weekly check-ins",
                    "Academic support activation",
                    "Financial aid processing",
                    "Progress monitoring"
                ]
            }
        ]
    elif risk_level == RiskLevel.YELLOW:
        return [
            {
                "stage": 1,
                "name": "Initial Outreach",
                "timeline": "Within 1 week",
                "actions": [
                    "Send personalized message",
                    "Schedule counselling session",
                    "Notify class teacher"
                ]
            },
            {
                "stage": 2,
                "name": "Counselling Session",
                "timeline": "Within 2 weeks",
                "actions": [
                    "Conduct assessment",
                    "Identify specific issues",
                    "Create improvement plan"
                ]
            },
            {
                "stage": 3,
                "name": "Monitoring",
                "timeline": "Ongoing - 2 weeks",
                "actions": [
                    "Bi-weekly check-ins",
                    "Track attendance/grades",
                    "Adjust plan if needed"
                ]
            }
        ]
    else:  # GREEN
        return [
            {
                "stage": 1,
                "name": "Periodic Check",
                "timeline": "Monthly",
                "actions": [
                    "Monitor dashboard metrics",
                    "Celebrate achievements",
                    "Maintain engagement"
                ]
            }
        ]