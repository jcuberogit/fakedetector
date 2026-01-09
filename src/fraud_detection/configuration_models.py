"""
Configuration models for the Python Fraud Detection Agent.
Mirrors the C# configuration system from FraudDetectionAgent.Api.Models.Configuration.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    provider: str = "SQLite"
    connection_strings: Dict[str, str] = Field(default_factory=lambda: {
        "SQLite": "Data Source=Data/frauddetection.db",
        "SQLServer": "Server=(localdb)\\mssqllocaldb;Database=FraudDetectionAgent;Trusted_Connection=true;MultipleActiveResultSets=true;TrustServerCertificate=True",
        "PostgreSQL": "Host=localhost;Database=FraudDetectionAgent;Username=postgres;Password=yourpassword;Include Error Detail=true;",
        "MySQL": "Server=localhost;Database=FraudDetectionAgent;Uid=root;Pwd=yourpassword;"
    })
    enable_sensitive_data_logging: bool = False
    enable_detailed_errors: bool = True
    max_retry_count: int = 3
    command_timeout: int = 30


class JwtSettings(BaseModel):
    """JWT authentication settings."""
    secret_key: str = "IfFnti/a17oa0mk7lfdFRr3c/p8MvxodfnXVj/3iqYE="
    issuer: str = "FraudDetectionAgent"
    audience: str = "FraudDetectionAgent.Users"
    expiry_minutes: int = 60


class FraudDetectionSettings(BaseModel):
    """Core fraud detection settings."""
    high_risk_threshold: float = 0.7
    critical_risk_threshold: float = 0.9
    alert_retention_days: int = 90
    auto_block_critical_risk: bool = True
    max_transactions_per_hour: int = 50


class AISettings(BaseModel):
    """AI service configuration settings."""
    temperature: float = 0.1
    top_p: float = 0.9
    max_tokens: int = 4000
    conversation_timeout_minutes: int = 30
    max_conversation_history: int = 20
    enable_function_calling: bool = True
    enable_content_filtering: bool = True
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 2
    use_mock_backend: bool = True
    test_ai_gpt_only: bool = True


class MLModelTrainingSettings(BaseModel):
    """ML model training configuration."""
    default_algorithm: str = "RandomForest"
    default_max_epochs: int = 100
    default_learning_rate: float = 0.001
    default_batch_size: int = 32
    training_timeout_minutes: int = 60
    validation_timeout_minutes: int = 30
    deployment_timeout_minutes: int = 45
    max_concurrent_training_jobs: int = 5
    enable_auto_retraining: bool = True
    performance_degradation_threshold: float = 5.0
    data_drift_detection_enabled: bool = True
    model_registry_path: str = "/models"
    training_logs_path: str = "/logs/training"
    model_artifacts_path: str = "/artifacts"


class DataObservabilitySettings(BaseModel):
    """Data observability configuration."""
    default_low_threshold: float = 0.1
    default_warning_threshold: float = 0.25
    default_high_threshold: float = 0.5
    default_critical_threshold: float = 1.0
    minimum_sample_size: int = 100


class ModelPerformanceMonitoringSettings(BaseModel):
    """Model performance monitoring configuration."""
    enable_real_time_monitoring: bool = True
    enable_performance_alerts: bool = True
    enable_drift_detection: bool = True
    enable_automated_retraining: bool = True
    enable_performance_history: bool = True
    enable_comparative_analysis: bool = True
    enable_performance_forecasting: bool = True
    enable_custom_thresholds: bool = True
    enable_performance_reporting: bool = True
    enable_performance_export: bool = True
    monitoring_interval_seconds: int = 300
    max_performance_history_days: int = 30
    default_performance_threshold: float = 0.8
    critical_performance_threshold: float = 0.6
    warning_performance_threshold: float = 0.75
    drift_detection_threshold: float = 0.15
    max_alerts_per_model: int = 10
    max_performance_data_points: int = 100
    enable_email_alerts: bool = True
    enable_slack_alerts: bool = False
    enable_webhook_alerts: bool = False
    alert_email_recipients: str = ""
    slack_webhook_url: str = ""
    webhook_endpoint: str = ""
    alert_cooldown_hours: int = 4
    enable_performance_metrics_aggregation: bool = True
    enable_performance_trend_analysis: bool = True
    enable_performance_anomaly_detection: bool = True
    enable_performance_optimization: bool = True


class AdvancedRulesEngineSettings(BaseModel):
    """Advanced rules engine configuration."""
    is_enabled: bool = True
    rule_store_provider: str = "InMemory"


class GNNModelSettings(BaseModel):
    """GNN model configuration settings."""
    model_type: str = "GraphSAGE"
    hidden_dimensions: int = 64
    num_layers: int = 3
    learning_rate: float = 0.001
    epochs: int = 100
    dropout_rate: float = 0.2
    activation_function: str = "ReLU"
    aggregation_function: str = "Mean"


class GraphConstructionSettings(BaseModel):
    """Graph construction settings."""
    max_graph_size: int = 10000
    max_node_degree: int = 100
    min_edge_weight: float = 0.1
    max_path_length: int = 6
    enable_directed_graph: bool = True
    enable_weighted_edges: bool = True
    max_features_per_node: int = 50
    max_features_per_edge: int = 20


class FeatureExtractionSettings(BaseModel):
    """Feature extraction settings."""
    enable_temporal_features: bool = True
    enable_spatial_features: bool = True
    enable_behavioral_features: bool = True
    feature_window_size: int = 30


class FraudDetectionThresholds(BaseModel):
    """Fraud detection threshold settings."""
    min_risk_score: float = 0.3
    high_risk_threshold: float = 0.7
    critical_risk_threshold: float = 0.9
    min_ring_size: int = 3
    max_ring_size: int = 20
    min_ring_risk_score: float = 0.5


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    jwt_secret_key: str = Field(default="IfFnti/a17oa0mk7lfdFRr3c/p8MvxodfnXVj/3iqYE=", description="JWT signing secret key")
    jwt_issuer: str = Field(default="FraudDetectionAgent", description="JWT issuer")
    jwt_audience: str = Field(default="FraudDetectionAgent.Users", description="JWT audience")
    jwt_expiry_minutes: int = Field(default=60, description="JWT expiration time in minutes")
    refresh_token_expiry_days: int = Field(default=30, description="Refresh token expiration in days")
    api_key_expiry_days: int = Field(default=365, description="API key expiration in days")
    max_login_attempts: int = Field(default=5, description="Maximum login attempts")
    lockout_duration_minutes: int = Field(default=15, description="Account lockout duration")
    password_min_length: int = Field(default=8, description="Minimum password length")
    require_strong_password: bool = Field(default=True, description="Require strong passwords")
    enable_two_factor: bool = Field(default=False, description="Enable two-factor authentication")
    enable_device_tracking: bool = Field(default=True, description="Enable device tracking")
    enable_session_management: bool = Field(default=True, description="Enable session management")
    enable_audit_logging: bool = Field(default=True, description="Enable security audit logging")
    cors_allowed_origins: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed origins")
    cors_allowed_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"], description="CORS allowed methods")
    cors_allowed_headers: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed headers")
    rate_limit_requests_per_minute: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_burst_size: int = Field(default=200, description="Rate limit burst size")


class PerformanceSettings(BaseModel):
    """Performance settings."""
    max_concurrent_analyses: int = 5
    analysis_timeout_seconds: int = 300
    max_memory_usage_mb: int = 2048
    enable_caching: bool = True
    cache_expiration_minutes: int = 60


class TypeWeightSettings(BaseModel):
    """Node and edge type weight settings."""
    user_node_weight: float = 1.0
    device_node_weight: float = 0.8
    ip_node_weight: float = 0.7
    merchant_node_weight: float = 0.6
    location_node_weight: float = 0.5
    account_node_weight: float = 0.9
    uses_edge_weight: float = 1.0
    located_at_edge_weight: float = 0.8
    transacts_with_edge_weight: float = 0.9
    owns_edge_weight: float = 0.7
    associated_with_edge_weight: float = 0.6
    shares_edge_weight: float = 0.9


class TemporalAnalysisSettings(BaseModel):
    """Temporal analysis settings."""
    max_time_window_days: int = 90
    min_time_window_days: int = 1
    enable_seasonal_analysis: bool = True
    enable_trend_analysis: bool = True
    time_granularity_minutes: int = 15


class SpatialAnalysisSettings(BaseModel):
    """Spatial analysis settings."""
    max_distance_miles: float = 100.0
    enable_geofencing: bool = True
    enable_velocity_analysis: bool = True
    max_velocity_mph: float = 500.0


class BehavioralAnalysisSettings(BaseModel):
    """Behavioral analysis settings."""
    max_behavioral_patterns: int = 20
    min_behavioral_confidence: float = 0.6
    enable_anomaly_detection: bool = True
    enable_pattern_matching: bool = True


class ModelTrainingSettings(BaseModel):
    """Model training settings."""
    enable_online_learning: bool = False
    retraining_interval_hours: int = 24
    min_performance_threshold: float = 0.8
    enable_model_versioning: bool = True
    max_model_versions: int = 10
    enable_performance_monitoring: bool = True
    enable_drift_detection: bool = True
    drift_threshold: float = 0.1
    enable_alerting: bool = True
    max_alerts_per_hour: int = 100


class StorageSettings(BaseModel):
    """Storage settings."""
    graph_storage_path: str = "./Graphs/"
    model_storage_path: str = "./Models/GNN/"
    feature_storage_path: str = "./Features/"
    enable_graph_persistence: bool = True
    enable_feature_persistence: bool = True


class IntegrationSettings(BaseModel):
    """Integration settings."""
    enable_ml_service_integration: bool = True
    enable_feature_vector_integration: bool = True
    enable_data_observability_integration: bool = True
    external_gnn_endpoint: str = ""
    external_timeout_seconds: int = 30


class SecuritySettings(BaseModel):
    """Security settings."""
    enable_data_masking: bool = True
    enable_audit_logging: bool = True
    enable_access_control: bool = True
    allowed_user_roles: str = "Analyst,Lead,Admin"


class DevelopmentSettings(BaseModel):
    """Development settings."""
    enable_debug_mode: bool = False
    enable_mock_data: bool = False
    mock_data_path: str = "./MockData/"
    enable_performance_profiling: bool = False
    confidence_level: float = 0.95
    enable_automatic_detection: bool = True
    detection_interval_hours: int = 24
    enable_alerts: bool = True
    max_alerts_retention: int = 1000
    enable_dashboard_data: bool = True
    dashboard_time_range_hours: int = 168
    enable_performance_correlation: bool = True
    trend_analysis_points: int = 100
    enable_feature_specific_thresholds: bool = True
    default_analysis_time_range_hours: int = 24
    enable_statistical_testing: bool = True
    statistical_significance_threshold: float = 0.05


class GNNServiceSettings(BaseModel):
    """GNN Service configuration settings."""
    enable_gnn: bool = True
    enable_real_time_analysis: bool = True
    enable_batch_analysis: bool = True
    
    # Model settings
    model: GNNModelSettings = Field(default_factory=GNNModelSettings)
    
    # Graph construction settings
    graph_construction: GraphConstructionSettings = Field(default_factory=GraphConstructionSettings)
    
    # Feature extraction settings
    feature_extraction: FeatureExtractionSettings = Field(default_factory=FeatureExtractionSettings)
    
    # Fraud detection thresholds
    fraud_detection: FraudDetectionThresholds = Field(default_factory=FraudDetectionThresholds)
    
    # Performance settings
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    
    # Type weights
    type_weights: TypeWeightSettings = Field(default_factory=TypeWeightSettings)
    
    # Temporal analysis
    temporal_analysis: TemporalAnalysisSettings = Field(default_factory=TemporalAnalysisSettings)
    
    # Spatial analysis
    spatial_analysis: SpatialAnalysisSettings = Field(default_factory=SpatialAnalysisSettings)
    
    # Behavioral analysis
    behavioral_analysis: BehavioralAnalysisSettings = Field(default_factory=BehavioralAnalysisSettings)
    
    # Model training
    model_training: ModelTrainingSettings = Field(default_factory=ModelTrainingSettings)
    
    # Storage
    storage: StorageSettings = Field(default_factory=StorageSettings)
    
    # Integration
    integration: IntegrationSettings = Field(default_factory=IntegrationSettings)
    
    # Security
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    # Development
    development: DevelopmentSettings = Field(default_factory=DevelopmentSettings)


class MLDataPipelineSettings(BaseModel):
    """ML data pipeline configuration."""
    default_quality_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "min_completeness": 0.85,
        "min_accuracy": 0.90,
        "max_null_percentage": 0.15,
        "max_duplicate_percentage": 0.05,
        "min_data_consistency": 0.80
    })
    default_split_proportions: Dict[str, float] = Field(default_factory=lambda: {
        "training_proportion": 0.7,
        "validation_proportion": 0.15,
        "test_proportion": 0.15
    })
    feature_engineering: Dict[str, Any] = Field(default_factory=lambda: {
        "enable_automated_engineering": True,
        "max_engineered_features": 100,
        "feature_importance_threshold": 0.01,
        "enable_feature_selection": True,
        "correlation_threshold": 0.8
    })
    dataset_balancing: Dict[str, Any] = Field(default_factory=lambda: {
        "enable_automatic_balancing": True,
        "default_strategy": "Undersampling",
        "preserve_minority_class": True,
        "class_imbalance_threshold": 0.1
    })
    data_export: Dict[str, Any] = Field(default_factory=lambda: {
        "default_format": "CSV",
        "enable_compression": True,
        "default_compression_method": "GZip",
        "compression_level": 6,
        "file_retention_days": 7,
        "max_file_size_mb": 100,
        "enable_chunked_exports": True,
        "chunk_size": 10000
    })
    pipeline_execution: Dict[str, Any] = Field(default_factory=lambda: {
        "enable_monitoring": True,
        "enable_logging": True,
        "log_level": "Information",
        "enable_metrics": True,
        "metrics_collection_interval_seconds": 30,
        "enable_alerting": True,
        "pipeline_failure_threshold": 3,
        "enable_automatic_retry": True,
        "max_retry_attempts": 3,
        "retry_delay_seconds": 30
    })
    max_dataset_size: int = 1000000
    max_feature_columns: int = 1000
    pipeline_timeout_minutes: int = 120
    enable_parallel_processing: bool = True
    max_parallel_workers: int = 4
    enable_caching: bool = True
    cache_ttl_minutes: int = 60
    enable_progress_tracking: bool = True
    progress_update_interval_seconds: int = 10


class DataLineageSettings(BaseModel):
    """Data lineage configuration."""
    enable_lineage_tracking: bool = True
    max_lineage_history_per_dataset: int = 100
    lineage_retention_days: int = 365
    enable_automatic_cleanup: bool = True
    cleanup_schedule_hours: int = 24
    enable_visualization_support: bool = True
    max_visualization_depth: int = 10
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 730
    enable_checksum_validation: bool = True
    checksum_algorithm: str = "SHA256"
    enable_data_versioning: bool = True
    max_versions_per_dataset: int = 50
    enable_transformation_tracking: bool = True
    max_transformation_steps: int = 100
    enable_metadata_tracking: bool = True
    max_metadata_size_kb: int = 1024
    enable_performance_monitoring: bool = True
    performance_threshold_ms: int = 1000
    enable_data_quality_tracking: bool = True
    data_quality_threshold: float = 0.8
    enable_compliance_reporting: bool = True
    compliance_report_retention_days: int = 2555
    enable_data_governance: bool = True
    data_governance_policy_version: str = "1.0"


class FeatureVectorSettings(BaseModel):
    """Feature vector configuration."""
    enabled: bool = True
    enable_structured_features: bool = True
    default_feature_set_version: str = "1.0.0"
    max_feature_vectors_per_transaction: int = 10
    feature_vector_retention_days: int = 365
    enable_automatic_cleanup: bool = True
    cleanup_schedule_hours: int = 24
    enable_validation: bool = True
    strict_validation: bool = False
    enable_feature_importance: bool = True
    enable_drift_detection: bool = True
    drift_threshold: float = 0.1
    enable_correlation_analysis: bool = True
    correlation_threshold: float = 0.8
    enable_feature_scaling: bool = True
    scaling_method: str = "Standard"
    enable_feature_selection: bool = True
    max_features_to_select: int = 100
    feature_selection_method: str = "Variance"
    enable_feature_engineering: bool = True
    enable_time_based_features: bool = True
    time_window_sizes: List[int] = Field(default_factory=lambda: [1, 6, 12, 24, 48, 72, 168])
    enable_location_features: bool = True
    enable_device_features: bool = True
    enable_merchant_features: bool = True
    enable_user_features: bool = True
    enable_risk_features: bool = True
    enable_velocity_features: bool = True
    velocity_windows: List[int] = Field(default_factory=lambda: [1, 6, 12, 24, 48, 72, 168, 720])
    enable_anomaly_features: bool = True
    anomaly_detection_method: str = "IsolationForest"
    anomaly_contamination: float = 0.1
    enable_statistical_features: bool = True
    statistical_features: List[str] = Field(default_factory=lambda: ["Mean", "Median", "Std", "Min", "Max", "Range", "Variance"])
    enable_aggregation_features: bool = True
    aggregation_functions: List[str] = Field(default_factory=lambda: ["Sum", "Count", "Average", "Min", "Max"])
    enable_rolling_features: bool = True
    rolling_window_sizes: List[int] = Field(default_factory=lambda: [3, 5, 7, 10, 14, 30])
    enable_lag_features: bool = True
    lag_periods: List[int] = Field(default_factory=lambda: [1, 2, 3, 5, 7, 14, 30])
    enable_difference_features: bool = True
    difference_periods: List[int] = Field(default_factory=lambda: [1, 2, 3, 5, 7, 14, 30])
    enable_ratio_features: bool = True
    enable_percentage_change_features: bool = True
    enable_moving_average_features: bool = True
    moving_average_windows: List[int] = Field(default_factory=lambda: [3, 5, 7, 10, 14, 30])
    enable_exponential_moving_average_features: bool = True
    exponential_moving_average_alphas: List[float] = Field(default_factory=lambda: [0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
    enable_feature_caching: bool = True
    feature_cache_ttl_minutes: int = 60
    max_cache_size_mb: int = 1024
    enable_feature_versioning: bool = True
    max_feature_versions: int = 10
    enable_feature_migration: bool = True
    enable_feature_rollback: bool = True
    enable_feature_monitoring: bool = True
    feature_monitoring_interval_minutes: int = 15
    enable_feature_alerts: bool = True
    feature_alert_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "drift_score": 0.2,
        "anomaly_score": 0.8,
        "validation_score": 0.7,
        "correlation_score": 0.9
    })


class MLServiceSettings(BaseModel):
    """ML Service configuration."""
    enabled: bool = True
    enable_ml_models: bool = True
    enable_static_rules: bool = False
    default_model_type: str = "Ensemble"
    model_storage_path: str = "./Models"
    model_registry_path: str = "./ModelRegistry"
    max_concurrent_predictions: int = 100
    prediction_timeout_seconds: float = 5.0
    enable_model_caching: bool = True
    model_cache_size: int = 10
    model_cache_ttl_minutes: float = 60.0
    min_accuracy_threshold: float = 0.85
    min_precision_threshold: float = 0.80
    min_recall_threshold: float = 0.80
    min_f1_score_threshold: float = 0.80
    min_roc_auc_threshold: float = 0.85
    min_prc_auc_threshold: float = 0.80
    enable_ensemble_models: bool = True
    default_ensemble_method: str = "WeightedVoting"
    ensemble_voting_threshold: float = 0.5
    enable_dynamic_weighting: bool = True
    dynamic_weighting_learning_rate: float = 0.01
    dynamic_weighting_update_frequency: int = 1000
    enable_xgboost: bool = True
    xgboost_max_depth: int = 6
    xgboost_learning_rate: float = 0.1
    xgboost_n_estimators: int = 100
    xgboost_subsample: float = 0.8
    xgboost_colsample_bytree: float = 0.8
    xgboost_reg_alpha: float = 0.0
    xgboost_reg_lambda: float = 1.0
    enable_neural_networks: bool = True
    neural_network_layers: List[int] = Field(default_factory=lambda: [64, 32, 16])
    neural_network_activation: str = "ReLU"
    neural_network_output_activation: str = "Sigmoid"
    neural_network_dropout_rate: float = 0.2
    neural_network_learning_rate: float = 0.001
    neural_network_batch_size: int = 32
    neural_network_epochs: int = 100
    neural_network_early_stopping: bool = True
    neural_network_patience: int = 10
    enable_continuous_training: bool = True
    min_samples_for_retraining: int = 10000
    retraining_frequency_hours: int = 24
    data_drift_threshold: float = 0.1
    performance_drift_threshold: float = 0.05
    enable_automatic_retraining: bool = True
    max_retraining_attempts: int = 3
    enable_feature_engineering: bool = True
    enable_feature_selection: bool = True
    max_features: int = 100
    min_feature_importance: float = 0.01
    enable_feature_scaling: bool = True
    feature_scaling_method: str = "StandardScaler"
    enable_feature_normalization: bool = True
    enable_cross_validation: bool = True
    cross_validation_folds: int = 5
    enable_stratified_sampling: bool = True
    test_set_size: float = 0.2
    validation_set_size: float = 0.2
    enable_data_balancing: bool = True
    data_balancing_method: str = "SMOTE"
    enable_model_monitoring: bool = True
    monitoring_interval_minutes: int = 15
    enable_prediction_logging: bool = True
    enable_feature_logging: bool = False
    enable_performance_logging: bool = True
    log_retention_days: int = 30
    enable_ab_testing: bool = True
    ab_testing_traffic_split: float = 0.1
    ab_testing_min_samples: int = 1000
    ab_testing_confidence_level: float = 0.95
    ab_testing_duration_hours: int = 24
    enable_fallback_to_static_rules: bool = True
    enable_model_rollback: bool = True
    max_prediction_latency_ms: float = 100.0
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    enable_model_explainability: bool = True
    enable_shap_explanations: bool = True
    enable_lim_explanations: bool = True
    enable_feature_attribution: bool = True
    enable_model_audit_trail: bool = True
    audit_trail_retention_days: int = 365
    enable_feature_store_integration: bool = True
    enable_data_lineage_integration: bool = True
    enable_observability_integration: bool = True
    enable_feedback_loop_integration: bool = True
    external_ml_provider: str = "None"
    external_ml_provider_config: Dict[str, Any] = Field(default_factory=dict)


class PredictiveRiskForecastingSettings(BaseModel):
    """Predictive risk forecasting configuration."""
    enabled: bool = True
    forecast_horizon_days: int = 30
    risk_threshold: float = 0.7
    seasonal_analysis_enabled: bool = True
    early_warning_enabled: bool = True
    enable_behavioral_forecasting: bool = True
    enable_risk_trajectory_prediction: bool = True
    enable_customer_lifetime_risk: bool = True
    enable_seasonal_pattern_detection: bool = True
    enable_early_warning_system: bool = True
    min_historical_data_days: int = 30
    max_forecast_days: int = 365
    model_update_interval_hours: int = 24
    enable_model_performance_monitoring: bool = True
    model_accuracy_threshold: float = 0.85
    enable_real_time_forecasting: bool = True
    forecast_cache_expiry_minutes: int = 60


class AzureSettings(BaseModel):
    """Azure services configuration."""
    service_bus: Dict[str, str] = Field(default_factory=lambda: {
        "connection_string": "your-service-bus-connection-string",
        "fraud_alerts_queue": "fraud-alerts",
        "critical_alerts_queue": "critical-alerts"
    })
    event_hubs: Dict[str, str] = Field(default_factory=lambda: {
        "connection_string": "your-event-hubs-connection-string",
        "transaction_hub": "transactions",
        "consumer_group": "fraud-detection"
    })


class TimeSeriesBehavioralSettings(BaseModel):
    """Time series behavioral analysis configuration."""
    enable_time_series_analysis: bool = True
    enable_behavioral_analysis: bool = True
    enable_real_time_inference: bool = True
    enable_batch_analysis: bool = True
    default_model_type: str = "LSTM"
    hidden_dimensions: int = 128
    num_layers: int = 4
    learning_rate: float = 0.001
    epochs: int = 200
    dropout_rate: float = 0.3
    activation_function: str = "ReLU"
    batch_size: int = 64
    sequence_length: int = 50
    prediction_horizon: int = 10
    enable_bidirectional_lstm: bool = True
    enable_lstm_peephole: bool = False
    lstm_forget_bias: float = 1.0
    enable_lstm_stateful: bool = False
    num_attention_heads: int = 8
    attention_key_dimension: int = 64
    attention_value_dimension: int = 64
    feed_forward_dimension: int = 256
    enable_positional_encoding: bool = True
    positional_encoding_type: str = "Sinusoidal"
    max_sequence_length: int = 1000
    min_sequence_length: int = 10
    default_time_window_hours: int = 24
    max_time_window_hours: int = 720
    time_granularity_minutes: int = 15
    enable_seasonal_decomposition: bool = True
    enable_trend_analysis: bool = True
    enable_cyclical_features: bool = True
    max_behavioral_patterns: int = 50
    min_pattern_confidence: float = 0.7
    min_pattern_occurrences: int = 5
    max_pattern_length: int = 100
    enable_pattern_clustering: bool = True
    enable_anomaly_detection: bool = True
    anomaly_threshold: float = 0.8
    enable_temporal_features: bool = True
    enable_statistical_features: bool = True
    enable_frequency_features: bool = True
    enable_velocity_features: bool = True
    enable_interaction_features: bool = True
    max_features_per_pattern: int = 100
    enable_feature_selection: bool = True
    feature_selection_method: str = "MutualInformation"
    enable_velocity_analysis: bool = True
    velocity_windows_hours: int = 1
    max_velocity_threshold: float = 1000.0
    enable_velocity_anomaly_detection: bool = True
    velocity_anomaly_threshold: float = 0.9
    enable_seasonal_analysis: bool = True
    seasonal_periods: int = 24
    seasonal_window_size: int = 7
    enable_multiple_seasonality: bool = True
    max_concurrent_analyses: int = 10
    analysis_timeout_seconds: int = 300
    max_memory_usage_mb: int = 4096
    enable_caching: bool = True
    cache_expiration_minutes: int = 120
    enable_model_caching: bool = True
    model_cache_size: int = 20
    enable_online_learning: bool = False
    retraining_interval_hours: int = 24
    min_samples_for_retraining: int = 10000
    min_performance_threshold: float = 0.8
    enable_early_stopping: bool = True
    early_stopping_patience: int = 15
    enable_model_checkpointing: bool = True
    checkpoint_frequency: int = 10
    train_test_split_ratio: float = 0.8
    validation_split_ratio: float = 0.1
    enable_cross_validation: bool = True
    cross_validation_folds: int = 5
    enable_time_series_cross_validation: bool = True
    time_series_cv_folds: int = 3
    enable_performance_monitoring: bool = True
    enable_drift_detection: bool = True
    drift_threshold: float = 0.1
    enable_alerting: bool = True
    alert_threshold: float = 0.9
    monitoring_interval_minutes: int = 15
    enable_data_normalization: bool = True
    normalization_method: str = "StandardScaler"
    enable_missing_value_imputation: bool = True
    imputation_method: str = "ForwardFill"
    enable_outlier_detection: bool = True
    outlier_detection_method: str = "IQR"
    outlier_threshold: float = 3.0
    enable_model_versioning: bool = True
    max_model_versions: int = 10
    enable_ab_testing: bool = False
    ab_test_traffic_split: int = 50
    enable_canary_deployment: bool = False
    canary_traffic_percentage: int = 5
    enable_gnn_integration: bool = True
    enable_ml_service_integration: bool = True
    enable_feature_vector_integration: bool = True
    enable_real_time_messaging: bool = True
    message_queue_endpoint: str = "localhost:6379"
    enable_database_persistence: bool = True
    database_connection_string: str = "Data Source=localhost;Initial Catalog=FraudDetection;Integrated Security=true"


class GPTFineTuningSettings(BaseModel):
    """GPT fine-tuning configuration."""
    base_model: str = "gpt-4o"
    model_name_prefix: str = "fraud-detection-agent"
    training_data_path: str = "Data/Training/fraud_training_data.jsonl"
    validation_data_path: str = "Data/Training/fraud_validation_data.jsonl"
    training_epochs: int = 3
    learning_rate: float = 0.0001
    batch_size: int = 4
    max_sequence_length: int = 2048
    use_lora: bool = True
    lora_rank: int = 16
    lora_alpha: int = 32
    dropout_rate: float = 0.1
    weight_decay: float = 0.01
    warmup_steps: int = 100
    max_training_steps: int = 10000
    evaluation_frequency: int = 500
    checkpoint_frequency: int = 1000
    early_stopping_patience: int = 3
    min_improvement_threshold: float = 0.001
    enable_gradient_clipping: bool = True
    max_gradient_norm: float = 1.0
    use_mixed_precision: bool = True
    data_augmentation: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "synonym_replacement_probability": 0.1,
        "back_translation_probability": 0.05,
        "context_perturbation_probability": 0.15,
        "max_augmentation_factor": 3
    })
    model_versioning: Dict[str, Any] = Field(default_factory=lambda: {
        "versioning_scheme": "semantic",
        "auto_versioning": True,
        "version_prefix": "v",
        "maintain_version_history": True,
        "max_versions_to_keep": 10
    })
    ab_testing: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "traffic_split_percentage": 10.0,
        "min_sample_size": 1000,
        "significance_threshold": 0.05,
        "test_duration_days": 14,
        "success_metrics": [
            "fraud_detection_accuracy",
            "false_positive_rate",
            "response_time",
            "user_satisfaction"
        ]
    })


class RAGKnowledgeBaseSettings(BaseModel):
    """RAG knowledge base configuration."""
    vector_database_provider: str = "Qdrant"
    vector_database_connection_string: str = "http://localhost:6333"
    embedding_model_provider: str = "OpenAI"
    embedding_model_name: str = "text-embedding-ada-002"
    openai_api_key: str = ""
    max_chunk_size: int = 1000
    overlap_size: int = 200
    search_results_limit: int = 10
    similarity_threshold: float = 0.7
    indexing_batch_size: int = 100
    max_concurrent_indexing_jobs: int = 5
    document_retention_days: int = 365
    enable_real_time_indexing: bool = True
    enable_semantic_search: bool = True
    enable_hybrid_search: bool = True
    enable_related_concepts: bool = True
    max_related_concepts: int = 5
    enable_document_versioning: bool = True
    enable_audit_logging: bool = True
    enable_performance_monitoring: bool = True


class AdvancedAnalyticsSettings(BaseModel):
    """Advanced analytics configuration."""
    enable_real_time_dashboard: bool = True
    enable_historical_trends: bool = True
    enable_predictive_analytics: bool = True
    enable_fraud_pattern_visualization: bool = True
    enable_risk_heatmaps: bool = True
    enable_performance_benchmarking: bool = True
    enable_custom_reports: bool = True
    enable_data_export: bool = True
    dashboard_refresh_interval_seconds: int = 30
    max_real_time_data_points: int = 1000
    historical_data_retention_days: int = 365
    enable_analytics_caching: bool = True
    cache_expiration_minutes: int = 15
    enable_data_aggregation: bool = True
    aggregation_intervals_minutes: List[int] = Field(default_factory=lambda: [1, 5, 15, 60, 1440])
    enable_anomaly_detection: bool = True
    anomaly_detection_sensitivity: float = 0.7
    enable_trend_forecasting: bool = True
    forecasting_horizon_days: int = 30
    enable_comparative_analysis: bool = True
    enable_geographic_mapping: bool = True
    enable_temporal_patterns: bool = True
    enable_user_behavior_analytics: bool = True
    enable_merchant_risk_analytics: bool = True
    enable_device_analytics: bool = True
    enable_velocity_analytics: bool = True
    enable_amount_pattern_analysis: bool = True
    enable_cross_channel_analytics: bool = True
    enable_social_network_analysis: bool = True
    enable_ml_model_tracking: bool = True
    enable_ab_testing: bool = True
    enable_score_distribution_analysis: bool = True
    enable_false_positive_analysis: bool = True
    enable_cost_benefit_analysis: bool = True
    enable_compliance_reporting: bool = True
    enable_executive_dashboards: bool = True
    enable_operational_dashboards: bool = True
    enable_investigator_dashboards: bool = True
    enable_customer_service_dashboards: bool = True
    enable_risk_management_dashboards: bool = True
    enable_compliance_officer_dashboards: bool = True
    enable_board_level_reporting: bool = True
    enable_automated_reporting: bool = True
    enable_email_delivery: bool = True
    enable_webhook_delivery: bool = True
    enable_file_export: bool = True
    enable_api_delivery: bool = True
    enable_mobile_push_delivery: bool = True
    enable_sms_delivery: bool = True
    enable_slack_delivery: bool = True
    enable_teams_delivery: bool = True
    enable_whatsapp_delivery: bool = True
    enable_telegram_delivery: bool = True
    enable_discord_delivery: bool = True
    enable_custom_channel_delivery: bool = True


class ExternalIntegrationSettings(BaseModel):
    """External integration configuration."""
    enable_webhooks: bool = True
    enable_external_connections: bool = True
    enable_data_streaming: bool = True
    enable_health_monitoring: bool = True
    default_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    webhook_signature_validation: bool = True
    enable_rate_limiting: bool = True
    max_webhooks_per_minute: int = 100
    enable_webhook_retry: bool = True
    webhook_retry_delay_seconds: int = 5
    max_webhook_retries: int = 3


class ExternalSystemSettings(BaseModel):
    """External system configuration."""
    name: str
    base_url: str
    api_key: str = ""
    secret: str = ""
    is_enabled: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3


class WebhookSubscriptionSettings(BaseModel):
    """Webhook subscription configuration."""
    system_id: str
    endpoint: str
    event_types: List[str]
    is_active: bool = True
    secret: str = ""


class SerilogSettings(BaseModel):
    """Serilog logging configuration."""
    using: List[str] = Field(default_factory=lambda: ["Serilog.Sinks.Console", "Serilog.Sinks.File"])
    minimum_level: str = "Information"
    write_to: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "Name": "Console",
            "Args": {
                "outputTemplate": "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}"
            }
        },
        {
            "Name": "File",
            "Args": {
                "path": "logs/fraud-detection-.txt",
                "rollingInterval": "Day",
                "outputTemplate": "[{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} {Level:u3}] {Message:lj}{NewLine}{Exception}"
            }
        }
    ])
    enrich: List[str] = Field(default_factory=lambda: ["FromLogContext", "WithMachineName", "WithThreadId"])
    properties: Dict[str, str] = Field(default_factory=lambda: {"Application": "FraudDetectionAgent"})


class ExplainabilityServiceSettings(BaseModel):
    """Explainability service configuration."""
    enabled: bool = True
    max_features: int = 10
    cache_timeout_minutes: int = 30
    enable_shap: bool = True
    enable_rules: bool = True
    enable_counterfactuals: bool = True
    min_importance_threshold: float = 0.01
    default_time_window: str = "24h"


class OpenTelemetrySettings(BaseModel):
    """OpenTelemetry configuration."""
    service_name: str = "FraudDetectionAgent.Api"
    service_version: str = "1.0.0"
    service_namespace: str = "FraudDetection"
    tracing_enabled: bool = True
    metrics_enabled: bool = True
    console_exporter: bool = True
    jaeger_exporter: bool = True


class JaegerSettings(BaseModel):
    """Jaeger configuration."""
    endpoint: str = "http://localhost:14268/api/traces"
    agent_host: str = "localhost"
    agent_port: int = 6831


class PerformanceSettings(BaseModel):
    """Performance configuration."""
    slo: Dict[str, Any] = Field(default_factory=lambda: {
        "target_latency_ms": 200,
        "target_success_rate": 0.99,
        "monitoring_window_minutes": 60
    })
    cache: Dict[str, Any] = Field(default_factory=lambda: {
        "target_hit_rate": 0.7,
        "max_size": 1000,
        "cleanup_threshold": 100
    })
    tracing: Dict[str, Any] = Field(default_factory=lambda: {
        "sample_rate": 1.0,
        "max_span_attributes": 50,
        "max_span_events": 100
    })


class FraudDetectionAgentConfig(BaseModel):
    """Main configuration class for the Fraud Detection Agent."""
    
    # Core settings
    logging: Dict[str, Any] = Field(default_factory=lambda: {
        "log_level": {
            "default": "Information",
            "microsoft_aspnetcore": "Warning",
            "frauddetectionagent": "Debug"
        }
    })
    allowed_hosts: str = "*"
    use_mock_api: bool = True
    banking_api: Dict[str, str] = Field(default_factory=lambda: {"base_url": "https://api.axosbank.com"})
    feature_store_provider: str = "InMemory"
    secrets_provider: str = "Env"
    ai_provider: str = "openai"
    
    # Database configuration
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    connection_strings: Dict[str, str] = Field(default_factory=lambda: {"redis": "localhost:6379"})
    idempotency_provider: str = "InMemory"
    redis: Dict[str, str] = Field(default_factory=lambda: {
        "idempotency_key_prefix": "fraud:idem:",
        "idempotency_response_prefix": "fraud:idem:resp:",
        "idempotency_metrics_key": "fraud:idem:metrics"
    })
    
    # AI configuration
    azure_openai: Dict[str, Any] = Field(default_factory=lambda: {
        "endpoint": "https://your-openai-resource.openai.azure.com/",
        "api_key": "your-azure-openai-api-key",
        "deployment_name": "gpt-4o-fraud-detection",
        "use_managed_identity": False
    })
    openai: Dict[str, str] = Field(default_factory=lambda: {
        "api_key": "sk-proj-YOUR_OPENAI_API_KEY_HERE",
        "model": "gpt-4o",
        "fallback_model": "gpt-3.5-turbo"
    })
    ai: AISettings = Field(default_factory=AISettings)
    
    # Authentication
    jwt_settings: JwtSettings = Field(default_factory=JwtSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    # Core fraud detection
    fraud_detection: FraudDetectionSettings = Field(default_factory=FraudDetectionSettings)
    
    # Data quality
    data_quality: Dict[str, Any] = Field(default_factory=lambda: {
        "completeness_threshold": 0.85,
        "accuracy_threshold": 0.90,
        "required_fields": ["MerchantName", "Location", "DeviceId"],
        "enable_trend_analysis": True,
        "trend_analysis_hours": 24
    })
    
    # ML and training
    ml_model_training: MLModelTrainingSettings = Field(default_factory=MLModelTrainingSettings)
    data_observability: DataObservabilitySettings = Field(default_factory=DataObservabilitySettings)
    model_performance_monitoring: ModelPerformanceMonitoringSettings = Field(default_factory=ModelPerformanceMonitoringSettings)
    
    # Advanced features
    advanced_rules_engine: AdvancedRulesEngineSettings = Field(default_factory=AdvancedRulesEngineSettings)
    gnn_service: GNNServiceSettings = Field(default_factory=GNNServiceSettings)
    ml_data_pipeline: MLDataPipelineSettings = Field(default_factory=MLDataPipelineSettings)
    data_lineage: DataLineageSettings = Field(default_factory=DataLineageSettings)
    feature_vector: FeatureVectorSettings = Field(default_factory=FeatureVectorSettings)
    ml_service: MLServiceSettings = Field(default_factory=MLServiceSettings)
    predictive_risk_forecasting: PredictiveRiskForecastingSettings = Field(default_factory=PredictiveRiskForecastingSettings)
    
    # Azure services
    azure: AzureSettings = Field(default_factory=AzureSettings)
    
    # Advanced analytics
    time_series_behavioral: TimeSeriesBehavioralSettings = Field(default_factory=TimeSeriesBehavioralSettings)
    gpt_fine_tuning: GPTFineTuningSettings = Field(default_factory=GPTFineTuningSettings)
    rag_knowledge_base: RAGKnowledgeBaseSettings = Field(default_factory=RAGKnowledgeBaseSettings)
    advanced_analytics: AdvancedAnalyticsSettings = Field(default_factory=AdvancedAnalyticsSettings)
    
    # External integration
    external_integration: ExternalIntegrationSettings = Field(default_factory=ExternalIntegrationSettings)
    external_systems: Dict[str, ExternalSystemSettings] = Field(default_factory=lambda: {
        "sys_payment_gateway": ExternalSystemSettings(
            name="Primary Payment Gateway",
            base_url="https://api.paymentgateway.com/v1",
            api_key="key_live_1234567890abcdef",
            secret="secret_live_fedcba0987654321",
            is_enabled=True,
            timeout_seconds=45,
            retry_attempts=3
        ),
        "demo-system": ExternalSystemSettings(
            name="Demo External System",
            base_url="https://demo.external-system.com",
            is_enabled=True
        ),
        "fraud-monitoring": ExternalSystemSettings(
            name="Fraud Monitoring Service",
            base_url="https://fraud-monitoring.service.com",
            is_enabled=False,
            timeout_seconds=45,
            retry_attempts=5
        )
    })
    webhook_subscriptions: Dict[str, WebhookSubscriptionSettings] = Field(default_factory=lambda: {
        "transaction-events": WebhookSubscriptionSettings(
            system_id="demo-system",
            endpoint="https://demo.external-system.com/webhooks/transactions",
            event_types=["transaction.created", "transaction.updated", "transaction.blocked"],
            is_active=True,
            secret="webhook-secret-123"
        ),
        "fraud-alerts": WebhookSubscriptionSettings(
            system_id="fraud-monitoring",
            endpoint="https://fraud-monitoring.service.com/webhooks/alerts",
            event_types=["fraud.alert", "fraud.resolved"],
            is_active=False,
            secret="fraud-webhook-secret"
        )
    })
    
    # Logging and monitoring
    serilog: SerilogSettings = Field(default_factory=SerilogSettings)
    explainability_service: ExplainabilityServiceSettings = Field(default_factory=ExplainabilityServiceSettings)
    open_telemetry: OpenTelemetrySettings = Field(default_factory=OpenTelemetrySettings)
    jaeger: JaegerSettings = Field(default_factory=JaegerSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
