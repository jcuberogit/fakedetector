"""
Universal Fraud Detection SDK
Python implementation of the fraud detection SDK for cross-platform compatibility
"""

from .models import *
from .interfaces import *
from .client import FraudDetectionApiClient, MockFraudDetectionApiClient
from .authentication import AuthenticationHandler, MockAuthenticationHandler
from .storage import SecureStorageService, MockStorageService, InMemoryStorageService
from .interceptor import FraudDetectionInterceptor, MockFraudDetectionInterceptor, UniversalHttpInterceptor
from .sdk import FraudDetectionSdk, FraudDetectionSdkBuilder

__version__ = "1.0.0"
__author__ = "ParadigmStore Team"

__all__ = [
    # Main SDK
    "FraudDetectionSdk",
    "FraudDetectionSdkBuilder",
    
    # API Client
    "FraudDetectionApiClient",
    "MockFraudDetectionApiClient",
    
    # Authentication
    "AuthenticationHandler",
    "MockAuthenticationHandler",
    
    # Storage
    "SecureStorageService",
    "MockStorageService",
    "InMemoryStorageService",
    
    # HTTP Interceptor
    "FraudDetectionInterceptor",
    "MockFraudDetectionInterceptor",
    "UniversalHttpInterceptor",
    
    # Models
    "ApiResponse",
    "MobileChatRequest",
    "MobileTransactionRequest",
    "MobileCounterfactualRequest",
    "MobileFraudResponse",
    "CounterfactualResponse",
    "MobileRecommendation",
    "ParameterChange",
    "SuggestedAction",
    "TransactionContext",
    "LocationInfo",
    "DeviceInfo",
    "UserInfo",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "LogoutRequest",
    "AuthenticationResult",
    "FraudFeedback",
    "FraudHistoryRequest",
    "FraudHistoryResponse",
    "FraudHistoryItem",
    "UserPreferences",
    "HealthStatus",
    "FraudAnalysisRequest",
    "FraudRiskAnalysis",
    "ApiResponseEventArgs",
    "ApiErrorEventArgs",
    "AuthenticationStateChangedEventArgs",
    "TokenExpiringEventArgs",
    "FraudDetectionSdkOptions",
    "RetryPolicyOptions",
    "OfflineSyncOptions",
    "SecurityOptions",
    "LoggingOptions",
    "CachingOptions",
    "FeatureFlagOptions",
    "FraudInterceptorOptions",
    
    # Enums
    "ConflictResolutionStrategy",
    "LogLevel",
    
    # Interfaces
    "IApiClient",
    "IAuthenticationHandler",
    "IStorage",
    "IConnectivityService",
    "ISyncService",
    "INotificationService",
    "IHttpInterceptor",
    "IAnalyticsService",
    "ICacheService",
    "ILogger",
    "IDeviceService",
    "IBiometricService"
]
