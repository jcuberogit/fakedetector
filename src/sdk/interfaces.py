"""
Universal Fraud Detection SDK Interfaces
Python equivalent of C# MAUI SDK interfaces for cross-platform compatibility
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from .models import (
    ApiResponse, MobileChatRequest, MobileFraudResponse, MobileTransactionRequest,
    MobileCounterfactualRequest, CounterfactualResponse, FraudFeedback,
    FraudHistoryRequest, FraudHistoryResponse, UserPreferences, HealthStatus,
    AuthenticationResult, LoginRequest, TokenResponse, UserInfo
)


class IApiClient(ABC):
    """Interface for API client operations"""
    
    @abstractmethod
    async def chat_async(self, request: MobileChatRequest) -> ApiResponse[MobileFraudResponse]:
        """Send chat message for fraud analysis"""
        pass
    
    @abstractmethod
    async def check_transaction_risk_async(self, request: MobileTransactionRequest) -> ApiResponse[MobileFraudResponse]:
        """Check transaction risk"""
        pass
    
    @abstractmethod
    async def get_counterfactual_analysis_async(self, request: MobileCounterfactualRequest) -> ApiResponse[CounterfactualResponse]:
        """Get counterfactual analysis for transaction"""
        pass
    
    @abstractmethod
    async def submit_feedback_async(self, feedback: FraudFeedback) -> ApiResponse[bool]:
        """Submit user feedback on fraud detection"""
        pass
    
    @abstractmethod
    async def get_fraud_history_async(self, request: FraudHistoryRequest) -> ApiResponse[FraudHistoryResponse]:
        """Get user's fraud history"""
        pass
    
    @abstractmethod
    async def update_user_preferences_async(self, preferences: UserPreferences) -> ApiResponse[bool]:
        """Update user preferences"""
        pass
    
    @abstractmethod
    async def get_health_async(self) -> ApiResponse[HealthStatus]:
        """Get API health status"""
        pass


class IAuthenticationHandler(ABC):
    """Interface for authentication operations"""
    
    @abstractmethod
    async def login_async(self, login_request: LoginRequest) -> AuthenticationResult:
        """Authenticate user with credentials"""
        pass
    
    @abstractmethod
    async def refresh_token_async(self) -> AuthenticationResult:
        """Refresh access token using refresh token"""
        pass
    
    @abstractmethod
    async def logout_async(self) -> bool:
        """Logout and revoke tokens"""
        pass
    
    @abstractmethod
    async def is_authenticated_async(self) -> bool:
        """Check if user is currently authenticated"""
        pass
    
    @abstractmethod
    async def get_current_user_async(self) -> Optional[UserInfo]:
        """Get current user information from token"""
        pass
    
    @abstractmethod
    async def get_current_user_id_async(self) -> Optional[str]:
        """Get current user ID from token"""
        pass
    
    @abstractmethod
    async def get_access_token_async(self) -> Optional[str]:
        """Get current access token"""
        pass
    
    @abstractmethod
    def validate_token(self, token: Optional[str]) -> bool:
        """Validate a JWT token"""
        pass


class IStorage(ABC):
    """Interface for secure storage operations"""
    
    @abstractmethod
    async def set_async(self, key: str, value: str) -> None:
        """Store a value securely"""
        pass
    
    @abstractmethod
    async def get_async(self, key: str) -> Optional[str]:
        """Retrieve a value from secure storage"""
        pass
    
    @abstractmethod
    async def remove_async(self, key: str) -> bool:
        """Remove a value from secure storage"""
        pass
    
    @abstractmethod
    async def remove_all_async(self) -> None:
        """Remove all values from secure storage"""
        pass
    
    @abstractmethod
    async def has_key_async(self, key: str) -> bool:
        """Check if a key exists in secure storage"""
        pass
    
    @abstractmethod
    async def get_all_keys_async(self) -> List[str]:
        """Get all keys in secure storage"""
        pass
    
    @abstractmethod
    async def set_token_async(self, token_type: str, token: str) -> None:
        """Store authentication token"""
        pass
    
    @abstractmethod
    async def get_token_async(self, token_type: str) -> Optional[str]:
        """Retrieve authentication token"""
        pass
    
    @abstractmethod
    async def remove_token_async(self, token_type: str) -> bool:
        """Remove authentication token"""
        pass
    
    @abstractmethod
    async def set_user_info_async(self, user_info: UserInfo) -> None:
        """Store user information"""
        pass
    
    @abstractmethod
    async def get_user_info_async(self) -> Optional[UserInfo]:
        """Retrieve user information"""
        pass
    
    @abstractmethod
    async def set_device_info_async(self, device_info: Any) -> None:
        """Store device information"""
        pass
    
    @abstractmethod
    async def get_device_info_async(self) -> Optional[Any]:
        """Retrieve device information"""
        pass


class IConnectivityService(ABC):
    """Interface for connectivity operations"""
    
    @abstractmethod
    async def is_connected_async(self) -> bool:
        """Check if device is connected to network"""
        pass
    
    @abstractmethod
    async def get_connection_type_async(self) -> str:
        """Get current connection type (wifi, cellular, etc.)"""
        pass
    
    @abstractmethod
    async def is_cellular_data_enabled_async(self) -> bool:
        """Check if cellular data is enabled"""
        pass
    
    @abstractmethod
    async def is_wifi_enabled_async(self) -> bool:
        """Check if WiFi is enabled"""
        pass


class ISyncService(ABC):
    """Interface for offline synchronization operations"""
    
    @abstractmethod
    async def start_auto_sync_async(self) -> None:
        """Start automatic synchronization"""
        pass
    
    @abstractmethod
    async def stop_auto_sync_async(self) -> None:
        """Stop automatic synchronization"""
        pass
    
    @abstractmethod
    async def sync_now_async(self) -> bool:
        """Perform immediate synchronization"""
        pass
    
    @abstractmethod
    async def queue_item_async(self, item: Dict[str, Any]) -> None:
        """Queue an item for synchronization"""
        pass
    
    @abstractmethod
    async def get_queue_status_async(self) -> Dict[str, Any]:
        """Get synchronization queue status"""
        pass
    
    @abstractmethod
    async def clear_queue_async(self) -> None:
        """Clear synchronization queue"""
        pass


class INotificationService(ABC):
    """Interface for notification operations"""
    
    @abstractmethod
    async def send_notification_async(self, title: str, message: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send a notification"""
        pass
    
    @abstractmethod
    async def schedule_notification_async(self, title: str, message: str, delay_seconds: int, data: Optional[Dict[str, Any]] = None) -> str:
        """Schedule a notification"""
        pass
    
    @abstractmethod
    async def cancel_notification_async(self, notification_id: str) -> bool:
        """Cancel a scheduled notification"""
        pass
    
    @abstractmethod
    async def is_notification_enabled_async(self) -> bool:
        """Check if notifications are enabled"""
        pass
    
    @abstractmethod
    async def request_permission_async(self) -> bool:
        """Request notification permission"""
        pass


class IHttpInterceptor(ABC):
    """Interface for HTTP request interception"""
    
    @abstractmethod
    async def intercept_request_async(self, method: str, url: str, headers: Dict[str, str], body: Optional[str] = None) -> Dict[str, Any]:
        """Intercept and analyze HTTP request"""
        pass
    
    @abstractmethod
    async def intercept_response_async(self, request_id: str, status_code: int, headers: Dict[str, str], body: Optional[str] = None) -> None:
        """Intercept and analyze HTTP response"""
        pass
    
    @abstractmethod
    def should_intercept(self, url: str, method: str) -> bool:
        """Determine if request should be intercepted"""
        pass


class IAnalyticsService(ABC):
    """Interface for analytics operations"""
    
    @abstractmethod
    async def track_event_async(self, event_name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Track an analytics event"""
        pass
    
    @abstractmethod
    async def track_page_view_async(self, page_name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Track a page view"""
        pass
    
    @abstractmethod
    async def track_exception_async(self, exception: Exception, properties: Optional[Dict[str, Any]] = None) -> None:
        """Track an exception"""
        pass
    
    @abstractmethod
    async def set_user_properties_async(self, properties: Dict[str, Any]) -> None:
        """Set user properties for analytics"""
        pass
    
    @abstractmethod
    async def flush_async(self) -> None:
        """Flush analytics data"""
        pass


class ICacheService(ABC):
    """Interface for caching operations"""
    
    @abstractmethod
    async def get_async(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set_async(self, key: str, value: Any, expiration_seconds: Optional[int] = None) -> None:
        """Set value in cache"""
        pass
    
    @abstractmethod
    async def remove_async(self, key: str) -> bool:
        """Remove value from cache"""
        pass
    
    @abstractmethod
    async def clear_async(self) -> None:
        """Clear all cache"""
        pass
    
    @abstractmethod
    async def get_size_async(self) -> int:
        """Get cache size"""
        pass
    
    @abstractmethod
    async def cleanup_async(self) -> None:
        """Cleanup expired cache entries"""
        pass


class ILogger(ABC):
    """Interface for logging operations"""
    
    @abstractmethod
    def log_trace(self, message: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log trace message"""
        pass
    
    @abstractmethod
    def log_debug(self, message: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message"""
        pass
    
    @abstractmethod
    def log_info(self, message: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def log_warning(self, message: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def log_error(self, message: str, exception: Optional[Exception] = None, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def log_critical(self, message: str, exception: Optional[Exception] = None, properties: Optional[Dict[str, Any]] = None) -> None:
        """Log critical message"""
        pass


class IDeviceService(ABC):
    """Interface for device operations"""
    
    @abstractmethod
    async def get_device_info_async(self) -> Dict[str, Any]:
        """Get device information"""
        pass
    
    @abstractmethod
    async def get_device_id_async(self) -> str:
        """Get unique device ID"""
        pass
    
    @abstractmethod
    async def is_jailbroken_async(self) -> bool:
        """Check if device is jailbroken/rooted"""
        pass
    
    @abstractmethod
    async def is_emulator_async(self) -> bool:
        """Check if running on emulator"""
        pass
    
    @abstractmethod
    async def get_app_version_async(self) -> str:
        """Get application version"""
        pass
    
    @abstractmethod
    async def get_os_version_async(self) -> str:
        """Get operating system version"""
        pass


class IBiometricService(ABC):
    """Interface for biometric authentication operations"""
    
    @abstractmethod
    async def is_available_async(self) -> bool:
        """Check if biometric authentication is available"""
        pass
    
    @abstractmethod
    async def authenticate_async(self, prompt: str) -> bool:
        """Perform biometric authentication"""
        pass
    
    @abstractmethod
    async def get_biometric_type_async(self) -> str:
        """Get available biometric type (fingerprint, face, etc.)"""
        pass
    
    @abstractmethod
    async def is_enrolled_async(self) -> bool:
        """Check if biometric is enrolled"""
        pass
