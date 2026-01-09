"""
ML Training Pipeline Service
Productionized ML model training and optimization pipeline
Python equivalent of C# MLModelTrainingService
"""

import asyncio
import logging
import pickle
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.neural_network import MLPClassifier
import joblib
import schedule
import threading
import time

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """ML model types"""
    XGBOOST = "xgboost"
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    ENSEMBLE = "ensemble"

class TrainingStatus(Enum):
    """Training status"""
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    DEPRECATED = "deprecated"

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    training_time: float
    prediction_time: float
    feature_importance: Dict[str, float]
    confusion_matrix: List[List[int]]

@dataclass
class TrainingConfig:
    """Training configuration"""
    model_type: ModelType
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    hyperparameter_tuning: bool = True
    feature_selection: bool = True
    cross_validation: bool = True
    early_stopping: bool = True
    max_iterations: int = 1000

@dataclass
class ModelVersion:
    """Model version information"""
    version_id: str
    model_type: ModelType
    training_config: TrainingConfig
    metrics: ModelMetrics
    training_data_size: int
    training_duration: float
    created_at: datetime
    status: TrainingStatus
    model_path: str
    hyperparameters: Dict[str, Any]
    feature_names: List[str]

class MLTrainingPipeline:
    """
    ML Training Pipeline Service
    
    Productionized ML model training and optimization pipeline with:
    - Automated model training and evaluation
    - Hyperparameter optimization
    - Model versioning and management
    - Performance monitoring and drift detection
    - Scheduled retraining
    """
    
    def __init__(self):
        self.models: Dict[str, ModelVersion] = {}
        self.training_queue: List[Dict[str, Any]] = []
        self.model_storage_path = "models"
        self.training_data_path = "training_data"
        self.is_training = False
        self.training_thread = None
        
        # Create directories
        os.makedirs(self.model_storage_path, exist_ok=True)
        os.makedirs(self.training_data_path, exist_ok=True)
        
        # Initialize default configurations
        self.default_configs = {
            ModelType.XGBOOST: TrainingConfig(
                model_type=ModelType.XGBOOST,
                hyperparameter_tuning=True,
                early_stopping=True
            ),
            ModelType.NEURAL_NETWORK: TrainingConfig(
                model_type=ModelType.NEURAL_NETWORK,
                max_iterations=1000,
                early_stopping=True
            ),
            ModelType.RANDOM_FOREST: TrainingConfig(
                model_type=ModelType.RANDOM_FOREST,
                hyperparameter_tuning=True
            ),
            ModelType.ENSEMBLE: TrainingConfig(
                model_type=ModelType.ENSEMBLE,
                hyperparameter_tuning=True
            )
        }
        
        # Start background training scheduler
        self._start_training_scheduler()
        
        logger.info("ML Training Pipeline initialized")
    
    def _start_training_scheduler(self):
        """Start background training scheduler"""
        def run_scheduler():
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Training scheduler error: {e}")
                    time.sleep(60)
        
        # Schedule daily retraining
        schedule.every().day.at("02:00").do(self._scheduled_retraining)
        
        # Start scheduler thread
        self.training_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.training_thread.start()
        
        logger.info("Training scheduler started")
    
    async def train_model(self, training_data: List[Dict[str, Any]], 
                         config: Optional[TrainingConfig] = None,
                         model_name: str = "fraud_detection") -> ModelVersion:
        """Train a new ML model"""
        try:
            if self.is_training:
                raise Exception("Training already in progress")
            
            self.is_training = True
            
            # Use default config if not provided
            if config is None:
                config = self.default_configs[ModelType.XGBOOST]
            
            logger.info(f"Starting model training: {config.model_type.value}")
            
            # Prepare training data
            X, y, feature_names = await self._prepare_training_data(training_data)
            
            if len(X) < 100:
                raise Exception("Insufficient training data (minimum 100 samples required)")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state, stratify=y
            )
            
            # Train model
            start_time = time.time()
            model, hyperparameters = await self._train_model_with_config(
                X_train, y_train, config
            )
            training_duration = time.time() - start_time
            
            # Evaluate model
            metrics = await self._evaluate_model(model, X_test, y_test, feature_names)
            
            # Create model version
            version_id = f"{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            model_version = ModelVersion(
                version_id=version_id,
                model_type=config.model_type,
                training_config=config,
                metrics=metrics,
                training_data_size=len(training_data),
                training_duration=training_duration,
                created_at=datetime.utcnow(),
                status=TrainingStatus.COMPLETED,
                model_path=f"{self.model_storage_path}/{version_id}.pkl",
                hyperparameters=hyperparameters,
                feature_names=feature_names
            )
            
            # Save model
            await self._save_model(model, model_version)
            
            # Store model version
            self.models[version_id] = model_version
            
            # Set as active model if it's the best performing
            await self._update_active_model(model_version)
            
            logger.info(f"Model training completed: {version_id}")
            return model_version
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Model training failed: {e}")
            raise
        finally:
            self.is_training = False
    
    async def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data for ML models"""
        try:
            df = pd.DataFrame(training_data)
            
            # Define feature columns (exclude target and metadata)
            exclude_columns = ['is_fraud', 'fraud_label', 'target', 'id', 'created_at', 'updated_at']
            feature_columns = [col for col in df.columns if col not in exclude_columns]
            
            # Handle missing values
            df[feature_columns] = df[feature_columns].fillna(0)
            
            # Convert categorical variables to numeric
            for col in feature_columns:
                if df[col].dtype == 'object':
                    df[col] = pd.Categorical(df[col]).codes
            
            # Prepare features and target
            X = df[feature_columns].values
            y = df['is_fraud'].values if 'is_fraud' in df.columns else df['fraud_label'].values
            
            return X, y, feature_columns
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to prepare training data: {e}")
            raise
    
    async def _train_model_with_config(self, X_train: np.ndarray, y_train: np.ndarray, 
                                     config: TrainingConfig) -> Tuple[Any, Dict[str, Any]]:
        """Train model with specific configuration"""
        try:
            if config.model_type == ModelType.XGBOOST:
                return await self._train_xgboost_model(X_train, y_train, config)
            elif config.model_type == ModelType.NEURAL_NETWORK:
                return await self._train_neural_network_model(X_train, y_train, config)
            elif config.model_type == ModelType.RANDOM_FOREST:
                return await self._train_random_forest_model(X_train, y_train, config)
            elif config.model_type == ModelType.ENSEMBLE:
                return await self._train_ensemble_model(X_train, y_train, config)
            else:
                raise ValueError(f"Unsupported model type: {config.model_type}")
                
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to train model: {e}")
            raise
    
    async def _train_xgboost_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                                 config: TrainingConfig) -> Tuple[Any, Dict[str, Any]]:
        """Train XGBoost model"""
        try:
            # Default hyperparameters
            params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': config.random_state
            }
            
            # Hyperparameter tuning if enabled
            if config.hyperparameter_tuning:
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 6, 9],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0]
                }
                
                xgb_model = xgb.XGBClassifier(random_state=config.random_state)
                grid_search = GridSearchCV(
                    xgb_model, param_grid, cv=config.cv_folds, 
                    scoring='roc_auc', n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                
                model = grid_search.best_estimator_
                params = grid_search.best_params_
            else:
                model = xgb.XGBClassifier(**params)
                model.fit(X_train, y_train)
            
            return model, params
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to train XGBoost model: {e}")
            raise
    
    async def _train_neural_network_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                                        config: TrainingConfig) -> Tuple[Any, Dict[str, Any]]:
        """Train Neural Network model"""
        try:
            # Default hyperparameters
            params = {
                'hidden_layer_sizes': (100, 50),
                'activation': 'relu',
                'solver': 'adam',
                'alpha': 0.001,
                'learning_rate': 'adaptive',
                'max_iter': config.max_iterations,
                'random_state': config.random_state,
                'early_stopping': config.early_stopping
            }
            
            # Hyperparameter tuning if enabled
            if config.hyperparameter_tuning:
                param_grid = {
                    'hidden_layer_sizes': [(50,), (100,), (100, 50), (200, 100)],
                    'activation': ['relu', 'tanh'],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate': ['constant', 'adaptive']
                }
                
                nn_model = MLPClassifier(random_state=config.random_state)
                grid_search = GridSearchCV(
                    nn_model, param_grid, cv=config.cv_folds,
                    scoring='roc_auc', n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                
                model = grid_search.best_estimator_
                params = grid_search.best_params_
            else:
                model = MLPClassifier(**params)
                model.fit(X_train, y_train)
            
            return model, params
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to train Neural Network model: {e}")
            raise
    
    async def _train_random_forest_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                                       config: TrainingConfig) -> Tuple[Any, Dict[str, Any]]:
        """Train Random Forest model"""
        try:
            # Default hyperparameters
            params = {
                'n_estimators': 100,
                'max_depth': None,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'random_state': config.random_state
            }
            
            # Hyperparameter tuning if enabled
            if config.hyperparameter_tuning:
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [None, 10, 20, 30],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
                
                rf_model = RandomForestClassifier(random_state=config.random_state)
                grid_search = GridSearchCV(
                    rf_model, param_grid, cv=config.cv_folds,
                    scoring='roc_auc', n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                
                model = grid_search.best_estimator_
                params = grid_search.best_params_
            else:
                model = RandomForestClassifier(**params)
                model.fit(X_train, y_train)
            
            return model, params
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to train Random Forest model: {e}")
            raise
    
    async def _train_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                                  config: TrainingConfig) -> Tuple[Any, Dict[str, Any]]:
        """Train Ensemble model"""
        try:
            from sklearn.ensemble import VotingClassifier
            
            # Create individual models
            xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=config.random_state)
            rf_model = RandomForestClassifier(n_estimators=100, random_state=config.random_state)
            nn_model = MLPClassifier(hidden_layer_sizes=(100, 50), random_state=config.random_state)
            
            # Create ensemble
            ensemble = VotingClassifier(
                estimators=[
                    ('xgboost', xgb_model),
                    ('random_forest', rf_model),
                    ('neural_network', nn_model)
                ],
                voting='soft'
            )
            
            ensemble.fit(X_train, y_train)
            
            params = {
                'ensemble_type': 'voting',
                'models': ['xgboost', 'random_forest', 'neural_network'],
                'voting': 'soft'
            }
            
            return ensemble, params
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to train Ensemble model: {e}")
            raise
    
    async def _evaluate_model(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, 
                            feature_names: List[str]) -> ModelMetrics:
        """Evaluate model performance"""
        try:
            start_time = time.time()
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
            prediction_time = time.time() - start_time
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            roc_auc = roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.0
            
            # Feature importance
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                for i, feature in enumerate(feature_names):
                    feature_importance[feature] = float(model.feature_importances_[i])
            elif hasattr(model, 'coef_'):
                for i, feature in enumerate(feature_names):
                    feature_importance[feature] = float(abs(model.coef_[0][i]))
            
            # Confusion matrix
            from sklearn.metrics import confusion_matrix
            cm = confusion_matrix(y_test, y_pred).tolist()
            
            return ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                roc_auc=roc_auc,
                training_time=0.0,  # Will be set by caller
                prediction_time=prediction_time,
                feature_importance=feature_importance,
                confusion_matrix=cm
            )
            
        except (ValueError) as e:
            logger.error(f"Failed to evaluate model: {e}")
            raise
    
    async def _save_model(self, model: Any, model_version: ModelVersion):
        """Save trained model"""
        try:
            # Save model using joblib
            joblib.dump(model, model_version.model_path)
            
            # Save model metadata
            metadata_path = f"{self.model_storage_path}/{model_version.version_id}_metadata.json"
            metadata = {
                'version_id': model_version.version_id,
                'model_type': model_version.model_type.value,
                'metrics': {
                    'accuracy': model_version.metrics.accuracy,
                    'precision': model_version.metrics.precision,
                    'recall': model_version.metrics.recall,
                    'f1_score': model_version.metrics.f1_score,
                    'roc_auc': model_version.metrics.roc_auc
                },
                'hyperparameters': model_version.hyperparameters,
                'feature_names': model_version.feature_names,
                'created_at': model_version.created_at.isoformat(),
                'training_data_size': model_version.training_data_size
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model saved: {model_version.model_path}")
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    async def _update_active_model(self, model_version: ModelVersion):
        """Update active model if this is the best performing"""
        try:
            # Check if this is the best model
            best_model = None
            best_score = 0.0
            
            for version_id, version in self.models.items():
                if version.status == TrainingStatus.COMPLETED:
                    score = version.metrics.roc_auc
                    if score > best_score:
                        best_score = score
                        best_model = version
            
            # Update active model marker
            if best_model and best_model.version_id == model_version.version_id:
                logger.info(f"New active model: {model_version.version_id}")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to update active model: {e}")
    
    async def load_model(self, version_id: str) -> Optional[Any]:
        """Load trained model"""
        try:
            if version_id not in self.models:
                logger.warning(f"Model version not found: {version_id}")
                return None
            
            model_version = self.models[version_id]
            if not os.path.exists(model_version.model_path):
                logger.warning(f"Model file not found: {model_version.model_path}")
                return None
            
            model = joblib.load(model_version.model_path)
            logger.info(f"Model loaded: {version_id}")
            return model
            
        except (OSError) as e:
            logger.error(f"Failed to load model: {e}")
            return None
    
    async def get_model_versions(self) -> List[ModelVersion]:
        """Get all model versions"""
        try:
            return list(self.models.values())
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get model versions: {e}")
            return []
    
    async def get_best_model(self) -> Optional[ModelVersion]:
        """Get the best performing model"""
        try:
            best_model = None
            best_score = 0.0
            
            for version in self.models.values():
                if version.status == TrainingStatus.COMPLETED:
                    score = version.metrics.roc_auc
                    if score > best_score:
                        best_score = score
                        best_model = version
            
            return best_model
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get best model: {e}")
            return None
    
    async def detect_model_drift(self, version_id: str, new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect model drift"""
        try:
            if version_id not in self.models:
                return {'drift_detected': False, 'message': 'Model version not found'}
            
            model_version = self.models[version_id]
            model = await self.load_model(version_id)
            
            if model is None:
                return {'drift_detected': False, 'message': 'Model could not be loaded'}
            
            # Prepare new data
            X_new, _, _ = await self._prepare_training_data(new_data)
            
            # Get predictions on new data
            y_pred_new = model.predict(X_new)
            y_pred_proba_new = model.predict_proba(X_new)[:, 1] if hasattr(model, 'predict_proba') else y_pred_new
            
            # Calculate performance on new data
            # Note: In real scenario, you'd need ground truth labels
            # For now, we'll use prediction distribution analysis
            
            prediction_mean = np.mean(y_pred_proba_new)
            prediction_std = np.std(y_pred_proba_new)
            
            # Simple drift detection based on prediction distribution
            # In production, you'd use more sophisticated methods like KS test, PSI, etc.
            drift_threshold = 0.1  # 10% change threshold
            
            # This is a simplified drift detection
            # Real implementation would compare with baseline distribution
            drift_detected = prediction_std > drift_threshold
            
            return {
                'drift_detected': drift_detected,
                'prediction_mean': float(prediction_mean),
                'prediction_std': float(prediction_std),
                'drift_threshold': drift_threshold,
                'message': 'Drift detected' if drift_detected else 'No significant drift detected'
            }
            
        except (ValueError) as e:
            logger.error(f"Failed to detect model drift: {e}")
            return {'drift_detected': False, 'message': f'Error: {str(e)}'}
    
    async def _scheduled_retraining(self):
        """Scheduled retraining job"""
        try:
            logger.info("Starting scheduled retraining")
            
            # Get recent data for retraining
            # In production, this would fetch from database
            recent_data = await self._get_recent_training_data()
            
            if len(recent_data) < 100:
                logger.warning("Insufficient data for scheduled retraining")
                return
            
            # Train new model
            config = self.default_configs[ModelType.XGBOOST]
            await self.train_model(recent_data, config, "scheduled_retraining")
            
            logger.info("Scheduled retraining completed")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Scheduled retraining failed: {e}")
    
    async def _get_recent_training_data(self) -> List[Dict[str, Any]]:
        """Get recent training data"""
        # This is a placeholder - in production, fetch from database
        return []
    
    async def get_training_status(self) -> Dict[str, Any]:
        """Get current training status"""
        try:
            return {
                'is_training': self.is_training,
                'models_count': len(self.models),
                'training_queue_size': len(self.training_queue),
                'active_model': await self.get_best_model(),
                'last_training': max([m.created_at for m in self.models.values()]).isoformat() if self.models else None
            }
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get training status: {e}")
            return {}


# Global ML training pipeline instance
ml_training_pipeline = MLTrainingPipeline()
