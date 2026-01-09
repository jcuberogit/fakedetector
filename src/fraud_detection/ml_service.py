#!/usr/bin/env python3
"""
ML Service for Fraud Detection
Python equivalent of C# MLService.cs
"""

import asyncio
import logging
import pickle
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb
import joblib

from .ml_models import (
    MLModel, ModelType, ModelStatus, EnsembleConfig, EnsembleMethod,
    ModelPredictionRequest, ModelPredictionResponse, ModelTrainingConfig,
    ModelTrainingResult, ModelMetrics, ModelVersion, ModelDriftResult,
    ModelFeedback, ModelPerformanceMonitor, ModelRetrainingJob,
    ConfusionMatrix, ModelPerformance
)

logger = logging.getLogger(__name__)


class MLService:
    """
    ML Service implementation for fraud detection using machine learning models
    
    Python equivalent of C# MLService with XGBoost, Neural Networks, and Ensemble support.
    """
    
    def __init__(self):
        self.models: Dict[str, MLModel] = {}
        self.ensembles: Dict[str, EnsembleConfig] = {}
        self.feedback: Dict[str, ModelFeedback] = {}
        self.versions: Dict[str, ModelVersion] = {}
        self.drift_results: Dict[str, ModelDriftResult] = {}
        self.training_jobs: Dict[str, str] = {}
        self.predictions: Dict[str, ModelPredictionResponse] = {}
        
        # Circuit breaker pattern
        self.circuit_breaker_open = False
        self.circuit_breaker_failure_count = 0
        self.circuit_breaker_last_failure = datetime.min
        
        # Model counters
        self.next_model_id = 1
        self.next_ensemble_id = 1
        self.next_feedback_id = 1
        self.next_version_id = 1
        self.next_prediction_id = 1
        
        # Initialize default models
        self._initialize_default_models()
        
        logger.info("MLService initialized with default models")
    
    def _initialize_default_models(self):
        """Initialize default XGBoost and Neural Network models"""
        
        # Create default XGBoost model
        xgboost_model = MLModel(
            id="xgboost-default",
            name="Default XGBoost Model",
            description="Default XGBoost model for fraud detection",
            type=ModelType.XGBOOST,
            status=ModelStatus.ACTIVE,
            version="1.0.0",
            model_path="./models/xgboost-default.pkl",
            hyperparameters={
                "max_depth": 6,
                "learning_rate": 0.1,
                "n_estimators": 100,
                "subsample": 0.8,
                "colsample_bytree": 0.8
            },
            features={
                "transaction_amount": "numeric",
                "merchant_category": "categorical",
                "device_id": "categorical",
                "location": "categorical",
                "time_of_day": "numeric",
                "day_of_week": "categorical"
            },
            performance=ModelPerformance(
                accuracy=Decimal('0.92'),
                precision=Decimal('0.89'),
                recall=Decimal('0.87'),
                f1_score=Decimal('0.88'),
                roc_auc=Decimal('0.91'),
                prc_auc=Decimal('0.86'),
                last_evaluated_at=datetime.utcnow() - timedelta(days=1),
                training_samples=50000,
                validation_samples=10000,
                test_samples=10000
            ),
            created_at=datetime.utcnow() - timedelta(days=30),
            last_updated_at=datetime.utcnow() - timedelta(days=1),
            last_trained_at=datetime.utcnow() - timedelta(days=7),
            created_by="system",
            source="default"
        )
        
        self.models[xgboost_model.id] = xgboost_model
        
        # Create default Neural Network model
        nn_model = MLModel(
            id="nn-default",
            name="Default Neural Network Model",
            description="Default neural network model for fraud detection",
            type=ModelType.NEURAL_NETWORK,
            status=ModelStatus.ACTIVE,
            version="1.0.0",
            model_path="./models/nn-default.pkl",
            hyperparameters={
                "layers": [64, 32, 16],
                "activation": "relu",
                "dropout_rate": 0.2,
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 100
            },
            features={
                "transaction_amount": "numeric",
                "merchant_category": "categorical",
                "device_id": "categorical",
                "location": "categorical",
                "time_of_day": "numeric",
                "day_of_week": "categorical"
            },
            performance=ModelPerformance(
                accuracy=Decimal('0.90'),
                precision=Decimal('0.88'),
                recall=Decimal('0.85'),
                f1_score=Decimal('0.86'),
                roc_auc=Decimal('0.89'),
                prc_auc=Decimal('0.84'),
                last_evaluated_at=datetime.utcnow() - timedelta(days=1),
                training_samples=50000,
                validation_samples=10000,
                test_samples=10000
            ),
            created_at=datetime.utcnow() - timedelta(days=30),
            last_updated_at=datetime.utcnow() - timedelta(days=1),
            last_trained_at=datetime.utcnow() - timedelta(days=7),
            created_by="system",
            source="default"
        )
        
        self.models[nn_model.id] = nn_model
        
        # Create default ensemble
        ensemble = EnsembleConfig(
            id="ensemble-default",
            name="Default Ensemble Model",
            model_ids=["xgboost-default", "nn-default"],
            method=EnsembleMethod.WEIGHTED_VOTING,
            model_weights={
                "xgboost-default": Decimal('0.6'),
                "nn-default": Decimal('0.4')
            },
            voting_threshold=Decimal('0.5'),
            enable_dynamic_weighting=True,
            created_at=datetime.utcnow() - timedelta(days=30),
            last_updated_at=datetime.utcnow() - timedelta(days=1)
        )
        
        self.ensembles[ensemble.id] = ensemble
    
    async def predict_async(self, request: ModelPredictionRequest) -> ModelPredictionResponse:
        """
        Make prediction using specified model
        
        Args:
            request: Prediction request
            
        Returns:
            ModelPredictionResponse: Prediction result
        """
        start_time = time.time()
        
        try:
            if self.circuit_breaker_open:
                return await self._predict_with_fallback_async(request)
            
            model = await self._get_model_async(request.model_id)
            if model is None:
                raise ValueError(f"Model {request.model_id} not found")
            
            return await self._predict_with_model_async(request, model)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in predict_async for model {request.model_id}: {e}")
            await self._handle_prediction_failure()
            return await self._predict_with_fallback_async(request)
    
    async def predict_with_ensemble_async(self, request: ModelPredictionRequest) -> ModelPredictionResponse:
        """
        Make prediction using ensemble of models
        
        Args:
            request: Prediction request
            
        Returns:
            ModelPredictionResponse: Ensemble prediction result
        """
        start_time = time.time()
        
        try:
            # Find ensemble containing the model
            ensemble = None
            for ens in self.ensembles.values():
                if request.model_id in ens.model_ids:
                    ensemble = ens
                    break
            
            if ensemble is None:
                raise ValueError(f"No ensemble found containing model {request.model_id}")
            
            # Get predictions from all models in ensemble
            model_predictions = []
            model_probabilities = []
            
            for model_id in ensemble.model_ids:
                model_request = ModelPredictionRequest(
                    model_id=model_id,
                    features=request.features,
                    transaction_id=request.transaction_id,
                    user_id=request.user_id,
                    return_probabilities=True,
                    return_feature_importance=False,
                    metadata=request.metadata
                )
                
                prediction = await self.predict_async(model_request)
                model_predictions.append(prediction.prediction)
                model_probabilities.append(float(prediction.probability))
            
            # Apply ensemble method
            if ensemble.method == EnsembleMethod.WEIGHTED_VOTING:
                final_prediction, final_probability = self._weighted_voting(
                    model_predictions, model_probabilities, ensemble.model_weights
                )
            elif ensemble.method == EnsembleMethod.VOTING:
                final_prediction, final_probability = self._simple_voting(
                    model_predictions, model_probabilities
                )
            else:
                # Default to weighted voting
                final_prediction, final_probability = self._weighted_voting(
                    model_predictions, model_probabilities, ensemble.model_weights
                )
            
            processing_time = (time.time() - start_time) * 1000
            
            prediction_id = f"pred_{self.next_prediction_id}_{int(time.time())}"
            self.next_prediction_id += 1
            
            response = ModelPredictionResponse(
                prediction_id=prediction_id,
                model_id=request.model_id,
                prediction=final_prediction,
                probability=Decimal(str(final_probability)),
                confidence=Decimal(str(final_probability)),
                processing_time_ms=processing_time,
                timestamp=datetime.utcnow(),
                metadata={
                    "ensemble_method": ensemble.method.value,
                    "model_count": len(ensemble.model_ids),
                    "individual_predictions": model_predictions,
                    "individual_probabilities": model_probabilities
                }
            )
            
            self.predictions[prediction_id] = response
            
            logger.info(f"Ensemble prediction completed: {final_prediction} "
                       f"(Probability: {final_probability:.3f}, Time: {processing_time:.1f}ms)")
            
            return response
            
        except (ValueError) as e:
            logger.error(f"Error in ensemble prediction: {e}")
            raise
    
    async def train_model_async(self, config: ModelTrainingConfig) -> ModelTrainingResult:
        """
        Train a new model
        
        Args:
            config: Training configuration
            
        Returns:
            ModelTrainingResult: Training result
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting model training for {config.model_id}")
            
            # Load training data (mock implementation)
            X_train, X_val, X_test, y_train, y_val, y_test = await self._load_training_data(config)
            
            # Get model configuration
            model_config = self.models.get(config.model_id)
            if model_config is None:
                raise ValueError(f"Model configuration {config.model_id} not found")
            
            # Train model based on type
            if model_config.type == ModelType.XGBOOST:
                trained_model, metrics = await self._train_xgboost_model(
                    X_train, X_val, y_train, y_val, config
                )
            elif model_config.type == ModelType.NEURAL_NETWORK:
                trained_model, metrics = await self._train_neural_network_model(
                    X_train, X_val, y_train, y_val, config
                )
            elif model_config.type == ModelType.RANDOM_FOREST:
                trained_model, metrics = await self._train_random_forest_model(
                    X_train, X_val, y_train, y_val, config
                )
            else:
                raise ValueError(f"Unsupported model type: {model_config.type}")
            
            # Save model
            model_path = f"./models/{config.model_id}_{int(time.time())}.pkl"
            joblib.dump(trained_model, model_path)
            
            # Update model configuration
            model_config.model_path = model_path
            model_config.performance = ModelPerformance(
                accuracy=Decimal(str(metrics.accuracy)),
                precision=Decimal(str(metrics.precision)),
                recall=Decimal(str(metrics.recall)),
                f1_score=Decimal(str(metrics.f1_score)),
                roc_auc=Decimal(str(metrics.auc)),
                last_evaluated_at=datetime.utcnow(),
                training_samples=len(X_train),
                validation_samples=len(X_val),
                test_samples=len(X_test)
            )
            model_config.last_trained_at = datetime.utcnow()
            model_config.last_updated_at = datetime.utcnow()
            
            training_duration = time.time() - start_time
            
            result = ModelTrainingResult(
                model_id=config.model_id,
                model_type=model_config.type.value,
                model_name=model_config.name,
                status="completed",
                training_started_at=datetime.fromtimestamp(start_time),
                training_completed_at=datetime.utcnow(),
                training_duration=training_duration,
                metrics=metrics,
                model_file_path=model_path,
                logs_path=f"./logs/{config.model_id}_{int(time.time())}.log"
            )
            
            logger.info(f"Model training completed for {config.model_id} "
                       f"in {training_duration:.2f} seconds")
            
            return result
            
        except (ValueError) as e:
            logger.error(f"Error training model {config.model_id}: {e}")
            raise
    
    async def evaluate_model_async(self, model_id: str) -> ModelMetrics:
        """
        Evaluate model performance
        
        Args:
            model_id: Model identifier
            
        Returns:
            ModelMetrics: Model performance metrics
        """
        try:
            model = await self._get_model_async(model_id)
            if model is None:
                raise ValueError(f"Model {model_id} not found")
            
            # Load test data (mock implementation)
            X_test, y_test = await self._load_test_data(model_id)
            
            # Load trained model
            trained_model = joblib.load(model.model_path)
            
            # Make predictions
            y_pred = trained_model.predict(X_test)
            y_pred_proba = trained_model.predict_proba(X_test)[:, 1] if hasattr(trained_model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            auc = 0.0
            if y_pred_proba is not None:
                auc = roc_auc_score(y_test, y_pred_proba)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            confusion_matrix_obj = ConfusionMatrix(
                true_positives=int(cm[1, 1]),
                true_negatives=int(cm[0, 0]),
                false_positives=int(cm[0, 1]),
                false_negatives=int(cm[1, 0])
            )
            
            metrics = ModelMetrics(
                accuracy=Decimal(str(accuracy)),
                precision=Decimal(str(precision)),
                recall=Decimal(str(recall)),
                f1_score=Decimal(str(f1)),
                auc=Decimal(str(auc)),
                confusion_matrix=confusion_matrix_obj
            )
            
            # Update model performance
            model.performance = ModelPerformance(
                accuracy=metrics.accuracy,
                precision=metrics.precision,
                recall=metrics.recall,
                f1_score=metrics.f1_score,
                roc_auc=metrics.auc,
                last_evaluated_at=datetime.utcnow(),
                training_samples=model.performance.training_samples,
                validation_samples=model.performance.validation_samples,
                test_samples=len(X_test)
            )
            
            logger.info(f"Model evaluation completed for {model_id}: "
                       f"Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
            
            return metrics
            
        except (ValueError) as e:
            logger.error(f"Error evaluating model {model_id}: {e}")
            raise
    
    async def detect_drift_async(self, model_id: str) -> ModelDriftResult:
        """
        Detect model drift
        
        Args:
            model_id: Model identifier
            
        Returns:
            ModelDriftResult: Drift detection result
        """
        try:
            model = await self._get_model_async(model_id)
            if model is None:
                raise ValueError(f"Model {model_id} not found")
            
            # Load current and baseline data (mock implementation)
            current_data, baseline_data = await self._load_drift_data(model_id)
            
            # Calculate drift score (simplified implementation)
            drift_score = self._calculate_drift_score(current_data, baseline_data)
            drift_threshold = Decimal('0.1')
            
            drift_detected = drift_score > drift_threshold
            affected_features = []
            
            if drift_detected:
                # Identify affected features (simplified)
                affected_features = ["transaction_amount", "merchant_category", "time_of_day"]
            
            result = ModelDriftResult(
                model_id=model_id,
                drift_detected=drift_detected,
                drift_score=drift_score,
                drift_threshold=drift_threshold,
                affected_features=affected_features,
                drift_details={
                    "statistical_distance": float(drift_score),
                    "feature_drift_scores": {f: float(drift_score) for f in affected_features}
                },
                detection_timestamp=datetime.utcnow(),
                recommendations=[
                    "Consider retraining the model" if drift_detected else "Model performance is stable",
                    "Monitor feature distributions closely" if drift_detected else "Continue regular monitoring"
                ]
            )
            
            self.drift_results[f"{model_id}_{int(time.time())}"] = result
            
            logger.info(f"Drift detection completed for {model_id}: "
                       f"Drift detected: {drift_detected}, Score: {drift_score}")
            
            return result
            
        except (ValueError) as e:
            logger.error(f"Error detecting drift for {model_id}: {e}")
            raise
    
    # Private helper methods
    
    async def _get_model_async(self, model_id: str) -> Optional[MLModel]:
        """Get model by ID"""
        return self.models.get(model_id)
    
    async def _predict_with_model_async(self, request: ModelPredictionRequest, model: MLModel) -> ModelPredictionResponse:
        """Make prediction with specific model"""
        start_time = time.time()
        
        try:
            # Load trained model
            trained_model = joblib.load(model.model_path)
            
            # Prepare features
            features_array = self._prepare_features(request.features, model.features)
            
            # Make prediction
            prediction = trained_model.predict([features_array])[0]
            probability = 0.5  # Default probability
            
            if hasattr(trained_model, 'predict_proba'):
                probabilities = trained_model.predict_proba([features_array])[0]
                probability = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
            
            processing_time = (time.time() - start_time) * 1000
            
            prediction_id = f"pred_{self.next_prediction_id}_{int(time.time())}"
            self.next_prediction_id += 1
            
            response = ModelPredictionResponse(
                prediction_id=prediction_id,
                model_id=request.model_id,
                prediction=int(prediction),
                probability=Decimal(str(probability)),
                confidence=Decimal(str(probability)),
                processing_time_ms=processing_time,
                timestamp=datetime.utcnow(),
                metadata={
                    "model_type": model.type.value,
                    "model_version": model.version,
                    "features_used": list(request.features.keys())
                }
            )
            
            self.predictions[prediction_id] = response
            
            logger.info(f"Prediction completed: {prediction} "
                       f"(Probability: {probability:.3f}, Time: {processing_time:.1f}ms)")
            
            return response
            
        except (ValueError) as e:
            logger.error(f"Error making prediction with model {model.id}: {e}")
            raise
    
    async def _predict_with_fallback_async(self, request: ModelPredictionRequest) -> ModelPredictionResponse:
        """Fallback prediction when circuit breaker is open"""
        prediction_id = f"fallback_{self.next_prediction_id}_{int(time.time())}"
        self.next_prediction_id += 1
        
        return ModelPredictionResponse(
            prediction_id=prediction_id,
            model_id=request.model_id,
            prediction=0,  # Default to non-fraud
            probability=Decimal('0.5'),
            confidence=Decimal('0.3'),
            processing_time_ms=1.0,
            timestamp=datetime.utcnow(),
            metadata={
                "fallback": True,
                "circuit_breaker_open": self.circuit_breaker_open,
                "reason": "Circuit breaker open or model unavailable"
            }
        )
    
    async def _handle_prediction_failure(self):
        """Handle prediction failure for circuit breaker"""
        self.circuit_breaker_failure_count += 1
        self.circuit_breaker_last_failure = datetime.utcnow()
        
        if self.circuit_breaker_failure_count >= 5:
            self.circuit_breaker_open = True
            logger.warning("Circuit breaker opened due to repeated failures")
    
    def _weighted_voting(self, predictions: List[Any], probabilities: List[float], weights: Dict[str, Decimal]) -> Tuple[Any, float]:
        """Weighted voting ensemble method"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            weight = float(weights.get(f"model_{i}", Decimal('1.0')))
            weighted_sum += prob * weight
            total_weight += weight
        
        final_probability = weighted_sum / total_weight if total_weight > 0 else 0.5
        final_prediction = 1 if final_probability > 0.5 else 0
        
        return final_prediction, final_probability
    
    def _simple_voting(self, predictions: List[Any], probabilities: List[float]) -> Tuple[Any, float]:
        """Simple voting ensemble method"""
        fraud_votes = sum(1 for pred in predictions if pred == 1)
        total_votes = len(predictions)
        
        final_prediction = 1 if fraud_votes > total_votes / 2 else 0
        final_probability = fraud_votes / total_votes if total_votes > 0 else 0.5
        
        return final_prediction, final_probability
    
    def _prepare_features(self, features: Dict[str, Any], model_features: Dict[str, Any]) -> List[float]:
        """Prepare features for model prediction"""
        # Simplified feature preparation
        feature_vector = []
        
        for feature_name, feature_type in model_features.items():
            if feature_name in features:
                value = features[feature_name]
                if feature_type == "numeric":
                    feature_vector.append(float(value))
                elif feature_type == "categorical":
                    # Simple categorical encoding
                    feature_vector.append(hash(str(value)) % 1000)
            else:
                feature_vector.append(0.0)  # Default value
        
        return feature_vector
    
    async def _load_training_data(self, config: ModelTrainingConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load training data (mock implementation)"""
        # Generate mock training data
        np.random.seed(42)
        n_samples = 10000
        
        X = np.random.randn(n_samples, 6)  # 6 features
        y = np.random.randint(0, 2, n_samples)  # Binary classification
        
        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    async def _load_test_data(self, model_id: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load test data (mock implementation)"""
        np.random.seed(123)
        n_samples = 1000
        
        X_test = np.random.randn(n_samples, 6)
        y_test = np.random.randint(0, 2, n_samples)
        
        return X_test, y_test
    
    async def _load_drift_data(self, model_id: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load drift detection data (mock implementation)"""
        np.random.seed(456)
        
        # Baseline data
        baseline_data = np.random.randn(1000, 6)
        
        # Current data (slightly different distribution)
        current_data = np.random.randn(1000, 6) + 0.1
        
        return current_data, baseline_data
    
    def _calculate_drift_score(self, current_data: np.ndarray, baseline_data: np.ndarray) -> Decimal:
        """Calculate drift score between current and baseline data"""
        # Simplified drift calculation using mean difference
        current_mean = np.mean(current_data)
        baseline_mean = np.mean(baseline_data)
        
        drift_score = abs(current_mean - baseline_mean) / abs(baseline_mean) if baseline_mean != 0 else 0
        
        return Decimal(str(drift_score))
    
    async def _train_xgboost_model(self, X_train: np.ndarray, X_val: np.ndarray, y_train: np.ndarray, y_val: np.ndarray, config: ModelTrainingConfig) -> Tuple[Any, ModelMetrics]:
        """Train XGBoost model"""
        model = xgb.XGBClassifier(
            max_depth=6,
            learning_rate=0.1,
            n_estimators=100,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = ModelMetrics(
            accuracy=Decimal(str(accuracy_score(y_val, y_pred))),
            precision=Decimal(str(precision_score(y_val, y_pred, average='weighted'))),
            recall=Decimal(str(recall_score(y_val, y_pred, average='weighted'))),
            f1_score=Decimal(str(f1_score(y_val, y_pred, average='weighted'))),
            auc=Decimal(str(roc_auc_score(y_val, y_pred_proba)))
        )
        
        return model, metrics
    
    async def _train_neural_network_model(self, X_train: np.ndarray, X_val: np.ndarray, y_train: np.ndarray, y_val: np.ndarray, config: ModelTrainingConfig) -> Tuple[Any, ModelMetrics]:
        """Train Neural Network model (using Random Forest as proxy)"""
        # Using Random Forest as a proxy for Neural Network for simplicity
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = ModelMetrics(
            accuracy=Decimal(str(accuracy_score(y_val, y_pred))),
            precision=Decimal(str(precision_score(y_val, y_pred, average='weighted'))),
            recall=Decimal(str(recall_score(y_val, y_pred, average='weighted'))),
            f1_score=Decimal(str(f1_score(y_val, y_pred, average='weighted'))),
            auc=Decimal(str(roc_auc_score(y_val, y_pred_proba)))
        )
        
        return model, metrics
    
    async def _train_random_forest_model(self, X_train: np.ndarray, X_val: np.ndarray, y_train: np.ndarray, y_val: np.ndarray, config: ModelTrainingConfig) -> Tuple[Any, ModelMetrics]:
        """Train Random Forest model"""
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = ModelMetrics(
            accuracy=Decimal(str(accuracy_score(y_test, y_pred))),
            precision=Decimal(str(precision_score(y_val, y_pred, average='weighted'))),
            recall=Decimal(str(recall_score(y_val, y_pred, average='weighted'))),
            f1_score=Decimal(str(f1_score(y_val, y_pred, average='weighted'))),
            auc=Decimal(str(roc_auc_score(y_val, y_pred_proba)))
        )
        
        return model, metrics
