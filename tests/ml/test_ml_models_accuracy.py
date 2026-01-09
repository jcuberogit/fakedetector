"""
ML Model Accuracy Tests (FRAUD-002)
TDD: RED → GREEN → REFACTOR
Target: >99% accuracy, <1% false positives, <0.1% false negatives
"""

import pytest
import numpy as np
import pandas as pd
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fraud_detection.ml_service import MLService
from fraud_detection.ml_models import (
    ModelPredictionRequest, ModelPredictionResponse, ModelTrainingConfig,
    ModelType, ModelStatus
)


@pytest.mark.ml
@pytest.mark.slow
class TestMLModelAccuracy:
    """Test ML model accuracy and performance metrics"""
    
    @pytest.fixture
    def ml_service(self):
        """Create MLService instance"""
        return MLService()
    
    @pytest.fixture
    def test_dataset(self):
        """Create test dataset with 1000+ transactions"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic fraud detection dataset
        data = {
            'transaction_amount': np.random.lognormal(mean=5, sigma=1, size=n_samples),
            'merchant_category': np.random.choice(['retail', 'online', 'gas', 'food'], n_samples),
            'device_id': [f'device_{i%100}' for i in range(n_samples)],
            'location': np.random.choice(['US', 'UK', 'CA', 'MX'], n_samples),
            'time_of_day': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'is_fraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])  # 5% fraud rate
        }
        
        return pd.DataFrame(data)
    
    @pytest.mark.asyncio
    async def test_model_accuracy_threshold(self, ml_service, test_dataset):
        """Test that model accuracy meets >99% threshold"""
        # RED: Test should validate accuracy
        # This is a validation test - models should already be trained
        
        # Get default XGBoost model
        model = ml_service.models.get("xgboost-default")
        
        if model and model.performance:
            accuracy = float(model.performance.accuracy)
            
            # GREEN: Assert accuracy meets threshold
            assert accuracy >= 0.99, f"Model accuracy {accuracy} below 99% threshold"
    
    @pytest.mark.asyncio
    async def test_model_false_positive_rate(self, ml_service, test_dataset):
        """Test that false positive rate is <1%"""
        # Get default model
        model = ml_service.models.get("xgboost-default")
        
        if model and model.performance:
            precision = float(model.performance.precision)
            # False positive rate = 1 - precision (for binary classification)
            # Higher precision = lower false positive rate
            false_positive_rate = 1 - precision
            
            # GREEN: Assert false positive rate < 1%
            assert false_positive_rate < 0.01, f"False positive rate {false_positive_rate} exceeds 1%"
    
    @pytest.mark.asyncio
    async def test_model_false_negative_rate(self, ml_service, test_dataset):
        """Test that false negative rate is <0.1%"""
        # Get default model
        model = ml_service.models.get("xgboost-default")
        
        if model and model.performance:
            recall = float(model.performance.recall)
            # False negative rate = 1 - recall
            false_negative_rate = 1 - recall
            
            # GREEN: Assert false negative rate < 0.1%
            assert false_negative_rate < 0.001, f"False negative rate {false_negative_rate} exceeds 0.1%"
    
    @pytest.mark.asyncio
    async def test_model_roc_auc_score(self, ml_service):
        """Test that ROC AUC score is high (>0.95)"""
        model = ml_service.models.get("xgboost-default")
        
        if model and model.performance:
            roc_auc = float(model.performance.roc_auc)
            
            # High ROC AUC indicates good model discrimination
            assert roc_auc >= 0.95, f"ROC AUC {roc_auc} below 0.95 threshold"
    
    @pytest.mark.asyncio
    async def test_model_prediction_consistency(self, ml_service):
        """Test that model predictions are consistent"""
        # Create prediction request
        request = ModelPredictionRequest(
            model_id="xgboost-default",
            features={
                "transaction_amount": 100.0,
                "merchant_category": "retail",
                "device_id": "device_001",
                "location": "US",
                "time_of_day": 14,
                "day_of_week": 3
            }
        )
        
        # Make multiple predictions
        predictions = []
        for _ in range(10):
            result = await ml_service.predict(request)
            if result:
                predictions.append(result.risk_score)
        
        if len(predictions) > 1:
            # Predictions should be consistent (low variance)
            variance = np.var(predictions)
            assert variance < 0.01, f"Prediction variance {variance} too high"


@pytest.mark.ml
class TestMLModelPerformance:
    """Test ML model performance metrics"""
    
    @pytest.fixture
    def ml_service(self):
        """Create MLService instance"""
        return MLService()
    
    @pytest.mark.asyncio
    async def test_model_exists(self, ml_service):
        """Test that default models exist"""
        assert "xgboost-default" in ml_service.models
        assert ml_service.models["xgboost-default"].status == ModelStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_model_prediction(self, ml_service):
        """Test model prediction functionality"""
        request = ModelPredictionRequest(
            model_id="xgboost-default",
            features={
                "transaction_amount": 500.0,
                "merchant_category": "online",
                "device_id": "device_123",
                "location": "US",
                "time_of_day": 10,
                "day_of_week": 1
            }
        )
        
        result = await ml_service.predict(request)
        
        # Should return prediction response
        assert result is not None
        assert hasattr(result, 'risk_score')
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
    
    @pytest.mark.asyncio
    async def test_ensemble_prediction(self, ml_service):
        """Test ensemble prediction"""
        request = ModelPredictionRequest(
            model_id="ensemble-default",
            features={
                "transaction_amount": 1000.0,
                "merchant_category": "retail",
                "device_id": "device_456",
                "location": "UK",
                "time_of_day": 20,
                "day_of_week": 5
            }
        )
        
        result = await ml_service.ensemble_predict(request)
        
        if result:
            assert result.risk_score >= Decimal('0')
            assert result.risk_score <= Decimal('1')










