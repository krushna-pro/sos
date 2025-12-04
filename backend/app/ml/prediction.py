"""
PREDICTION.PY - Machine Learning Prediction (Stage 2)
====================================================
Uses ML models to predict dropout probability.

Models Used:
1. K-Means Clustering - Groups similar students
2. Logistic Regression - Predicts dropout probability

How It Works:
1. Extract features from student data
2. Scale features (normalize)
3. Predict cluster (which group)
4. Predict probability (how likely to dropout)
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List
import warnings

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings('ignore')


class DropoutPredictor:
    """
    Main class for dropout prediction.
    
    Usage:
        predictor = DropoutPredictor()
        probability, cluster = predictor.predict(student)
    """
    
    def __init__(self):
        """Initialize the predictor with default models."""
        self.scaler = StandardScaler()
        self.cluster_model = None
        self.prediction_model = None
        self.is_initialized = False
        
        # Feature names for reference
        self.feature_names = [
            'attendance_percentage',
            'cgpa',
            'backlogs',
            'fees_pending',
            'fees_amount_normalized',
            'quiz_score_avg',
            'bot_engagement_score',
            'counselling_sessions',
            'semester'
        ]
        
        # Initialize with synthetic data
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialize models with synthetic data.
        
        Since we don't have historical dropout data, we create
        synthetic training data based on domain knowledge.
        """
        np.random.seed(42)  # For reproducibility
        n_samples = 500
        
        # Generate synthetic student data
        # Each row: [attendance, cgpa, backlogs, fees_pending, fees_amount, 
        #            quiz_score, engagement, counselling, semester]
        
        X = np.zeros((n_samples, 9))
        
        # Generate varied student profiles
        for i in range(n_samples):
            profile_type = np.random.choice(['good', 'average', 'struggling', 'at_risk'], 
                                           p=[0.3, 0.35, 0.2, 0.15])
            
            if profile_type == 'good':
                X[i] = [
                    np.random.uniform(85, 100),  # High attendance
                    np.random.uniform(7, 10),    # Good CGPA
                    0,                            # No backlogs
                    0,                            # No fees pending
                    0,                            # No fee amount
                    np.random.uniform(70, 100),  # Good quiz scores
                    np.random.uniform(60, 100),  # Good engagement
                    np.random.randint(0, 3),     # Some counselling
                    np.random.randint(1, 9)      # Any semester
                ]
            elif profile_type == 'average':
                X[i] = [
                    np.random.uniform(70, 85),
                    np.random.uniform(5.5, 7.5),
                    np.random.randint(0, 2),
                    np.random.choice([0, 1], p=[0.8, 0.2]),
                    np.random.uniform(0, 0.3),
                    np.random.uniform(50, 75),
                    np.random.uniform(40, 70),
                    np.random.randint(0, 2),
                    np.random.randint(1, 9)
                ]
            elif profile_type == 'struggling':
                X[i] = [
                    np.random.uniform(55, 75),
                    np.random.uniform(4, 6),
                    np.random.randint(1, 4),
                    np.random.choice([0, 1], p=[0.5, 0.5]),
                    np.random.uniform(0.2, 0.5),
                    np.random.uniform(30, 55),
                    np.random.uniform(25, 50),
                    np.random.randint(1, 4),
                    np.random.randint(1, 9)
                ]
            else:  # at_risk
                X[i] = [
                    np.random.uniform(30, 60),
                    np.random.uniform(2, 5),
                    np.random.randint(3, 8),
                    np.random.choice([0, 1], p=[0.2, 0.8]),
                    np.random.uniform(0.4, 1.0),
                    np.random.uniform(10, 40),
                    np.random.uniform(5, 30),
                    np.random.randint(0, 2),
                    np.random.randint(1, 9)
                ]
        
        # Generate labels based on risk rules
        y = np.zeros(n_samples)
        for i in range(n_samples):
            risk_score = 0
            if X[i, 0] < 60: risk_score += 3      # Low attendance
            if X[i, 1] < 5: risk_score += 3       # Low CGPA
            if X[i, 2] >= 3: risk_score += 2      # Many backlogs
            if X[i, 3] == 1: risk_score += 2      # Fees pending
            if X[i, 5] < 40: risk_score += 1      # Low quiz score
            if X[i, 6] < 30: risk_score += 1      # Low engagement
            
            # Probability of dropout based on risk score
            if risk_score >= 8:
                y[i] = np.random.choice([0, 1], p=[0.2, 0.8])
            elif risk_score >= 5:
                y[i] = np.random.choice([0, 1], p=[0.5, 0.5])
            elif risk_score >= 3:
                y[i] = np.random.choice([0, 1], p=[0.8, 0.2])
            else:
                y[i] = np.random.choice([0, 1], p=[0.95, 0.05])
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X)
        
        # Train clustering model (4 clusters)
        self.cluster_model = KMeans(n_clusters=4, random_state=42, n_init=10)
        self.cluster_model.fit(X_scaled)
        
        # Train prediction model
        self.prediction_model = LogisticRegression(random_state=42, max_iter=1000)
        self.prediction_model.fit(X_scaled, y)
        
        self.is_initialized = True
    
    def extract_features(self, student) -> np.ndarray:
        """
        Extract ML features from a student object.
        
        Args:
            student: Student model object
        
        Returns:
            numpy array of shape (1, 9) with features
        """
        features = np.array([
            student.attendance_percentage,
            student.cgpa,
            student.backlogs,
            1 if student.fees_pending else 0,
            student.fees_amount_due / 100000,  # Normalize to 0-1 range
            student.quiz_score_avg,
            student.bot_engagement_score,
            student.counselling_sessions,
            student.semester
        ]).reshape(1, -1)
        
        return features
    
    def predict(self, student) -> Tuple[float, int]:
        """
        Predict dropout probability and cluster for a student.
        
        Args:
            student: Student model object
        
        Returns:
            tuple: (dropout_probability, cluster_id)
                - probability: 0.0 to 1.0
                - cluster_id: 0, 1, 2, or 3
        """
        if not self.is_initialized:
            self._initialize_models()
        
        # Extract and scale features
        features = self.extract_features(student)
        features_scaled = self.scaler.transform(features)
        
        # Predict probability
        probability = self.prediction_model.predict_proba(features_scaled)[0][1]
        
        # Predict cluster
        cluster = self.cluster_model.predict(features_scaled)[0]
        
        return float(probability), int(cluster)
    
    def get_cluster_info(self, cluster_id: int) -> dict:
        """
        Get descriptive information about a cluster.
        
        Args:
            cluster_id: 0, 1, 2, or 3
        
        Returns:
            dict with cluster name, description, issues, intervention
        """
        cluster_profiles = {
            0: {
                "name": "High Performers",
                "description": "Students with strong academics and good engagement",
                "typical_issues": [
                    "May face burnout from overwork",
                    "Peer pressure to maintain performance",
                    "May neglect extracurriculars"
                ],
                "intervention": "Maintain motivation, offer leadership opportunities, ensure work-life balance"
            },
            1: {
                "name": "Academic Strugglers",
                "description": "Students with low CGPA and multiple backlogs",
                "typical_issues": [
                    "Learning difficulties or gaps",
                    "Wrong course/stream choice",
                    "Lack of study skills",
                    "Possible learning disabilities"
                ],
                "intervention": "Academic mentoring, remedial classes, peer tutoring, study skill workshops"
            },
            2: {
                "name": "Financially Stressed",
                "description": "Students with pending fees and financial constraints",
                "typical_issues": [
                    "Family financial problems",
                    "May be working part-time",
                    "Stress affecting studies",
                    "May skip classes for work"
                ],
                "intervention": "Scholarship information, fee installment plans, work-study programs, financial counselling"
            },
            3: {
                "name": "Disengaged Students",
                "description": "Low attendance, low engagement, disconnected from college",
                "typical_issues": [
                    "Lack of interest in course",
                    "Personal or family problems",
                    "Mental health issues",
                    "Peer group influence",
                    "Substance abuse (rare)"
                ],
                "intervention": "One-on-one counselling, interest assessment, parent meeting, mental health support"
            }
        }
        
        return cluster_profiles.get(cluster_id, cluster_profiles[3])
    
    def get_feature_importance(self) -> List[dict]:
        """
        Get feature importance from the model.
        
        Returns:
            List of dicts with feature name and importance score
        """
        if not self.is_initialized:
            return []
        
        # Get coefficients from logistic regression
        coefficients = self.prediction_model.coef_[0]
        
        # Create list of (feature, importance)
        importance_list = []
        for name, coef in zip(self.feature_names, coefficients):
            importance_list.append({
                "feature": name,
                "importance": abs(float(coef)),
                "direction": "increases_risk" if coef > 0 else "decreases_risk"
            })
        
        # Sort by importance
        importance_list.sort(key=lambda x: x["importance"], reverse=True)
        
        return importance_list


# =============================================================================
# GLOBAL PREDICTOR INSTANCE
# =============================================================================
# Create a single instance to be used throughout the application

predictor = DropoutPredictor()