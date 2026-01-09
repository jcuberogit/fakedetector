#!/usr/bin/env python3
"""
ML Models for Fraud Detection
Python equivalent of C# MLModels.cs
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class ModelType(str, Enum):
    """ML Model types"""
    XGBOOST = "XGBoost"
    NEURAL_NETWORK = "NeuralNetwork"
    RANDOM_FOREST = "RandomForest"
    LOGISTIC_REGRESSION = "LogisticRegression"
    SUPPORT_VECTOR_MACHINE = "SupportVectorMachine"
    ISOLATION_FOREST = "IsolationForest"
    ONE_CLASS_SVM = "OneClassSVM"
    AUTOENCODER = "Autoencoder"
    LSTM = "LSTM"
    TRANSFORMER = "Transformer"
    ENSEMBLE = "Ensemble"
    CUSTOM = "Custom"


class ModelStatus(str, Enum):
    """Model status"""
    TRAINING = "Training"
    VALIDATING = "Validating"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DEPRECATED = "Deprecated"
    ERROR = "Error"
    PENDING = "Pending"


class EnsembleMethod(str, Enum):
    """Ensemble methods"""
    VOTING = "Voting"
    WEIGHTED_VOTING = "WeightedVoting"
    STACKING = "Stacking"
    BLENDING = "Blending"
    BAGGING = "Bagging"
    BOOSTING = "Boosting"
    DYNAMIC_WEIGHTING = "DynamicWeighting"


class ConfusionMatrix(BaseModel):
    """Confusion matrix for classification models"""
    true_positives: int = Field(default=0, description="True positives")
    true_negatives: int = Field(default=0, description="True negatives")
    false_positives: int = Field(default=0, description="False positives")
    false_negatives: int = Field(default=0, description="False negatives")


class ModelPerformance(BaseModel):
    """Model performance metrics"""
    accuracy: Decimal = Field(default=Decimal('0'), description="Accuracy score")
    precision: Decimal = Field(default=Decimal('0'), description="Precision score")
    recall: Decimal = Field(default=Decimal('0'), description="Recall score")
    f1_score: Decimal = Field(default=Decimal('0'), description="F1 score")
    roc_auc: Decimal = Field(default=Decimal('0'), description="ROC AUC score")
    prc_auc: Decimal = Field(default=Decimal('0'), description="PRC AUC score")
    true_positive_rate: Decimal = Field(default=Decimal('0'), description="True positive rate")
    false_positive_rate: Decimal = Field(default=Decimal('0'), description="False positive rate")
    true_negative_rate: Decimal = Field(default=Decimal('0'), description="True negative rate")
    false_negative_rate: Decimal = Field(default=Decimal('0'), description="False negative rate")
    class_metrics: Dict[str, Decimal] = Field(default_factory=dict, description="Class-specific metrics")
    feature_importance: Dict[str, Decimal] = Field(default_factory=dict, description="Feature importance scores")
    last_evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Last evaluation time")
    training_samples: int = Field(default=0, description="Number of training samples")
    validation_samples: int = Field(default=0, description="Number of validation samples")
    test_samples: int = Field(default=0, description="Number of test samples")


class MLModel(BaseModel):
    """ML Model for fraud detection"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    type: ModelType = Field(..., description="Model type")
    status: ModelStatus = Field(default=ModelStatus.PENDING, description="Model status")
    version: str = Field(default="1.0.0", description="Model version")
    model_path: str = Field(default="", description="Path to model file")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    features: Dict[str, Any] = Field(default_factory=dict, description="Model features")
    performance: ModelPerformance = Field(default_factory=ModelPerformance, description="Model performance")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    last_trained_at: datetime = Field(default_factory=datetime.utcnow, description="Last training time")
    created_by: str = Field(default="system", description="Created by")
    source: str = Field(default="default", description="Model source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EnsembleConfig(BaseModel):
    """Ensemble configuration"""
    id: str = Field(..., description="Ensemble identifier")
    name: str = Field(..., description="Ensemble name")
    model_ids: List[str] = Field(default_factory=list, description="Model IDs in ensemble")
    method: EnsembleMethod = Field(..., description="Ensemble method")
    model_weights: Dict[str, Decimal] = Field(default_factory=dict, description="Model weights")
    voting_threshold: Decimal = Field(default=Decimal('0.5'), description="Voting threshold")
    enable_dynamic_weighting: bool = Field(default=False, description="Enable dynamic weighting")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Ensemble parameters")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class ModelTrainingConfig(BaseModel):
    """Model training configuration"""
    model_id: str = Field(..., description="Model identifier")
    dataset_path: str = Field(..., description="Dataset path")
    train_split: Decimal = Field(default=Decimal('0.7'), description="Training split ratio")
    validation_split: Decimal = Field(default=Decimal('0.15'), description="Validation split ratio")
    test_split: Decimal = Field(default=Decimal('0.15'), description="Test split ratio")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Training hyperparameters")
    max_epochs: int = Field(default=100, description="Maximum epochs")
    learning_rate: Decimal = Field(default=Decimal('0.01'), description="Learning rate")
    batch_size: int = Field(default=32, description="Batch size")
    enable_early_stopping: bool = Field(default=True, description="Enable early stopping")
    patience: int = Field(default=10, description="Early stopping patience")
    metric_to_monitor: str = Field(default="val_loss", description="Metric to monitor")
    mode: str = Field(default="min", description="Monitoring mode")
    callbacks: Dict[str, Any] = Field(default_factory=dict, description="Training callbacks")
    data_augmentation: Dict[str, Any] = Field(default_factory=dict, description="Data augmentation settings")


class ModelPredictionRequest(BaseModel):
    """Model prediction request"""
    model_id: str = Field(..., description="Model identifier")
    features: Dict[str, Any] = Field(..., description="Input features")
    transaction_id: str = Field(default="", description="Transaction identifier")
    user_id: str = Field(default="", description="User identifier")
    return_probabilities: bool = Field(default=True, description="Return probabilities")
    return_feature_importance: bool = Field(default=False, description="Return feature importance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelPredictionResponse(BaseModel):
    """Model prediction response"""
    prediction_id: str = Field(..., description="Prediction identifier")
    model_id: str = Field(..., description="Model identifier")
    prediction: Union[int, float, str] = Field(..., description="Prediction result")
    probability: Decimal = Field(default=Decimal('0'), description="Prediction probability")
    probabilities: Dict[str, Decimal] = Field(default_factory=dict, description="Class probabilities")
    feature_importance: Dict[str, Decimal] = Field(default_factory=dict, description="Feature importance")
    confidence: Decimal = Field(default=Decimal('0'), description="Prediction confidence")
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Prediction timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelMetrics(BaseModel):
    """Model performance metrics"""
    accuracy: Decimal = Field(default=Decimal('0'), description="Accuracy")
    precision: Decimal = Field(default=Decimal('0'), description="Precision")
    recall: Decimal = Field(default=Decimal('0'), description="Recall")
    f1_score: Decimal = Field(default=Decimal('0'), description="F1 score")
    auc: Decimal = Field(default=Decimal('0'), description="AUC")
    rmse: Decimal = Field(default=Decimal('0'), description="RMSE")
    mae: Decimal = Field(default=Decimal('0'), description="MAE")
    class_specific_metrics: Dict[str, Decimal] = Field(default_factory=dict, description="Class-specific metrics")
    feature_importance: Dict[str, Decimal] = Field(default_factory=dict, description="Feature importance")
    confusion_matrix: ConfusionMatrix = Field(default_factory=ConfusionMatrix, description="Confusion matrix")


class ModelTrainingResult(BaseModel):
    """Model training result"""
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Model type")
    model_name: str = Field(..., description="Model name")
    status: str = Field(..., description="Training status")
    training_started_at: datetime = Field(..., description="Training start time")
    training_completed_at: Optional[datetime] = Field(None, description="Training completion time")
    training_duration: Optional[float] = Field(None, description="Training duration in seconds")
    metrics: ModelMetrics = Field(default_factory=ModelMetrics, description="Training metrics")
    model_file_path: str = Field(default="", description="Model file path")
    logs_path: str = Field(default="", description="Logs path")
    warnings: List[str] = Field(default_factory=list, description="Training warnings")
    errors: List[str] = Field(default_factory=list, description="Training errors")
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Training artifacts")


class ModelVersion(BaseModel):
    """Model version information"""
    model_id: str = Field(..., description="Model identifier")
    version: str = Field(..., description="Version number")
    model_type: str = Field(..., description="Model type")
    model_name: str = Field(..., description="Model name")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    deployed_at: Optional[datetime] = Field(None, description="Deployment time")
    status: str = Field(default="training", description="Version status")
    metrics: ModelMetrics = Field(default_factory=ModelMetrics, description="Version metrics")
    model_file_path: str = Field(default="", description="Model file path")
    description: str = Field(default="", description="Version description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelDriftResult(BaseModel):
    """Model drift detection result"""
    model_id: str = Field(..., description="Model identifier")
    drift_detected: bool = Field(default=False, description="Whether drift was detected")
    drift_score: Decimal = Field(default=Decimal('0'), description="Drift score")
    drift_threshold: Decimal = Field(default=Decimal('0.1'), description="Drift threshold")
    affected_features: List[str] = Field(default_factory=list, description="Affected features")
    drift_details: Dict[str, Any] = Field(default_factory=dict, description="Drift details")
    detection_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class ModelFeedback(BaseModel):
    """Model feedback for continuous learning"""
    feedback_id: str = Field(..., description="Feedback identifier")
    model_id: str = Field(..., description="Model identifier")
    prediction_id: str = Field(..., description="Prediction identifier")
    actual_label: Union[int, str] = Field(..., description="Actual label")
    predicted_label: Union[int, str] = Field(..., description="Predicted label")
    feedback_type: str = Field(default="correction", description="Feedback type")
    feedback_source: str = Field(default="user", description="Feedback source")
    feedback_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feedback time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelPerformanceMonitor(BaseModel):
    """Model performance monitoring results"""
    model_id: str = Field(..., description="Model identifier")
    monitored_at: datetime = Field(default_factory=datetime.utcnow, description="Monitoring time")
    current_metrics: ModelMetrics = Field(default_factory=ModelMetrics, description="Current metrics")
    baseline_metrics: ModelMetrics = Field(default_factory=ModelMetrics, description="Baseline metrics")
    performance_degradation: Decimal = Field(default=Decimal('0'), description="Performance degradation percentage")
    is_data_drift_detected: bool = Field(default=False, description="Data drift detected")
    is_performance_degraded: bool = Field(default=False, description="Performance degraded")
    alerts: List[str] = Field(default_factory=list, description="Performance alerts")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    requires_retraining: bool = Field(default=False, description="Requires retraining")
    retraining_reason: str = Field(default="", description="Retraining reason")


class ModelRetrainingJob(BaseModel):
    """Model retraining job information"""
    job_id: str = Field(..., description="Job identifier")
    model_id: str = Field(..., description="Model identifier")
    status: str = Field(default="pending", description="Job status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    progress_percentage: Decimal = Field(default=Decimal('0'), description="Progress percentage")
    error_message: str = Field(default="", description="Error message")
    retraining_reason: str = Field(default="", description="Retraining reason")
    new_model_version: str = Field(default="", description="New model version")
    metrics: ModelMetrics = Field(default_factory=ModelMetrics, description="Training metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
