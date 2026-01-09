"""
Model Performance Monitoring Models for Fraud Detection Agent

This module contains Pydantic models for model performance monitoring and analysis,
mirroring the C# ModelPerformanceMonitoringModels.cs functionality.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(str, Enum):
    """Alert types"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    ANOMALY = "anomaly"
    SYSTEM_ERROR = "system_error"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    MODEL_FAILURE = "model_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_ISSUE = "security_issue"
    COMPLIANCE_VIOLATION = "compliance_violation"
    CUSTOM = "custom"


class DriftType(str, Enum):
    """Drift types"""
    FEATURE_DRIFT = "feature_drift"
    LABEL_DRIFT = "label_drift"
    CONCEPT_DRIFT = "concept_drift"
    DATA_QUALITY_DRIFT = "data_quality_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    DISTRIBUTION_DRIFT = "distribution_drift"


class DriftSeverity(str, Enum):
    """Drift severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    CYCLICAL = "cyclical"
    VOLATILE = "volatile"


class AnomalyType(str, Enum):
    """Anomaly types"""
    POINT_ANOMALY = "point_anomaly"
    CONTEXTUAL_ANOMALY = "contextual_anomaly"
    COLLECTIVE_ANOMALY = "collective_anomaly"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    TREND_ANOMALY = "trend_anomaly"


class AnomalyImpact(str, Enum):
    """Anomaly impact levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportType(str, Enum):
    """Report types"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    """Export formats"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    EXCEL = "excel"
    PDF = "pdf"
    HTML = "html"


class ExportScope(str, Enum):
    """Export scopes"""
    SINGLE_MODEL = "single_model"
    MULTIPLE_MODELS = "multiple_models"
    ALL_MODELS = "all_models"
    CUSTOM = "custom"


class ExportStatus(str, Enum):
    """Export status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EnhancedModelPerformance(BaseModel):
    """Enhanced model performance metrics with comprehensive monitoring capabilities"""
    model_id: str = Field(default="", description="Model ID")
    model_version: str = Field(default="", description="Model version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    
    # Core Metrics
    accuracy: Decimal = Field(default=Decimal('0.0'), description="Accuracy")
    precision: Decimal = Field(default=Decimal('0.0'), description="Precision")
    recall: Decimal = Field(default=Decimal('0.0'), description="Recall")
    f1_score: Decimal = Field(default=Decimal('0.0'), description="F1 Score")
    roc_auc: Decimal = Field(default=Decimal('0.0'), description="ROC AUC")
    prc_auc: Decimal = Field(default=Decimal('0.0'), description="PRC AUC")
    
    # Detailed Metrics
    true_positive_rate: Decimal = Field(default=Decimal('0.0'), description="True Positive Rate")
    false_positive_rate: Decimal = Field(default=Decimal('0.0'), description="False Positive Rate")
    true_negative_rate: Decimal = Field(default=Decimal('0.0'), description="True Negative Rate")
    false_negative_rate: Decimal = Field(default=Decimal('0.0'), description="False Negative Rate")
    
    # Advanced Metrics
    matthews_correlation_coefficient: Decimal = Field(default=Decimal('0.0'), description="Matthews Correlation Coefficient")
    cohen_kappa: Decimal = Field(default=Decimal('0.0'), description="Cohen Kappa")
    log_loss: Decimal = Field(default=Decimal('0.0'), description="Log Loss")
    hamming_loss: Decimal = Field(default=Decimal('0.0'), description="Hamming Loss")
    
    # Performance Indicators
    inference_latency_ms: Decimal = Field(default=Decimal('0.0'), description="Inference Latency (ms)")
    throughput_per_second: Decimal = Field(default=Decimal('0.0'), description="Throughput per Second")
    memory_usage_mb: Decimal = Field(default=Decimal('0.0'), description="Memory Usage (MB)")
    cpu_usage_percent: Decimal = Field(default=Decimal('0.0'), description="CPU Usage (%)")
    
    # Metadata
    class_metrics: Dict[str, Decimal] = Field(default_factory=dict, description="Class-specific metrics")
    feature_importance: Dict[str, Decimal] = Field(default_factory=dict, description="Feature importance")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, description="Custom metrics")
    
    # Sample Information
    training_samples: int = Field(default=0, description="Training samples")
    validation_samples: int = Field(default=0, description="Validation samples")
    test_samples: int = Field(default=0, description="Test samples")
    production_samples: int = Field(default=0, description="Production samples")


class PerformanceAlert(BaseModel):
    """Performance monitoring alert with severity and actionable information"""
    alert_id: str = Field(default="", description="Alert ID")
    model_id: str = Field(default="", description="Model ID")
    severity: AlertSeverity = Field(default=AlertSeverity.INFO, description="Alert severity")
    type: AlertType = Field(default=AlertType.CUSTOM, description="Alert type")
    title: str = Field(default="", description="Alert title")
    description: str = Field(default="", description="Alert description")
    recommendation: str = Field(default="", description="Recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    acknowledged_at: Optional[datetime] = Field(default=None, description="Acknowledgment timestamp")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")
    acknowledged_by: str = Field(default="", description="Acknowledged by")
    resolved_by: str = Field(default="", description="Resolved by")
    alert_data: Dict[str, Any] = Field(default_factory=dict, description="Alert data")
    affected_metrics: List[str] = Field(default_factory=list, description="Affected metrics")
    is_active: bool = Field(default=True, description="Is active")


class PerformanceDriftResult(BaseModel):
    """Performance drift detection result with detailed analysis"""
    model_id: str = Field(default="", description="Model ID")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")
    drift_type: DriftType = Field(default=DriftType.FEATURE_DRIFT, description="Drift type")
    severity: DriftSeverity = Field(default=DriftSeverity.NONE, description="Drift severity")
    drift_score: Decimal = Field(default=Decimal('0.0'), description="Drift score")
    confidence_level: Decimal = Field(default=Decimal('0.0'), description="Confidence level")
    
    # Drift Analysis
    feature_drift_scores: Dict[str, Decimal] = Field(default_factory=dict, description="Feature drift scores")
    metric_drift_scores: Dict[str, Decimal] = Field(default_factory=dict, description="Metric drift scores")
    drifted_features: List[str] = Field(default_factory=list, description="Drifted features")
    drifted_metrics: List[str] = Field(default_factory=list, description="Drifted metrics")
    
    # Statistical Measures
    kolmogorov_smirnov_statistic: Decimal = Field(default=Decimal('0.0'), description="Kolmogorov-Smirnov statistic")
    chi_square_statistic: Decimal = Field(default=Decimal('0.0'), description="Chi-square statistic")
    wasserstein_distance: Decimal = Field(default=Decimal('0.0'), description="Wasserstein distance")
    jensen_shannon_divergence: Decimal = Field(default=Decimal('0.0'), description="Jensen-Shannon divergence")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    requires_retraining: bool = Field(default=False, description="Requires retraining")
    retraining_reason: str = Field(default="", description="Retraining reason")
    estimated_retraining_date: Optional[datetime] = Field(default=None, description="Estimated retraining date")


class PerformanceTrendPoint(BaseModel):
    """Performance trend data point"""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    value: Decimal = Field(default=Decimal('0.0'), description="Value")
    confidence_lower: Optional[Decimal] = Field(default=None, description="Lower confidence bound")
    confidence_upper: Optional[Decimal] = Field(default=None, description="Upper confidence bound")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")


class PerformanceDashboardData(BaseModel):
    """Real-time performance monitoring dashboard data"""
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    active_models: List[EnhancedModelPerformance] = Field(default_factory=list, description="Active models")
    active_alerts: List[PerformanceAlert] = Field(default_factory=list, description="Active alerts")
    recent_drifts: List[PerformanceDriftResult] = Field(default_factory=list, description="Recent drifts")
    
    # Summary Statistics
    total_models: int = Field(default=0, description="Total models")
    models_with_alerts: int = Field(default=0, description="Models with alerts")
    models_with_drift: int = Field(default=0, description="Models with drift")
    models_requiring_retraining: int = Field(default=0, description="Models requiring retraining")
    
    # Performance Trends
    accuracy_trend: List[PerformanceTrendPoint] = Field(default_factory=list, description="Accuracy trend")
    latency_trend: List[PerformanceTrendPoint] = Field(default_factory=list, description="Latency trend")
    throughput_trend: List[PerformanceTrendPoint] = Field(default_factory=list, description="Throughput trend")
    
    # System Health
    overall_system_health: Decimal = Field(default=Decimal('0.0'), description="Overall system health")
    system_warnings: List[str] = Field(default_factory=list, description="System warnings")
    system_errors: List[str] = Field(default_factory=list, description="System errors")


class PerformanceAnomaly(BaseModel):
    """Performance anomaly detection result"""
    anomaly_id: str = Field(default="", description="Anomaly ID")
    model_id: str = Field(default="", description="Model ID")
    metric_name: str = Field(default="", description="Metric name")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")
    type: AnomalyType = Field(default=AnomalyType.POINT_ANOMALY, description="Anomaly type")
    anomaly_score: Decimal = Field(default=Decimal('0.0'), description="Anomaly score")
    severity: Decimal = Field(default=Decimal('0.0'), description="Severity")
    
    # Anomaly Details
    expected_value: Decimal = Field(default=Decimal('0.0'), description="Expected value")
    actual_value: Decimal = Field(default=Decimal('0.0'), description="Actual value")
    deviation: Decimal = Field(default=Decimal('0.0'), description="Deviation")
    deviation_percent: Decimal = Field(default=Decimal('0.0'), description="Deviation percentage")
    
    # Context
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    contributing_factors: List[str] = Field(default_factory=list, description="Contributing factors")
    root_cause: str = Field(default="", description="Root cause")
    
    # Impact Assessment
    impact: AnomalyImpact = Field(default=AnomalyImpact.NONE, description="Impact level")
    affected_services: List[str] = Field(default_factory=list, description="Affected services")
    estimated_cost: Decimal = Field(default=Decimal('0.0'), description="Estimated cost")
    estimated_resolution_time_hours: float = Field(default=0.0, description="Estimated resolution time (hours)")


class PerformanceTrendAnalysis(BaseModel):
    """Performance trend analysis with forecasting capabilities"""
    model_id: str = Field(default="", description="Model ID")
    metric_name: str = Field(default="", description="Metric name")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")
    analysis_window_hours: float = Field(default=24.0, description="Analysis window (hours)")
    
    # Historical Data
    historical_data: List[PerformanceTrendPoint] = Field(default_factory=list, description="Historical data")
    forecasted_data: List[PerformanceTrendPoint] = Field(default_factory=list, description="Forecasted data")
    
    # Trend Analysis
    direction: TrendDirection = Field(default=TrendDirection.STABLE, description="Trend direction")
    trend_strength: Decimal = Field(default=Decimal('0.0'), description="Trend strength")
    trend_slope: Decimal = Field(default=Decimal('0.0'), description="Trend slope")
    trend_intercept: Decimal = Field(default=Decimal('0.0'), description="Trend intercept")
    r_squared: Decimal = Field(default=Decimal('0.0'), description="R-squared")
    
    # Seasonality
    has_seasonality: bool = Field(default=False, description="Has seasonality")
    seasonality_strength: Decimal = Field(default=Decimal('0.0'), description="Seasonality strength")
    seasonality_period_hours: float = Field(default=24.0, description="Seasonality period (hours)")
    
    # Anomalies
    detected_anomalies: List[PerformanceAnomaly] = Field(default_factory=list, description="Detected anomalies")
    change_points: List[datetime] = Field(default_factory=list, description="Change points")
    
    # Predictions
    next_value_prediction: Decimal = Field(default=Decimal('0.0'), description="Next value prediction")
    prediction_confidence: Decimal = Field(default=Decimal('0.0'), description="Prediction confidence")
    prediction_interval_lower: Decimal = Field(default=Decimal('0.0'), description="Lower prediction interval")
    prediction_interval_upper: Decimal = Field(default=Decimal('0.0'), description="Upper prediction interval")


class PerformanceReport(BaseModel):
    """Comprehensive performance report with executive summary and detailed analysis"""
    report_id: str = Field(default="", description="Report ID")
    report_title: str = Field(default="", description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    report_period_hours: float = Field(default=24.0, description="Report period (hours)")
    type: ReportType = Field(default=ReportType.OPERATIONAL, description="Report type")
    
    # Executive Summary
    executive_summary: str = Field(default="", description="Executive summary")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    key_recommendations: List[str] = Field(default_factory=list, description="Key recommendations")
    overall_performance_score: Decimal = Field(default=Decimal('0.0'), description="Overall performance score")
    
    # Detailed Analysis
    model_performances: List[EnhancedModelPerformance] = Field(default_factory=list, description="Model performances")
    alerts: List[PerformanceAlert] = Field(default_factory=list, description="Alerts")
    drift_results: List[PerformanceDriftResult] = Field(default_factory=list, description="Drift results")
    anomalies: List[PerformanceAnomaly] = Field(default_factory=list, description="Anomalies")
    
    # Trends and Patterns
    trend_analyses: List[PerformanceTrendAnalysis] = Field(default_factory=list, description="Trend analyses")
    performance_patterns: Dict[str, Any] = Field(default_factory=dict, description="Performance patterns")
    insights: List[str] = Field(default_factory=list, description="Insights")
    
    # Metadata
    report_metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    data_sources: List[str] = Field(default_factory=list, description="Data sources")
    generated_by: str = Field(default="", description="Generated by")
    report_format: str = Field(default="", description="Report format")


class PerformanceExportRequest(BaseModel):
    """Performance data export configuration and result"""
    export_id: str = Field(default="", description="Export ID")
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    format: ExportFormat = Field(default=ExportFormat.JSON, description="Export format")
    scope: ExportScope = Field(default=ExportScope.ALL_MODELS, description="Export scope")
    
    # Data Selection
    model_ids: List[str] = Field(default_factory=list, description="Model IDs")
    metrics: List[str] = Field(default_factory=list, description="Metrics")
    start_date: Optional[datetime] = Field(default=None, description="Start date")
    end_date: Optional[datetime] = Field(default=None, description="End date")
    time_granularity_hours: Optional[float] = Field(default=None, description="Time granularity (hours)")
    
    # Export Options
    include_metadata: bool = Field(default=True, description="Include metadata")
    include_charts: bool = Field(default=False, description="Include charts")
    include_raw_data: bool = Field(default=True, description="Include raw data")
    include_analysis: bool = Field(default=True, description="Include analysis")
    
    # Delivery
    email_recipients: str = Field(default="", description="Email recipients")
    webhook_endpoint: str = Field(default="", description="Webhook endpoint")
    storage_location: str = Field(default="", description="Storage location")


class PerformanceExportResult(BaseModel):
    """Performance export result with download information"""
    export_id: str = Field(default="", description="Export ID")
    status: ExportStatus = Field(default=ExportStatus.PENDING, description="Export status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    processing_time_seconds: Optional[float] = Field(default=None, description="Processing time (seconds)")
    
    # Export Details
    format: ExportFormat = Field(default=ExportFormat.JSON, description="Export format")
    file_name: str = Field(default="", description="File name")
    file_path: str = Field(default="", description="File path")
    file_size_bytes: int = Field(default=0, description="File size (bytes)")
    download_url: str = Field(default="", description="Download URL")
    
    # Content Summary
    models_exported: int = Field(default=0, description="Models exported")
    metrics_exported: int = Field(default=0, description="Metrics exported")
    data_points_exported: int = Field(default=0, description="Data points exported")
    data_start_date: Optional[datetime] = Field(default=None, description="Data start date")
    data_end_date: Optional[datetime] = Field(default=None, description="Data end date")
    
    # Metadata
    export_metadata: Dict[str, Any] = Field(default_factory=dict, description="Export metadata")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    errors: List[str] = Field(default_factory=list, description="Errors")
