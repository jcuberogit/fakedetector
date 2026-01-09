"""
Universal Fraud Detection SDK Client
Python implementation of the fraud detection API client
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiohttp
from urllib.parse import urlencode

from .models import (
    ApiResponse, MobileChatRequest, MobileFraudResponse, MobileTransactionRequest,
    MobileCounterfactualRequest, CounterfactualResponse, FraudFeedback,
    FraudHistoryRequest, FraudHistoryResponse, UserPreferences, HealthStatus,
    FraudDetectionSdkOptions
)
from .interfaces import IApiClient, IAuthenticationHandler


class FraudDetectionApiClient(IApiClient):
    """API client for fraud detection services"""
    
    def __init__(
        self,
        options: FraudDetectionSdkOptions,
        auth_handler: IAuthenticationHandler,
        logger: Optional[logging.Logger] = None
    ):
        self.options = options
        self.auth_handler = auth_handler
        self.logger = logger or logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self._response_received_handlers: List[callable] = []
        self._error_occurred_handlers: List[callable] = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.dispose()
    
    async def initialize(self):
        """Initialize the API client"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.options.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            self.logger.info("Fraud Detection API Client initialized")
    
    async def dispose(self):
        """Dispose of resources"""
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("Fraud Detection API Client disposed")
    
    def add_response_received_handler(self, handler: callable):
        """Add response received event handler"""
        self._response_received_handlers.append(handler)
    
    def add_error_occurred_handler(self, handler: callable):
        """Add error occurred event handler"""
        self._error_occurred_handlers.append(handler)
    
    async def chat_async(self, request: MobileChatRequest) -> ApiResponse[MobileFraudResponse]:
        """Send chat message for fraud analysis"""
        if not request.message.strip():
            return ApiResponse.failure("Message cannot be empty", 400, "invalid_request")
        
        endpoint = "/api/mobile/v1/chat"
        return await self._execute_authorized_request(
            "POST", endpoint, request.dict(by_alias=True)
        )
    
    async def check_transaction_risk_async(self, request: MobileTransactionRequest) -> ApiResponse[MobileFraudResponse]:
        """Check transaction risk"""
        endpoint = "/api/mobile/v1/risk-check"
        return await self._execute_authorized_request(
            "POST", endpoint, request.dict(by_alias=True)
        )
    
    async def get_counterfactual_analysis_async(self, request: MobileCounterfactualRequest) -> ApiResponse[CounterfactualResponse]:
        """Get counterfactual analysis for transaction"""
        endpoint = "/api/mobile/v1/counterfactual"
        return await self._execute_authorized_request(
            "POST", endpoint, request.dict(by_alias=True)
        )
    
    async def submit_feedback_async(self, feedback: FraudFeedback) -> ApiResponse[bool]:
        """Submit user feedback on fraud detection"""
        endpoint = "/api/mobile/v1/feedback"
        return await self._execute_authorized_request(
            "POST", endpoint, feedback.dict(by_alias=True)
        )
    
    async def get_fraud_history_async(self, request: FraudHistoryRequest) -> ApiResponse[FraudHistoryResponse]:
        """Get user's fraud history"""
        query_params = {}
        if request.start_date:
            query_params["startDate"] = request.start_date.isoformat()
        if request.end_date:
            query_params["endDate"] = request.end_date.isoformat()
        if request.max_items:
            query_params["maxItems"] = request.max_items
        if request.page:
            query_params["page"] = request.page
        if request.risk_level_filter:
            query_params["riskLevelFilter"] = request.risk_level_filter
        if request.transaction_type_filter:
            query_params["transactionTypeFilter"] = request.transaction_type_filter
        
        query_string = urlencode(query_params)
        endpoint = f"/api/mobile/v1/history?{query_string}" if query_string else "/api/mobile/v1/history"
        
        return await self._execute_authorized_request("GET", endpoint, None)
    
    async def update_user_preferences_async(self, preferences: UserPreferences) -> ApiResponse[bool]:
        """Update user preferences"""
        endpoint = "/api/mobile/v1/preferences"
        return await self._execute_authorized_request(
            "PUT", endpoint, preferences.dict(by_alias=True)
        )
    
    async def get_health_async(self) -> ApiResponse[HealthStatus]:
        """Get API health status"""
        endpoint = "/health"
        return await self._execute_request("GET", endpoint, None, require_auth=False)
    
    async def _execute_authorized_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]]) -> ApiResponse:
        """Execute an authorized API request"""
        return await self._execute_request(method, endpoint, data, require_auth=True)
    
    async def _execute_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]], 
        require_auth: bool = True
    ) -> ApiResponse:
        """Execute an API request"""
        await self.initialize()
        
        start_time = datetime.utcnow()
        full_url = f"{self.options.base_url}{endpoint}"
        
        try:
            headers = {}
            
            # Set authorization header if required
            if require_auth:
                access_token = await self.auth_handler.get_access_token_async()
                if not access_token:
                    return ApiResponse.failure("Unauthorized - no valid access token", 401, "unauthorized")
                headers["Authorization"] = f"Bearer {access_token}"
            
            # Prepare request data
            json_data = None
            if data and method in ["POST", "PUT", "PATCH"]:
                json_data = data
            
            self.logger.debug(f"Executing {method} request to {endpoint}")
            
            # Send request
            async with self.session.request(
                method, full_url, headers=headers, json=json_data
            ) as response:
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Fire response event
                await self._fire_response_received_event(endpoint, response.status, response_time, response.ok)
                
                if response.ok:
                    response_content = await response.text()
                    
                    if response_content:
                        try:
                            response_data = json.loads(response_content)
                            
                            self.logger.debug(
                                f"Successfully executed {method} request to {endpoint} in {response_time:.2f}s"
                            )
                            
                            return ApiResponse.success(response_data, response.status)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Failed to parse JSON response from {endpoint}")
                            return ApiResponse.failure("Invalid JSON response", response.status, "invalid_response")
                    else:
                        return ApiResponse.success(None, response.status)
                else:
                    error_content = await response.text()
                    error_message = self._extract_error_message(error_content, response.status)
                    
                    self.logger.warning(
                        f"API request failed: {method} {endpoint} - {response.status}: {error_message}"
                    )
                    
                    # Fire error event
                    await self._fire_error_occurred_event(endpoint, error_message, response.status, self._is_retryable_status_code(response.status))
                    
                    error_code = self._get_error_code(response.status)
                    return ApiResponse.failure(error_message, response.status, error_code)
        
        except asyncio.TimeoutError:
            error_message = "Request timeout"
            self.logger.error(f"Request timeout for {method} {endpoint}")
            
            await self._fire_error_occurred_event(endpoint, error_message, 408, True)
            return ApiResponse.failure(error_message, 408, "timeout")
        
        except aiohttp.ClientError as ex:
            error_message = f"Network error: {str(ex)}"
            self.logger.error(f"Network error for {method} {endpoint}: {ex}")
            
            await self._fire_error_occurred_event(endpoint, error_message, 0, True)
            return ApiResponse.failure(error_message, 0, "network_error")
        
        except Exception as ex:
            error_message = f"Unexpected error: {str(ex)}"
            self.logger.error(f"Unexpected error for {method} {endpoint}: {ex}")
            
            await self._fire_error_occurred_event(endpoint, error_message, 0, False)
            return ApiResponse.failure(error_message, 0, "exception")
    
    def _extract_error_message(self, content: str, status_code: int) -> str:
        """Extract error message from response content"""
        if not content:
            return f"HTTP {status_code}"
        
        try:
            error_data = json.loads(content)
            
            # Try common error message properties
            for key in ["error", "message", "title"]:
                if key in error_data:
                    return str(error_data[key])
            
            return content
        except json.JSONDecodeError:
            pass
        
        # Default error messages based on status code
        error_messages = {
            401: "Unauthorized access",
            403: "Access forbidden",
            404: "Resource not found",
            400: "Bad request",
            500: "Internal server error",
            503: "Service unavailable",
            429: "Too many requests"
        }
        
        return error_messages.get(status_code, f"HTTP {status_code}")
    
    def _is_retryable_status_code(self, status_code: int) -> bool:
        """Check if status code is retryable"""
        retryable_codes = {408, 429, 500, 502, 503, 504}
        return status_code in retryable_codes
    
    def _get_error_code(self, status_code: int) -> str:
        """Get error code for status code"""
        error_codes = {
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            400: "bad_request",
            500: "server_error",
            503: "service_unavailable",
            429: "rate_limited"
        }
        return error_codes.get(status_code, "api_error")
    
    async def _fire_response_received_event(self, endpoint: str, status_code: int, response_time: float, is_success: bool):
        """Fire response received event"""
        event_data = {
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time,
            "is_success": is_success
        }
        
        for handler in self._response_received_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as ex:
                self.logger.error(f"Error in response received handler: {ex}")
    
    async def _fire_error_occurred_event(self, endpoint: str, error_message: str, status_code: int, is_retryable: bool):
        """Fire error occurred event"""
        event_data = {
            "endpoint": endpoint,
            "error_message": error_message,
            "status_code": status_code,
            "is_retryable": is_retryable
        }
        
        for handler in self._error_occurred_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as ex:
                self.logger.error(f"Error in error occurred handler: {ex}")


class MockFraudDetectionApiClient(IApiClient):
    """Mock API client for testing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def chat_async(self, request: MobileChatRequest) -> ApiResponse[MobileFraudResponse]:
        """Mock chat response"""
        response = MobileFraudResponse(
            Message="Mock response: " + request.message,
            RiskScore=0.3,
            RiskLevel="Low",
            Recommendations=["This is a mock response"],
            ConversationId="mock_conv_123"
        )
        return ApiResponse.success(response.dict(by_alias=True))
    
    async def check_transaction_risk_async(self, request: MobileTransactionRequest) -> ApiResponse[MobileFraudResponse]:
        """Mock transaction risk check"""
        risk_score = 0.1 if request.amount < 1000 else 0.8
        risk_level = "Low" if risk_score < 0.5 else "High"
        
        response = MobileFraudResponse(
            Message=f"Mock risk assessment for ${request.amount}",
            RiskScore=risk_score,
            RiskLevel=risk_level,
            Recommendations=["This is a mock assessment"]
        )
        return ApiResponse.success(response.dict(by_alias=True))
    
    async def get_counterfactual_analysis_async(self, request: MobileCounterfactualRequest) -> ApiResponse[CounterfactualResponse]:
        """Mock counterfactual analysis"""
        response = CounterfactualResponse(
            OriginalRiskScore=0.8,
            TargetThreshold=request.target_risk_threshold,
            CanAchieveTarget=True,
            BestAchievableRiskScore=0.3,
            ConfidenceLevel=0.9,
            DetailedExplanation="Mock counterfactual analysis",
            Recommendations=[]
        )
        return ApiResponse.success(response.dict(by_alias=True))
    
    async def submit_feedback_async(self, feedback: FraudFeedback) -> ApiResponse[bool]:
        """Mock feedback submission"""
        return ApiResponse.success(True)
    
    async def get_fraud_history_async(self, request: FraudHistoryRequest) -> ApiResponse[FraudHistoryResponse]:
        """Mock fraud history"""
        response = FraudHistoryResponse(
            Transactions=[],
            TotalCount=0,
            Page=request.page or 1,
            PageSize=20,
            HasMore=False
        )
        return ApiResponse.success(response.dict(by_alias=True))
    
    async def update_user_preferences_async(self, preferences: UserPreferences) -> ApiResponse[bool]:
        """Mock preferences update"""
        return ApiResponse.success(True)
    
    async def get_health_async(self) -> ApiResponse[HealthStatus]:
        """Mock health check"""
        response = HealthStatus(
            Status="Healthy",
            Version="1.0.0",
            Services={"api": "healthy", "database": "healthy"}
        )
        return ApiResponse.success(response.dict(by_alias=True))
