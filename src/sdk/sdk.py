"""
Universal Fraud Detection SDK
Main SDK service that orchestrates all components
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import (
    FraudDetectionSdkOptions, MobileChatRequest, MobileFraudResponse,
    MobileTransactionRequest, MobileCounterfactualRequest, CounterfactualResponse,
    FraudFeedback, FraudHistoryRequest, FraudHistoryResponse, UserPreferences,
    HealthStatus, LoginRequest, AuthenticationResult, UserInfo, DeviceInfo
)
from .interfaces import (
    IApiClient, IAuthenticationHandler, IStorage, IConnectivityService,
    ISyncService, INotificationService, IHttpInterceptor, IAnalyticsService,
    ICacheService, ILogger, IDeviceService, IBiometricService
)
from .client import FraudDetectionApiClient, MockFraudDetectionApiClient
from .authentication import AuthenticationHandler, MockAuthenticationHandler
from .storage import SecureStorageService, MockStorageService, InMemoryStorageService
from .interceptor import FraudDetectionInterceptor, MockFraudDetectionInterceptor


class FraudDetectionSdk:
    """Main Fraud Detection SDK service"""
    
    def __init__(
        self,
        options: FraudDetectionSdkOptions,
        logger: Optional[logging.Logger] = None
    ):
        self.options = options
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize core services
        self._storage = self._create_storage_service()
        self._auth_handler = self._create_auth_handler()
        self._api_client = self._create_api_client()
        self._interceptor = self._create_interceptor()
        
        # Optional services (can be None if not implemented)
        self._connectivity_service: Optional[IConnectivityService] = None
        self._sync_service: Optional[ISyncService] = None
        self._notification_service: Optional[INotificationService] = None
        self._analytics_service: Optional[IAnalyticsService] = None
        self._cache_service: Optional[ICacheService] = None
        self._device_service: Optional[IDeviceService] = None
        self._biometric_service: Optional[IBiometricService] = None
        
        self._initialized = False
        self._disposed = False
    
    def _create_storage_service(self) -> IStorage:
        """Create storage service based on options"""
        if self.options.environment.lower() == "test":
            return MockStorageService(self.logger)
        elif self.options.environment.lower() == "development":
            return InMemoryStorageService(self.logger)
        else:
            return SecureStorageService(logger=self.logger)
    
    def _create_auth_handler(self) -> IAuthenticationHandler:
        """Create authentication handler"""
        if self.options.environment.lower() == "test":
            return MockAuthenticationHandler(self.logger)
        else:
            return AuthenticationHandler(
                storage=self._storage,
                base_url=self.options.base_url,
                logger=self.logger
            )
    
    def _create_api_client(self) -> IApiClient:
        """Create API client"""
        if self.options.environment.lower() == "test":
            return MockFraudDetectionApiClient(self.logger)
        else:
            return FraudDetectionApiClient(
                options=self.options,
                auth_handler=self._auth_handler,
                logger=self.logger
            )
    
    def _create_interceptor(self) -> IHttpInterceptor:
        """Create HTTP interceptor"""
        if self.options.environment.lower() == "test":
            return MockFraudDetectionInterceptor(self.logger)
        else:
            return FraudDetectionInterceptor(
                options=self.options,
                auth_handler=self._auth_handler,
                logger=self.logger
            )
    
    async def initialize(self) -> None:
        """Initialize the SDK"""
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing Fraud Detection SDK")
            
            # Initialize API client
            if hasattr(self._api_client, 'initialize'):
                await self._api_client.initialize()
            
            # Start auto-sync if configured and available
            if self._sync_service and self.options.offline_sync.enabled:
                await self._sync_service.start_auto_sync_async()
            
            self._initialized = True
            self.logger.info("Fraud Detection SDK initialized successfully")
        
        except Exception as ex:
            self.logger.error(f"Failed to initialize Fraud Detection SDK: {ex}")
            raise
    
    async def dispose(self) -> None:
        """Dispose of resources"""
        if self._disposed:
            return
        
        try:
            self.logger.info("Disposing Fraud Detection SDK")
            
            # Dispose API client
            if hasattr(self._api_client, 'dispose'):
                await self._api_client.dispose()
            
            # Stop sync service
            if self._sync_service:
                await self._sync_service.stop_auto_sync_async()
            
            self._disposed = True
            self.logger.info("Fraud Detection SDK disposed successfully")
        
        except Exception as ex:
            self.logger.error(f"Error disposing Fraud Detection SDK: {ex}")
    
    # Authentication methods
    async def login_async(self, login_request: LoginRequest) -> AuthenticationResult:
        """Authenticate user with credentials"""
        return await self._auth_handler.login_async(login_request)
    
    async def logout_async(self) -> bool:
        """Logout and revoke tokens"""
        return await self._auth_handler.logout_async()
    
    async def is_authenticated_async(self) -> bool:
        """Check if user is currently authenticated"""
        return await self._auth_handler.is_authenticated_async()
    
    async def get_current_user_async(self) -> Optional[UserInfo]:
        """Get current user information"""
        return await self._auth_handler.get_current_user_async()
    
    async def get_current_user_id_async(self) -> Optional[str]:
        """Get current user ID"""
        return await self._auth_handler.get_current_user_id_async()
    
    # API methods
    async def chat_async(self, request: MobileChatRequest) -> MobileFraudResponse:
        """Send chat message for fraud analysis"""
        response = await self._api_client.chat_async(request)
        if response.is_success:
            return MobileFraudResponse.parse_obj(response.data)
        else:
            raise Exception(f"Chat request failed: {response.error_message}")
    
    async def check_transaction_risk_async(self, request: MobileTransactionRequest) -> MobileFraudResponse:
        """Check transaction risk"""
        response = await self._api_client.check_transaction_risk_async(request)
        if response.is_success:
            return MobileFraudResponse.parse_obj(response.data)
        else:
            raise Exception(f"Transaction risk check failed: {response.error_message}")
    
    async def get_counterfactual_analysis_async(self, request: MobileCounterfactualRequest) -> CounterfactualResponse:
        """Get counterfactual analysis for transaction"""
        response = await self._api_client.get_counterfactual_analysis_async(request)
        if response.is_success:
            return CounterfactualResponse.parse_obj(response.data)
        else:
            raise Exception(f"Counterfactual analysis failed: {response.error_message}")
    
    async def submit_feedback_async(self, feedback: FraudFeedback) -> bool:
        """Submit user feedback on fraud detection"""
        response = await self._api_client.submit_feedback_async(feedback)
        if response.is_success:
            return response.data
        else:
            raise Exception(f"Feedback submission failed: {response.error_message}")
    
    async def get_fraud_history_async(self, request: FraudHistoryRequest) -> FraudHistoryResponse:
        """Get user's fraud history"""
        response = await self._api_client.get_fraud_history_async(request)
        if response.is_success:
            return FraudHistoryResponse.parse_obj(response.data)
        else:
            raise Exception(f"Fraud history request failed: {response.error_message}")
    
    async def update_user_preferences_async(self, preferences: UserPreferences) -> bool:
        """Update user preferences"""
        response = await self._api_client.update_user_preferences_async(preferences)
        if response.is_success:
            return response.data
        else:
            raise Exception(f"Preferences update failed: {response.error_message}")
    
    async def get_health_async(self) -> HealthStatus:
        """Get API health status"""
        response = await self._api_client.get_health_async()
        if response.is_success:
            return HealthStatus.parse_obj(response.data)
        else:
            raise Exception(f"Health check failed: {response.error_message}")
    
    # HTTP Interception methods
    async def intercept_request_async(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Intercept HTTP request for fraud analysis"""
        return await self._interceptor.intercept_request_async(method, url, headers, body)
    
    async def intercept_response_async(
        self, 
        request_id: str, 
        status_code: int, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> None:
        """Intercept HTTP response for fraud analysis"""
        await self._interceptor.intercept_response_async(request_id, status_code, headers, body)
    
    def should_intercept_request(self, url: str, method: str) -> bool:
        """Check if request should be intercepted"""
        return self._interceptor.should_intercept(url, method)
    
    # Storage methods
    async def store_user_info_async(self, user_info: UserInfo) -> None:
        """Store user information"""
        await self._storage.set_user_info_async(user_info)
    
    async def get_stored_user_info_async(self) -> Optional[UserInfo]:
        """Get stored user information"""
        return await self._storage.get_user_info_async()
    
    async def store_device_info_async(self, device_info: DeviceInfo) -> None:
        """Store device information"""
        await self._storage.set_device_info_async(device_info)
    
    async def get_stored_device_info_async(self) -> Optional[DeviceInfo]:
        """Get stored device information"""
        return await self._storage.get_device_info_async()
    
    # Service registration methods
    def register_connectivity_service(self, service: IConnectivityService) -> None:
        """Register connectivity service"""
        self._connectivity_service = service
    
    def register_sync_service(self, service: ISyncService) -> None:
        """Register sync service"""
        self._sync_service = service
    
    def register_notification_service(self, service: INotificationService) -> None:
        """Register notification service"""
        self._notification_service = service
    
    def register_analytics_service(self, service: IAnalyticsService) -> None:
        """Register analytics service"""
        self._analytics_service = service
    
    def register_cache_service(self, service: ICacheService) -> None:
        """Register cache service"""
        self._cache_service = service
    
    def register_device_service(self, service: IDeviceService) -> None:
        """Register device service"""
        self._device_service = service
    
    def register_biometric_service(self, service: IBiometricService) -> None:
        """Register biometric service"""
        self._biometric_service = service
    
    # Service access properties
    @property
    def authentication(self) -> IAuthenticationHandler:
        """Get authentication handler"""
        return self._auth_handler
    
    @property
    def api_client(self) -> IApiClient:
        """Get API client"""
        return self._api_client
    
    @property
    def storage(self) -> IStorage:
        """Get storage service"""
        return self._storage
    
    @property
    def interceptor(self) -> IHttpInterceptor:
        """Get HTTP interceptor"""
        return self._interceptor
    
    @property
    def connectivity_service(self) -> Optional[IConnectivityService]:
        """Get connectivity service"""
        return self._connectivity_service
    
    @property
    def sync_service(self) -> Optional[ISyncService]:
        """Get sync service"""
        return self._sync_service
    
    @property
    def notification_service(self) -> Optional[INotificationService]:
        """Get notification service"""
        return self._notification_service
    
    @property
    def analytics_service(self) -> Optional[IAnalyticsService]:
        """Get analytics service"""
        return self._analytics_service
    
    @property
    def cache_service(self) -> Optional[ICacheService]:
        """Get cache service"""
        return self._cache_service
    
    @property
    def device_service(self) -> Optional[IDeviceService]:
        """Get device service"""
        return self._device_service
    
    @property
    def biometric_service(self) -> Optional[IBiometricService]:
        """Get biometric service"""
        return self._biometric_service
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.dispose()


class FraudDetectionSdkBuilder:
    """Builder for Fraud Detection SDK"""
    
    def __init__(self):
        self._options = FraudDetectionSdkOptions(BaseUrl="")
        self._logger: Optional[logging.Logger] = None
    
    def with_base_url(self, base_url: str) -> "FraudDetectionSdkBuilder":
        """Set base URL"""
        self._options.base_url = base_url
        return self
    
    def with_timeout(self, timeout: float) -> "FraudDetectionSdkBuilder":
        """Set timeout"""
        self._options.timeout = timeout
        return self
    
    def with_environment(self, environment: str) -> "FraudDetectionSdkBuilder":
        """Set environment"""
        self._options.environment = environment
        return self
    
    def with_logger(self, logger: logging.Logger) -> "FraudDetectionSdkBuilder":
        """Set logger"""
        self._logger = logger
        return self
    
    def with_api_key(self, api_key: str) -> "FraudDetectionSdkBuilder":
        """Set API key"""
        self._options.api_key = api_key
        return self
    
    def with_offline_sync(self, enabled: bool = True) -> "FraudDetectionSdkBuilder":
        """Enable/disable offline sync"""
        self._options.offline_sync.enabled = enabled
        return self
    
    def with_caching(self, enabled: bool = True) -> "FraudDetectionSdkBuilder":
        """Enable/disable caching"""
        self._options.caching.enable_caching = enabled
        return self
    
    def build(self) -> FraudDetectionSdk:
        """Build the SDK"""
        return FraudDetectionSdk(self._options, self._logger)
