"""
Universal Fraud Detection SDK Models
Python equivalent of C# MAUI SDK models for cross-platform compatibility
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator
import json


class ConflictResolutionStrategy(str, Enum):
    """Conflict resolution strategies for offline sync"""
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    LAST_WRITE_WINS = "last_write_wins"
    MANUAL = "manual"


class LogLevel(str, Enum):
    """Log levels for SDK logging"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    is_success: bool = Field(alias="IsSuccess")
    data: Optional[Any] = Field(default=None, alias="Data")
    error_message: Optional[str] = Field(default=None, alias="ErrorMessage")
    status_code: int = Field(alias="StatusCode")
    error_code: Optional[str] = Field(default=None, alias="ErrorCode")
    error_details: Optional[Dict[str, Any]] = Field(default=None, alias="ErrorDetails")
    correlation_id: Optional[str] = Field(default=None, alias="CorrelationId")
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="Timestamp")

    @classmethod
    def success(cls, data: Any, status_code: int = 200) -> "ApiResponse":
        """Create a successful response"""
        return cls(
            IsSuccess=True,
            Data=data,
            StatusCode=status_code
        )

    @classmethod
    def failure(cls, error_message: str, status_code: int = 400, error_code: Optional[str] = None) -> "ApiResponse":
        """Create a failure response"""
        return cls(
            IsSuccess=False,
            ErrorMessage=error_message,
            StatusCode=status_code,
            ErrorCode=error_code
        )


class MobileChatRequest(BaseModel):
    """Request for fraud detection chat"""
    message: str = Field(alias="Message")
    conversation_id: Optional[str] = Field(default=None, alias="ConversationId")
    session_id: Optional[str] = Field(default=None, alias="SessionId")
    transaction_context: Optional["TransactionContext"] = Field(default=None, alias="TransactionContext")
    location: Optional["LocationInfo"] = Field(default=None, alias="Location")
    device_info: Optional["DeviceInfo"] = Field(default=None, alias="DeviceInfo")
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="Metadata")


class MobileTransactionRequest(BaseModel):
    """Request for transaction risk assessment"""
    amount: Decimal = Field(alias="Amount")
    merchant_name: str = Field(alias="MerchantName")
    location: str = Field(alias="Location")
    transaction_time: datetime = Field(default_factory=datetime.utcnow, alias="TransactionTime")
    payment_method: str = Field(alias="PaymentMethod")
    device_info: Optional["DeviceInfo"] = Field(default=None, alias="DeviceInfo")
    merchant_category: Optional[str] = Field(default=None, alias="MerchantCategory")
    transaction_type: Optional[str] = Field(default=None, alias="TransactionType")
    currency: Optional[str] = Field(default=None, alias="Currency")
    card_last_four: Optional[str] = Field(default=None, alias="CardLastFour")
    is_recurring: bool = Field(default=False, alias="IsRecurring")
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="Metadata")


class MobileCounterfactualRequest(BaseModel):
    """Request for counterfactual analysis"""
    transaction_id: str = Field(alias="TransactionId")
    target_risk_threshold: float = Field(alias="TargetRiskThreshold")
    factors: List[str] = Field(default_factory=list, alias="Factors")
    max_recommendations: int = Field(default=5, alias="MaxRecommendations")
    include_explanations: bool = Field(default=True, alias="IncludeExplanations")


class MobileFraudResponse(BaseModel):
    """Response from fraud detection API"""
    message: str = Field(alias="Message")
    risk_score: Optional[float] = Field(default=None, alias="RiskScore")
    risk_level: Optional[str] = Field(default=None, alias="RiskLevel")
    recommendations: List[str] = Field(default_factory=list, alias="Recommendations")
    conversation_id: Optional[str] = Field(default=None, alias="ConversationId")
    can_copy_share: bool = Field(default=False, alias="CanCopyShare")
    detected_patterns: Optional[List[str]] = Field(default=None, alias="DetectedPatterns")
    confidence: Optional[float] = Field(default=None, alias="Confidence")
    suggested_actions: Optional[List["SuggestedAction"]] = Field(default=None, alias="SuggestedActions")
    context: Optional[Dict[str, Any]] = Field(default=None, alias="Context")


class CounterfactualResponse(BaseModel):
    """Counterfactual analysis response"""
    original_risk_score: float = Field(alias="OriginalRiskScore")
    target_threshold: float = Field(alias="TargetThreshold")
    can_achieve_target: bool = Field(alias="CanAchieveTarget")
    best_achievable_risk_score: float = Field(alias="BestAchievableRiskScore")
    confidence_level: float = Field(alias="ConfidenceLevel")
    detailed_explanation: str = Field(alias="DetailedExplanation")
    recommendations: List["MobileRecommendation"] = Field(default_factory=list, alias="Recommendations")
    margin_to_safe: Optional[float] = Field(default=None, alias="MarginToSafe")
    most_effective_change: Optional["ParameterChange"] = Field(default=None, alias="MostEffectiveChange")


class MobileRecommendation(BaseModel):
    """Mobile-specific recommendation"""
    change: str = Field(alias="Change")
    expected_risk_score: float = Field(alias="ExpectedRiskScore")
    explanation: str = Field(alias="Explanation")
    impact_level: Optional[str] = Field(default=None, alias="ImpactLevel")
    feasibility: Optional[str] = Field(default=None, alias="Feasibility")


class ParameterChange(BaseModel):
    """Parameter change suggestion"""
    parameter_name: str = Field(alias="ParameterName")
    current_value: Optional[Any] = Field(default=None, alias="CurrentValue")
    suggested_value: Optional[Any] = Field(default=None, alias="SuggestedValue")
    explanation: str = Field(alias="Explanation")
    impact: float = Field(alias="Impact")


class SuggestedAction(BaseModel):
    """Suggested action for user"""
    action_type: str = Field(alias="ActionType")
    description: str = Field(alias="Description")
    priority: str = Field(alias="Priority")
    can_automate: bool = Field(alias="CanAutomate")
    parameters: Optional[Dict[str, Any]] = Field(default=None, alias="Parameters")


class TransactionContext(BaseModel):
    """Transaction context information"""
    amount: Decimal = Field(alias="Amount")
    merchant_name: str = Field(alias="MerchantName")
    location: str = Field(alias="Location")
    timestamp: Optional[datetime] = Field(default=None, alias="Timestamp")
    payment_method: Optional[str] = Field(default=None, alias="PaymentMethod")
    transaction_id: Optional[str] = Field(default=None, alias="TransactionId")
    currency: Optional[str] = Field(default=None, alias="Currency")


class LocationInfo(BaseModel):
    """Location information"""
    latitude: Optional[float] = Field(default=None, alias="Latitude")
    longitude: Optional[float] = Field(default=None, alias="Longitude")
    city: Optional[str] = Field(default=None, alias="City")
    state: Optional[str] = Field(default=None, alias="State")
    country: Optional[str] = Field(default=None, alias="Country")
    postal_code: Optional[str] = Field(default=None, alias="PostalCode")
    accuracy: Optional[float] = Field(default=None, alias="Accuracy")
    timestamp: Optional[datetime] = Field(default=None, alias="Timestamp")


class DeviceInfo(BaseModel):
    """Device information"""
    device_id: str = Field(alias="DeviceId")
    device_type: str = Field(alias="DeviceType")
    os_version: str = Field(alias="OsVersion")
    app_version: str = Field(alias="AppVersion")
    screen_resolution: Optional[str] = Field(default=None, alias="ScreenResolution")
    timezone: Optional[str] = Field(default=None, alias="Timezone")
    language: Optional[str] = Field(default=None, alias="Language")
    carrier: Optional[str] = Field(default=None, alias="Carrier")
    network_type: Optional[str] = Field(default=None, alias="NetworkType")
    is_jailbroken: Optional[bool] = Field(default=None, alias="IsJailbroken")
    is_emulator: Optional[bool] = Field(default=None, alias="IsEmulator")
    fingerprint: Optional[str] = Field(default=None, alias="Fingerprint")


class UserInfo(BaseModel):
    """User information"""
    user_id: str = Field(alias="UserId")
    username: str = Field(alias="Username")
    name: str = Field(alias="Name")
    email: Optional[str] = Field(default=None, alias="Email")
    roles: List[str] = Field(default_factory=list, alias="Roles")
    claims: Dict[str, str] = Field(default_factory=dict, alias="Claims")
    preferred_language: Optional[str] = Field(default=None, alias="PreferredLanguage")


class LoginRequest(BaseModel):
    """Login request"""
    username: str = Field(alias="Username")
    password: str = Field(alias="Password")
    remember_me: bool = Field(default=False, alias="RememberMe")
    device_info: Optional["DeviceInfo"] = Field(default=None, alias="DeviceInfo")


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str = Field(alias="AccessToken")
    refresh_token: str = Field(alias="RefreshToken")
    expires_in: int = Field(alias="ExpiresIn")
    token_type: str = Field(default="Bearer", alias="TokenType")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(alias="RefreshToken")


class LogoutRequest(BaseModel):
    """Logout request"""
    access_token: str = Field(alias="AccessToken")
    refresh_token: Optional[str] = Field(default=None, alias="RefreshToken")


class AuthenticationResult(BaseModel):
    """Authentication result"""
    is_success: bool = Field(alias="IsSuccess")
    token_response: Optional["TokenResponse"] = Field(default=None, alias="TokenResponse")
    error_message: Optional[str] = Field(default=None, alias="ErrorMessage")
    error_code: Optional[str] = Field(default=None, alias="ErrorCode")


class FraudFeedback(BaseModel):
    """Fraud feedback"""
    transaction_id: str = Field(alias="TransactionId")
    user_id: str = Field(alias="UserId")
    label: str = Field(alias="Label")  # "true_positive", "false_positive", "true_negative", "false_negative"
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="Timestamp")
    comments: Optional[str] = Field(default=None, alias="Comments")
    confidence: Optional[float] = Field(default=None, alias="Confidence")


class FraudHistoryRequest(BaseModel):
    """Fraud history request"""
    start_date: Optional[datetime] = Field(default=None, alias="StartDate")
    end_date: Optional[datetime] = Field(default=None, alias="EndDate")
    max_items: Optional[int] = Field(default=None, alias="MaxItems")
    page: Optional[int] = Field(default=None, alias="Page")
    risk_level_filter: Optional[str] = Field(default=None, alias="RiskLevelFilter")
    transaction_type_filter: Optional[str] = Field(default=None, alias="TransactionTypeFilter")


class FraudHistoryResponse(BaseModel):
    """Fraud history response"""
    transactions: List["FraudHistoryItem"] = Field(default_factory=list, alias="Transactions")
    total_count: int = Field(alias="TotalCount")
    page: int = Field(alias="Page")
    page_size: int = Field(alias="PageSize")
    has_more: bool = Field(alias="HasMore")


class FraudHistoryItem(BaseModel):
    """Fraud history item"""
    transaction_id: str = Field(alias="TransactionId")
    timestamp: datetime = Field(alias="Timestamp")
    amount: Decimal = Field(alias="Amount")
    merchant_name: str = Field(alias="MerchantName")
    risk_score: float = Field(alias="RiskScore")
    risk_level: str = Field(alias="RiskLevel")
    status: str = Field(alias="Status")
    fraud_patterns: List[str] = Field(default_factory=list, alias="FraudPatterns")


class UserPreferences(BaseModel):
    """User preferences"""
    user_id: str = Field(alias="UserId")
    notifications_enabled: bool = Field(default=True, alias="NotificationsEnabled")
    risk_threshold: float = Field(default=0.7, alias="RiskThreshold")
    preferred_language: str = Field(default="en", alias="PreferredLanguage")
    timezone: str = Field(default="UTC", alias="Timezone")
    biometric_auth_enabled: bool = Field(default=False, alias="BiometricAuthEnabled")
    auto_logout_minutes: int = Field(default=30, alias="AutoLogoutMinutes")


class HealthStatus(BaseModel):
    """Health status"""
    status: str = Field(alias="Status")
    version: str = Field(alias="Version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="Timestamp")
    services: Dict[str, str] = Field(default_factory=dict, alias="Services")


class FraudAnalysisRequest(BaseModel):
    """Request details captured for fraud analysis"""
    request_id: str = Field(alias="RequestId")
    method: str = Field(alias="Method")
    url: str = Field(alias="Url")
    headers: Dict[str, str] = Field(alias="Headers")
    body: Optional[str] = Field(default=None, alias="Body")
    timestamp: datetime = Field(default_factory=datetime.utcnow, alias="Timestamp")
    user_agent: Optional[str] = Field(default=None, alias="UserAgent")
    content_type: Optional[str] = Field(default=None, alias="ContentType")


class FraudRiskAnalysis(BaseModel):
    """Result of fraud risk analysis"""
    request_id: str = Field(alias="RequestId")
    risk_score: float = Field(alias="RiskScore")
    recommended_action: str = Field(alias="RecommendedAction")
    should_block: bool = Field(alias="ShouldBlock")
    block_reason: Optional[str] = Field(default=None, alias="BlockReason")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, alias="AnalysisTimestamp")


class ApiResponseEventArgs(BaseModel):
    """API response event arguments"""
    endpoint: str = Field(alias="Endpoint")
    status_code: int = Field(alias="StatusCode")
    response_time: float = Field(alias="ResponseTime")
    is_success: bool = Field(alias="IsSuccess")


class ApiErrorEventArgs(BaseModel):
    """API error event arguments"""
    endpoint: str = Field(alias="Endpoint")
    error_message: str = Field(alias="ErrorMessage")
    status_code: int = Field(alias="StatusCode")
    is_retryable: bool = Field(alias="IsRetryable")
    exception: Optional[Exception] = Field(default=None, alias="Exception")


class AuthenticationStateChangedEventArgs(BaseModel):
    """Authentication state changed event arguments"""
    is_authenticated: bool = Field(alias="IsAuthenticated")
    user_info: Optional["UserInfo"] = Field(default=None, alias="UserInfo")
    reason: str = Field(alias="Reason")


class TokenExpiringEventArgs(BaseModel):
    """Token expiring event arguments"""
    expires_at: datetime = Field(alias="ExpiresAt")
    time_remaining: float = Field(alias="TimeRemaining")
    should_auto_refresh: bool = Field(alias="ShouldAutoRefresh")


# Configuration Models
class FraudDetectionSdkOptions(BaseModel):
    """Main configuration options for the Fraud Detection SDK"""
    base_url: str = Field(alias="BaseUrl")
    api_key: Optional[str] = Field(default=None, alias="ApiKey")
    timeout: float = Field(default=30.0, alias="Timeout")
    retry_policy: "RetryPolicyOptions" = Field(default_factory=lambda: RetryPolicyOptions(), alias="RetryPolicy")
    offline_sync: "OfflineSyncOptions" = Field(default_factory=lambda: OfflineSyncOptions(), alias="OfflineSync")
    security: "SecurityOptions" = Field(default_factory=lambda: SecurityOptions(), alias="Security")
    logging: "LoggingOptions" = Field(default_factory=lambda: LoggingOptions(), alias="Logging")
    caching: "CachingOptions" = Field(default_factory=lambda: CachingOptions(), alias="Caching")
    feature_flags: "FeatureFlagOptions" = Field(default_factory=lambda: FeatureFlagOptions(), alias="FeatureFlags")
    environment: str = Field(default="Production", alias="Environment")
    application_name: Optional[str] = Field(default=None, alias="ApplicationName")
    application_version: Optional[str] = Field(default=None, alias="ApplicationVersion")

    @validator('base_url')
    def validate_base_url(cls, v):
        if not v:
            raise ValueError('BaseUrl is required')
        return v

    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v


class RetryPolicyOptions(BaseModel):
    """Retry policy configuration"""
    max_retries: int = Field(default=3, alias="MaxRetries")
    base_delay: float = Field(default=1.0, alias="BaseDelay")
    max_delay: float = Field(default=60.0, alias="MaxDelay")
    backoff_multiplier: float = Field(default=2.0, alias="BackoffMultiplier")
    use_jitter: bool = Field(default=True, alias="UseJitter")
    retryable_status_codes: List[int] = Field(default=[408, 429, 500, 502, 503, 504], alias="RetryableStatusCodes")
    retryable_exceptions: List[str] = Field(default=["HttpRequestException", "TaskCanceledException", "SocketException"], alias="RetryableExceptions")

    @validator('max_retries')
    def validate_max_retries(cls, v):
        if v < 0 or v > 10:
            raise ValueError('MaxRetries must be between 0 and 10')
        return v

    @validator('base_delay')
    def validate_base_delay(cls, v):
        if v <= 0:
            raise ValueError('BaseDelay must be positive')
        return v

    @validator('backoff_multiplier')
    def validate_backoff_multiplier(cls, v):
        if v < 1.0 or v > 10.0:
            raise ValueError('BackoffMultiplier must be between 1.0 and 10.0')
        return v


class OfflineSyncOptions(BaseModel):
    """Offline synchronization configuration"""
    enabled: bool = Field(default=True, alias="Enabled")
    sync_interval: float = Field(default=300.0, alias="SyncInterval")  # 5 minutes
    max_queue_size: int = Field(default=1000, alias="MaxQueueSize")
    max_retries: int = Field(default=3, alias="MaxRetries")
    max_item_age: float = Field(default=604800.0, alias="MaxItemAge")  # 7 days
    conflict_resolution: ConflictResolutionStrategy = Field(default=ConflictResolutionStrategy.SERVER_WINS, alias="ConflictResolution")
    sync_over_cellular: bool = Field(default=True, alias="SyncOverCellular")
    sync_only_when_charging: bool = Field(default=False, alias="SyncOnlyWhenCharging")
    batch_size: int = Field(default=50, alias="BatchSize")
    compress_data: bool = Field(default=True, alias="CompressData")

    @validator('sync_interval')
    def validate_sync_interval(cls, v):
        if v <= 0:
            raise ValueError('SyncInterval must be positive')
        return v

    @validator('max_queue_size')
    def validate_max_queue_size(cls, v):
        if v <= 0 or v > 10000:
            raise ValueError('MaxQueueSize must be between 1 and 10000')
        return v

    @validator('max_retries')
    def validate_max_retries(cls, v):
        if v < 0 or v > 10:
            raise ValueError('MaxRetries must be between 0 and 10')
        return v

    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0 or v > 1000:
            raise ValueError('BatchSize must be between 1 and 1000')
        return v


class SecurityOptions(BaseModel):
    """Security configuration options"""
    enable_certificate_pinning: bool = Field(default=False, alias="EnableCertificatePinning")
    certificate_pins: List[str] = Field(default_factory=list, alias="CertificatePins")
    enable_token_refresh: bool = Field(default=True, alias="EnableTokenRefresh")
    token_refresh_threshold: float = Field(default=300.0, alias="TokenRefreshThreshold")  # 5 minutes
    enable_biometric_authentication: bool = Field(default=False, alias="EnableBiometricAuthentication")
    biometric_prompt: str = Field(default="Authenticate to access fraud detection", alias="BiometricPrompt")
    validate_ssl_certificates: bool = Field(default=True, alias="ValidateSslCertificates")
    minimum_tls_version: str = Field(default="1.2", alias="MinimumTlsVersion")

    @validator('enable_certificate_pinning')
    def validate_certificate_pinning(cls, v, values):
        if v and (not values.get('certificate_pins') or len(values.get('certificate_pins', [])) == 0):
            raise ValueError('Certificate pins are required when certificate pinning is enabled')
        return v

    @validator('enable_token_refresh')
    def validate_token_refresh(cls, v, values):
        if v and values.get('token_refresh_threshold', 0) <= 0:
            raise ValueError('TokenRefreshThreshold must be positive when token refresh is enabled')
        return v


class LoggingOptions(BaseModel):
    """Logging configuration options"""
    enable_logging: bool = Field(default=True, alias="EnableLogging")
    log_level: LogLevel = Field(default=LogLevel.INFO, alias="LogLevel")
    enable_pii_redaction: bool = Field(default=True, alias="EnablePiiRedaction")
    max_log_file_size: int = Field(default=10485760, alias="MaxLogFileSize")  # 10MB
    max_log_files: int = Field(default=5, alias="MaxLogFiles")
    log_file_path: Optional[str] = Field(default=None, alias="LogFilePath")
    log_to_console: bool = Field(default=True, alias="LogToConsole")
    log_to_file: bool = Field(default=False, alias="LogToFile")

    @validator('max_log_file_size')
    def validate_max_log_file_size(cls, v):
        if v <= 0:
            raise ValueError('MaxLogFileSize must be positive')
        return v

    @validator('max_log_files')
    def validate_max_log_files(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('MaxLogFiles must be between 1 and 100')
        return v


class CachingOptions(BaseModel):
    """Caching configuration options"""
    enable_caching: bool = Field(default=True, alias="EnableCaching")
    default_expiration: float = Field(default=1800.0, alias="DefaultExpiration")  # 30 minutes
    max_cache_size: int = Field(default=52428800, alias="MaxCacheSize")  # 50MB
    cleanup_interval: float = Field(default=600.0, alias="CleanupInterval")  # 10 minutes
    compress_cached_data: bool = Field(default=True, alias="CompressCachedData")
    encrypt_cached_data: bool = Field(default=False, alias="EncryptCachedData")

    @validator('default_expiration')
    def validate_default_expiration(cls, v):
        if v <= 0:
            raise ValueError('DefaultExpiration must be positive')
        return v

    @validator('max_cache_size')
    def validate_max_cache_size(cls, v):
        if v <= 0:
            raise ValueError('MaxCacheSize must be positive')
        return v

    @validator('cleanup_interval')
    def validate_cleanup_interval(cls, v):
        if v <= 0:
            raise ValueError('CleanupInterval must be positive')
        return v


class FeatureFlagOptions(BaseModel):
    """Feature flag configuration"""
    enable_offline_mode: bool = Field(default=True, alias="EnableOfflineMode")
    enable_biometric_auth: bool = Field(default=False, alias="EnableBiometricAuth")
    enable_detailed_logging: bool = Field(default=False, alias="EnableDetailedLogging")
    enable_analytics: bool = Field(default=True, alias="EnableAnalytics")
    enable_crash_reporting: bool = Field(default=True, alias="EnableCrashReporting")
    enable_experimental_features: bool = Field(default=False, alias="EnableExperimentalFeatures")
    custom_flags: Dict[str, bool] = Field(default_factory=dict, alias="CustomFlags")


class FraudInterceptorOptions(BaseModel):
    """Configuration options for the fraud detection interceptor"""
    exclude_url_patterns: List[str] = Field(default_factory=list, alias="ExcludeUrlPatterns")
    exclude_methods: List[str] = Field(default=["OPTIONS", "HEAD"], alias="ExcludeMethods")
    block_threshold: float = Field(default=0.8, alias="BlockThreshold")
    analyze_request_bodies: bool = Field(default=True, alias="AnalyzeRequestBodies")
    analyze_response_bodies: bool = Field(default=False, alias="AnalyzeResponseBodies")
    max_body_size: int = Field(default=1048576, alias="MaxBodySize")  # 1MB


# Update forward references
MobileChatRequest.model_rebuild()
MobileTransactionRequest.model_rebuild()
MobileCounterfactualRequest.model_rebuild()
MobileFraudResponse.model_rebuild()
CounterfactualResponse.model_rebuild()
MobileRecommendation.model_rebuild()
ParameterChange.model_rebuild()
SuggestedAction.model_rebuild()
TransactionContext.model_rebuild()
LocationInfo.model_rebuild()
DeviceInfo.model_rebuild()
UserInfo.model_rebuild()
LoginRequest.model_rebuild()
TokenResponse.model_rebuild()
RefreshTokenRequest.model_rebuild()
LogoutRequest.model_rebuild()
AuthenticationResult.model_rebuild()
FraudFeedback.model_rebuild()
FraudHistoryRequest.model_rebuild()
FraudHistoryResponse.model_rebuild()
FraudHistoryItem.model_rebuild()
UserPreferences.model_rebuild()
HealthStatus.model_rebuild()
FraudAnalysisRequest.model_rebuild()
FraudRiskAnalysis.model_rebuild()
ApiResponseEventArgs.model_rebuild()
ApiErrorEventArgs.model_rebuild()
AuthenticationStateChangedEventArgs.model_rebuild()
TokenExpiringEventArgs.model_rebuild()
FraudDetectionSdkOptions.model_rebuild()
RetryPolicyOptions.model_rebuild()
OfflineSyncOptions.model_rebuild()
SecurityOptions.model_rebuild()
LoggingOptions.model_rebuild()
CachingOptions.model_rebuild()
FeatureFlagOptions.model_rebuild()
FraudInterceptorOptions.model_rebuild()
