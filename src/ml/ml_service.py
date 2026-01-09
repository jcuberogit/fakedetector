"""
ML Service - XGBoost Model Integration
Loads trained model and provides prediction interface
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict


class MLService:
    """Machine Learning service for scam detection."""
    
    def __init__(self):
        self.model = None
        self.confidence = 0.0
        self.load_model()
    
    def load_model(self):
        """Load trained XGBoost model."""
        model_path = Path(__file__).parent.parent.parent / 'models' / 'scam_detector_v1.pkl'
        
        if model_path.exists():
            self.model = joblib.load(model_path)
            print(f"✅ ML model loaded from {model_path}")
        else:
            print(f"⚠️  ML model not found at {model_path}")
            print("   Run: python src/ml/train_model.py")
    
    def predict_risk(self, features: Dict) -> float:
        """
        Predict scam risk from anonymized features.
        Returns risk score 0-1 (multiply by 100 for percentage).
        """
        if not self.model:
            # Fallback to rule-based scoring
            return self._fallback_scoring(features)
        
        # Convert features dict to vector
        feature_vector = self._features_to_vector(features)
        
        # Get prediction probability
        risk_proba = self.model.predict_proba([feature_vector])[0][1]
        
        # Store confidence
        self.confidence = max(self.model.predict_proba([feature_vector])[0])
        
        return risk_proba
    
    def get_confidence(self) -> float:
        """Get confidence of last prediction."""
        return self.confidence
    
    def _features_to_vector(self, features: Dict) -> np.ndarray:
        """Convert features dict to numpy array in correct order."""
        return np.array([
            features.get('message_length', 0),
            features.get('word_count', 0),
            features.get('sentence_count', 1),
            features.get('avg_word_length', 5.0),
            features.get('urgency_keywords_count', 0),
            features.get('money_keywords_count', 0),
            features.get('credential_keywords_count', 0),
            features.get('link_count', 0),
            features.get('has_shortened_url', 0),
            features.get('file_attachment', 0),
            features.get('file_extension_risk', 0.0),
            features.get('exclamation_count', 0),
            features.get('question_count', 0),
            features.get('caps_ratio', 0.0),
            features.get('number_count', 0),
            features.get('currency_symbol_count', 0),
            features.get('sender_account_age_days', 365),
            features.get('connection_degree', 3),
            features.get('previous_interactions', 0),
            features.get('platform_id', 0),
            features.get('context_type_id', 0),
            features.get('requests_download', 0),
            features.get('requests_payment', 0),
            features.get('requests_credentials', 0),
            features.get('has_urgency', 0)
        ])
    
    def _fallback_scoring(self, features: Dict) -> float:
        """Fallback rule-based scoring when model not available."""
        risk = 0.0
        
        # High-risk indicators
        if features.get('file_extension_risk', 0) > 0.8:
            risk += 0.3
        if features.get('requests_credentials', 0):
            risk += 0.25
        if features.get('requests_payment', 0):
            risk += 0.2
        if features.get('sender_account_age_days', 365) < 7:
            risk += 0.2
        if features.get('urgency_keywords_count', 0) > 3:
            risk += 0.15
        
        return min(risk, 1.0)
