"""
Feature Vector Models for Fraud Detection Agent

This module contains Pydantic models for feature vector management and ML model input,
mirroring the C# FeatureVectorModels.cs functionality.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FeatureVectorStatus(str, Enum):
    """Feature vector status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ERROR = "error"
    PROCESSING = "processing"
    ARCHIVED = "archived"


class FeatureDataType(str, Enum):
    """Feature data types"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    TIME_SERIES = "time_series"
    TEXT = "text"
    DATETIME = "datetime"
    OBJECT = "object"
    ARRAY = "array"


class FeatureImportance(str, Enum):
    """Feature importance levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class FeatureSource(str, Enum):
    """Feature source systems"""
    TRANSACTION = "transaction"
    USER = "user"
    DEVICE = "device"
    LOCATION = "location"
    MERCHANT = "merchant"
    RISK = "risk"
    ML = "ml"
    EXTERNAL = "external"
    CALCULATED = "calculated"
    DERIVED = "derived"


class NumericFeatures(BaseModel):
    """Numeric features for continuous values"""
    amount: Decimal = Field(default=Decimal('0.0'), description="Transaction amount")
    user_account_balance: Decimal = Field(default=Decimal('0.0'), description="User account balance")
    daily_transaction_limit: Decimal = Field(default=Decimal('0.0'), description="Daily transaction limit")
    velocity_1_hour: Decimal = Field(default=Decimal('0.0'), description="1-hour velocity")
    velocity_24_hours: Decimal = Field(default=Decimal('0.0'), description="24-hour velocity")
    velocity_7_days: Decimal = Field(default=Decimal('0.0'), description="7-day velocity")
    velocity_30_days: Decimal = Field(default=Decimal('0.0'), description="30-day velocity")
    device_trust_score: Decimal = Field(default=Decimal('0.0'), description="Device trust score")
    ip_risk_score: Decimal = Field(default=Decimal('0.0'), description="IP risk score")
    merchant_risk_score: Decimal = Field(default=Decimal('0.0'), description="Merchant risk score")
    location_risk_score: Decimal = Field(default=Decimal('0.0'), description="Location risk score")
    user_risk_score: Decimal = Field(default=Decimal('0.0'), description="User risk score")
    time_of_day: Decimal = Field(default=Decimal('0.0'), description="Time of day (0-23)")
    day_of_week: Decimal = Field(default=Decimal('0.0'), description="Day of week (0-6)")
    month_of_year: Decimal = Field(default=Decimal('0.0'), description="Month of year (1-12)")
    distance_from_home: Decimal = Field(default=Decimal('0.0'), description="Distance from home")
    distance_from_work: Decimal = Field(default=Decimal('0.0'), description="Distance from work")
    transaction_frequency: Decimal = Field(default=Decimal('0.0'), description="Transaction frequency")
    average_transaction_amount: Decimal = Field(default=Decimal('0.0'), description="Average transaction amount")
    max_transaction_amount: Decimal = Field(default=Decimal('0.0'), description="Maximum transaction amount")
    min_transaction_amount: Decimal = Field(default=Decimal('0.0'), description="Minimum transaction amount")
    amount_variance: Decimal = Field(default=Decimal('0.0'), description="Amount variance")
    location_variance: Decimal = Field(default=Decimal('0.0'), description="Location variance")
    time_variance: Decimal = Field(default=Decimal('0.0'), description="Time variance")
    device_variance: Decimal = Field(default=Decimal('0.0'), description="Device variance")
    merchant_variance: Decimal = Field(default=Decimal('0.0'), description="Merchant variance")
    risk_factor_aggregate: Decimal = Field(default=Decimal('0.0'), description="Risk factor aggregate")
    confidence_score: Decimal = Field(default=Decimal('0.0'), description="Confidence score")
    anomaly_score: Decimal = Field(default=Decimal('0.0'), description="Anomaly score")
    drift_score: Decimal = Field(default=Decimal('0.0'), description="Drift score")


class CategoricalFeatures(BaseModel):
    """Categorical features for discrete values"""
    transaction_type: str = Field(default="", description="Transaction type")
    merchant_category: str = Field(default="", description="Merchant category")
    merchant_name: str = Field(default="", description="Merchant name")
    device_type: str = Field(default="", description="Device type")
    device_os: str = Field(default="", description="Device operating system")
    device_browser: str = Field(default="", description="Device browser")
    location_country: str = Field(default="", description="Location country")
    location_state: str = Field(default="", description="Location state")
    location_city: str = Field(default="", description="Location city")
    location_zip_code: str = Field(default="", description="Location zip code")
    payment_method: str = Field(default="", description="Payment method")
    card_type: str = Field(default="", description="Card type")
    card_network: str = Field(default="", description="Card network")
    user_segment: str = Field(default="", description="User segment")
    account_type: str = Field(default="", description="Account type")
    risk_level: str = Field(default="", description="Risk level")
    fraud_pattern: str = Field(default="", description="Fraud pattern")
    alert_type: str = Field(default="", description="Alert type")
    decision: str = Field(default="", description="Decision")
    investigation_status: str = Field(default="", description="Investigation status")
    analyst_assignment: str = Field(default="", description="Analyst assignment")
    priority: str = Field(default="", description="Priority")
    source_system: str = Field(default="", description="Source system")
    data_quality: str = Field(default="", description="Data quality")
    compliance_status: str = Field(default="", description="Compliance status")


class BinaryFeatures(BaseModel):
    """Binary features for boolean values"""
    is_new_device: bool = Field(default=False, description="Is new device")
    is_new_location: bool = Field(default=False, description="Is new location")
    is_new_merchant: bool = Field(default=False, description="Is new merchant")
    is_high_risk_time: bool = Field(default=False, description="Is high risk time")
    is_weekend: bool = Field(default=False, description="Is weekend")
    is_holiday: bool = Field(default=False, description="Is holiday")
    is_business_hours: bool = Field(default=False, description="Is business hours")
    is_first_time_merchant: bool = Field(default=False, description="Is first time merchant")
    is_first_time_location: bool = Field(default=False, description="Is first time location")
    is_first_time_amount: bool = Field(default=False, description="Is first time amount")
    is_velocity_exceeded: bool = Field(default=False, description="Is velocity exceeded")
    is_amount_anomaly: bool = Field(default=False, description="Is amount anomaly")
    is_time_anomaly: bool = Field(default=False, description="Is time anomaly")
    is_location_anomaly: bool = Field(default=False, description="Is location anomaly")
    is_device_anomaly: bool = Field(default=False, description="Is device anomaly")
    is_merchant_anomaly: bool = Field(default=False, description="Is merchant anomaly")
    is_user_anomaly: bool = Field(default=False, description="Is user anomaly")
    is_proxy_detected: bool = Field(default=False, description="Is proxy detected")
    is_vpn_detected: bool = Field(default=False, description="Is VPN detected")
    is_tor_detected: bool = Field(default=False, description="Is Tor detected")
    is_device_compromised: bool = Field(default=False, description="Is device compromised")
    is_account_locked: bool = Field(default=False, description="Is account locked")
    is_card_blocked: bool = Field(default=False, description="Is card blocked")
    is_fraud_alert: bool = Field(default=False, description="Is fraud alert")
    is_investigation_required: bool = Field(default=False, description="Is investigation required")
    is_escalation_required: bool = Field(default=False, description="Is escalation required")
    is_manual_review: bool = Field(default=False, description="Is manual review")
    is_auto_approved: bool = Field(default=False, description="Is auto approved")
    is_auto_declined: bool = Field(default=False, description="Is auto declined")
    is_step_up_required: bool = Field(default=False, description="Is step up required")
    is_trusted_entity: bool = Field(default=False, description="Is trusted entity")
    is_blacklisted_entity: bool = Field(default=False, description="Is blacklisted entity")
    is_whitelisted_entity: bool = Field(default=False, description="Is whitelisted entity")


class TimeSeriesFeatures(BaseModel):
    """Time series features for temporal patterns"""
    hourly_transaction_counts: List[Decimal] = Field(default_factory=list, description="Hourly transaction counts")
    daily_transaction_counts: List[Decimal] = Field(default_factory=list, description="Daily transaction counts")
    weekly_transaction_counts: List[Decimal] = Field(default_factory=list, description="Weekly transaction counts")
    monthly_transaction_counts: List[Decimal] = Field(default_factory=list, description="Monthly transaction counts")
    hourly_amounts: List[Decimal] = Field(default_factory=list, description="Hourly amounts")
    daily_amounts: List[Decimal] = Field(default_factory=list, description="Daily amounts")
    weekly_amounts: List[Decimal] = Field(default_factory=list, description="Weekly amounts")
    monthly_amounts: List[Decimal] = Field(default_factory=list, description="Monthly amounts")
    location_changes: List[Decimal] = Field(default_factory=list, description="Location changes")
    device_changes: List[Decimal] = Field(default_factory=list, description="Device changes")
    merchant_changes: List[Decimal] = Field(default_factory=list, description="Merchant changes")
    risk_score_trends: List[Decimal] = Field(default_factory=list, description="Risk score trends")
    anomaly_score_trends: List[Decimal] = Field(default_factory=list, description="Anomaly score trends")
    velocity_trends: List[Decimal] = Field(default_factory=list, description="Velocity trends")
    pattern_similarity_scores: List[Decimal] = Field(default_factory=list, description="Pattern similarity scores")
    seasonal_adjustments: List[Decimal] = Field(default_factory=list, description="Seasonal adjustments")
    trend_components: List[Decimal] = Field(default_factory=list, description="Trend components")
    cyclical_components: List[Decimal] = Field(default_factory=list, description="Cyclical components")
    residual_components: List[Decimal] = Field(default_factory=list, description="Residual components")
    forecast_values: List[Decimal] = Field(default_factory=list, description="Forecast values")
    confidence_intervals: List[Decimal] = Field(default_factory=list, description="Confidence intervals")
    prediction_intervals: List[Decimal] = Field(default_factory=list, description="Prediction intervals")


class FeatureVector(BaseModel):
    """Represents a structured feature vector for ML model input"""
    id: str = Field(default="", description="Unique identifier")
    transaction_id: str = Field(default="", description="Transaction ID")
    user_id: str = Field(default="", description="User ID")
    feature_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feature timestamp")
    feature_set_version: str = Field(default="", description="Feature set version")
    numeric_features: NumericFeatures = Field(default_factory=NumericFeatures, description="Numeric features")
    categorical_features: CategoricalFeatures = Field(default_factory=CategoricalFeatures, description="Categorical features")
    binary_features: BinaryFeatures = Field(default_factory=BinaryFeatures, description="Binary features")
    time_series_features: TimeSeriesFeatures = Field(default_factory=TimeSeriesFeatures, description="Time series features")
    extended_metadata: Dict[str, Any] = Field(default_factory=dict, description="Extended metadata")
    status: FeatureVectorStatus = Field(default=FeatureVectorStatus.DRAFT, description="Feature vector status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(default="", description="Created by")
    source: str = Field(default="", description="Source system")


class FeatureSetVersion(BaseModel):
    """Feature set version information"""
    version: str = Field(default="", description="Version number")
    description: str = Field(default="", description="Version description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    created_by: str = Field(default="", description="Created by")
    features: List[str] = Field(default_factory=list, description="List of features")
    feature_descriptions: Dict[str, str] = Field(default_factory=dict, description="Feature descriptions")
    feature_types: Dict[str, str] = Field(default_factory=dict, description="Feature types")
    default_values: Dict[str, Any] = Field(default_factory=dict, description="Default values")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="Validation rules")
    is_active: bool = Field(default=True, description="Is active version")
    is_deprecated: bool = Field(default=False, description="Is deprecated")
    deprecation_reason: str = Field(default="", description="Deprecation reason")
    deprecated_at: Optional[datetime] = Field(default=None, description="Deprecation timestamp")
    migration_path: str = Field(default="", description="Migration path")


class FeatureVectorMetadata(BaseModel):
    """Feature vector metadata and tracking"""
    id: str = Field(default="", description="Metadata ID")
    feature_vector_id: str = Field(default="", description="Feature vector ID")
    key: str = Field(default="", description="Metadata key")
    value: str = Field(default="", description="Metadata value")
    data_type: str = Field(default="", description="Data type")
    source: str = Field(default="", description="Source")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(default="", description="Created by")
    is_required: bool = Field(default=False, description="Is required")
    is_sensitive: bool = Field(default=False, description="Is sensitive")
    validation_rule: str = Field(default="", description="Validation rule")
    description: str = Field(default="", description="Description")


class FeatureVectorValidationResult(BaseModel):
    """Feature vector validation result"""
    is_valid: bool = Field(default=False, description="Is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    field_errors: Dict[str, str] = Field(default_factory=dict, description="Field-specific errors")
    field_warnings: Dict[str, str] = Field(default_factory=dict, description="Field-specific warnings")
    total_errors: int = Field(default=0, description="Total number of errors")
    total_warnings: int = Field(default=0, description="Total number of warnings")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")
    validated_by: str = Field(default="", description="Validated by")
    validation_rule: str = Field(default="", description="Validation rule used")
    validation_score: Decimal = Field(default=Decimal('0.0'), description="Validation score")


# Request/Response Models

class CreateFeatureVectorRequest(BaseModel):
    """Request to create a new feature vector"""
    transaction_id: str = Field(description="Transaction ID")
    user_id: str = Field(description="User ID")
    numeric_features: Optional[NumericFeatures] = Field(default=None, description="Numeric features")
    categorical_features: Optional[CategoricalFeatures] = Field(default=None, description="Categorical features")
    binary_features: Optional[BinaryFeatures] = Field(default=None, description="Binary features")
    time_series_features: Optional[TimeSeriesFeatures] = Field(default=None, description="Time series features")
    extended_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")
    source: str = Field(default="", description="Source system")


class CreateFeatureVectorResponse(BaseModel):
    """Response for feature vector creation"""
    success: bool = Field(description="Whether creation was successful")
    message: str = Field(default="", description="Response message")
    feature_vector_id: str = Field(default="", description="Created feature vector ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    validation_result: FeatureVectorValidationResult = Field(default_factory=FeatureVectorValidationResult, description="Validation result")


class UpdateFeatureVectorRequest(BaseModel):
    """Request to update a feature vector"""
    feature_vector_id: str = Field(description="Feature vector ID to update")
    numeric_features: Optional[NumericFeatures] = Field(default=None, description="Numeric features")
    categorical_features: Optional[CategoricalFeatures] = Field(default=None, description="Categorical features")
    binary_features: Optional[BinaryFeatures] = Field(default=None, description="Binary features")
    time_series_features: Optional[TimeSeriesFeatures] = Field(default=None, description="Time series features")
    extended_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Extended metadata")
    source: Optional[str] = Field(default=None, description="Source system")


class QueryFeatureVectorsRequest(BaseModel):
    """Request to query feature vectors"""
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID filter")
    user_id: Optional[str] = Field(default=None, description="User ID filter")
    from_date: Optional[datetime] = Field(default=None, description="From date filter")
    to_date: Optional[datetime] = Field(default=None, description="To date filter")
    status: Optional[FeatureVectorStatus] = Field(default=None, description="Status filter")
    feature_set_version: Optional[str] = Field(default=None, description="Feature set version filter")
    source: Optional[str] = Field(default=None, description="Source filter")
    max_results: int = Field(default=100, description="Maximum results to return")
    offset: int = Field(default=0, description="Offset for pagination")


class QueryFeatureVectorsResponse(BaseModel):
    """Response for feature vector queries"""
    feature_vectors: List[FeatureVector] = Field(default_factory=list, description="Feature vectors")
    total_count: int = Field(default=0, description="Total count")
    returned_count: int = Field(default=0, description="Returned count")
    offset: int = Field(default=0, description="Offset used")
    has_more: bool = Field(default=False, description="Has more results")


class ValidateFeatureVectorRequest(BaseModel):
    """Request to validate a feature vector"""
    feature_vector: FeatureVector = Field(description="Feature vector to validate")
    validation_rule: str = Field(default="", description="Validation rule")
    strict_validation: bool = Field(default=False, description="Strict validation mode")


class MigrateFeatureVectorsRequest(BaseModel):
    """Request to migrate feature vectors"""
    from_version: str = Field(description="Source version")
    to_version: str = Field(description="Target version")
    feature_vector_ids: List[str] = Field(default_factory=list, description="Feature vector IDs to migrate")
    dry_run: bool = Field(default=True, description="Dry run mode")
    validate_after_migration: bool = Field(default=True, description="Validate after migration")


class MigrateFeatureVectorsResponse(BaseModel):
    """Response for feature vector migration"""
    success: bool = Field(description="Whether migration was successful")
    message: str = Field(default="", description="Response message")
    total_processed: int = Field(default=0, description="Total processed")
    successfully_migrated: int = Field(default=0, description="Successfully migrated")
    failed_to_migrate: int = Field(default=0, description="Failed to migrate")
    migration_errors: List[str] = Field(default_factory=list, description="Migration errors")
    migration_warnings: List[str] = Field(default_factory=list, description="Migration warnings")
    completed_at: datetime = Field(default_factory=datetime.utcnow, description="Completion timestamp")
    completed_by: str = Field(default="", description="Completed by")
