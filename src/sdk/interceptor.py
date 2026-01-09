"""
Universal Fraud Detection SDK HTTP Interceptor
Python implementation of HTTP request interception for fraud analysis
"""

import asyncio
import json
import logging
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from urllib.parse import urlparse

from .models import (
    FraudAnalysisRequest, FraudRiskAnalysis, FraudDetectionSdkOptions,
    FraudInterceptorOptions
)
from .interfaces import IHttpInterceptor, IAuthenticationHandler


class FraudDetectionInterceptor(IHttpInterceptor):
    """HTTP interceptor that analyzes ALL HTTP requests for fraud detection"""
    
    def __init__(
        self,
        options: FraudDetectionSdkOptions,
        auth_handler: IAuthenticationHandler,
        interceptor_options: Optional[FraudInterceptorOptions] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.options = options
        self.auth_handler = auth_handler
        self.interceptor_options = interceptor_options or FraudInterceptorOptions()
        self.logger = logger or logging.getLogger(__name__)
        self._request_handlers: List[callable] = []
        self._response_handlers: List[callable] = []
    
    def add_request_handler(self, handler: callable):
        """Add request analysis handler"""
        self._request_handlers.append(handler)
    
    def add_response_handler(self, handler: callable):
        """Add response analysis handler"""
        self._response_handlers.append(handler)
    
    async def intercept_request_async(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Intercept and analyze HTTP request"""
        try:
            # Skip fraud analysis for fraud detection API calls to avoid infinite loops
            if self._is_fraud_detection_api_call(url):
                return {
                    "should_block": False,
                    "risk_score": 0.0,
                    "reason": "Fraud detection API call"
                }
            
            # Capture request details for fraud analysis
            fraud_request = await self._capture_request_details(method, url, headers, body)
            
            # Analyze request for fraud risk
            risk_analysis = await self._analyze_fraud_risk(fraud_request)
            
            # Log the analysis
            self.logger.info(
                f"Fraud analysis for {method} {url}: Risk={risk_analysis.risk_score}, "
                f"Action={risk_analysis.recommended_action}"
            )
            
            # Fire request handlers
            await self._fire_request_handlers(fraud_request, risk_analysis)
            
            return {
                "should_block": risk_analysis.should_block,
                "risk_score": risk_analysis.risk_score,
                "reason": risk_analysis.block_reason,
                "recommended_action": risk_analysis.recommended_action,
                "request_id": fraud_request.request_id
            }
        
        except Exception as ex:
            self.logger.error(f"Error in fraud detection interceptor for {method} {url}: {ex}")
            
            # Continue with original request on error (fail-open for availability)
            return {
                "should_block": False,
                "risk_score": 0.0,
                "reason": "Analysis failed"
            }
    
    async def intercept_response_async(
        self, 
        request_id: str, 
        status_code: int, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> None:
        """Intercept and analyze HTTP response"""
        try:
            # Analyze response for additional fraud indicators
            response_analysis = {
                "request_id": request_id,
                "status_code": status_code,
                "response_headers": headers,
                "content_length": len(body) if body else 0,
                "response_time": datetime.utcnow().isoformat()
            }
            
            # Fire response handlers
            await self._fire_response_handlers(response_analysis)
            
            # Send response analysis (fire-and-forget)
            asyncio.create_task(self._send_response_analysis(response_analysis))
        
        except Exception as ex:
            self.logger.debug(f"Error analyzing response for request {request_id}: {ex}")
    
    def should_intercept(self, url: str, method: str) -> bool:
        """Determine if request should be intercepted"""
        # Check excluded methods
        if method.upper() in self.interceptor_options.exclude_methods:
            return False
        
        # Check excluded URL patterns
        for pattern in self.interceptor_options.exclude_url_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _is_fraud_detection_api_call(self, url: str) -> bool:
        """Check if this is a call to our fraud detection API"""
        if not url:
            return False
        
        # Skip calls to our own fraud detection API to prevent infinite loops
        return (
            self.options.base_url.lower() in url.lower() or
            "/api/frauddetection" in url.lower() or
            "/api/advancedanalytics" in url.lower() or
            "/api/mobile/v1" in url.lower()
        )
    
    async def _capture_request_details(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[str]
    ) -> FraudAnalysisRequest:
        """Capture request details for fraud analysis"""
        fraud_request = FraudAnalysisRequest(
            RequestId=self._generate_request_id(),
            Method=method,
            Url=url,
            Headers=headers,
            Body=body if self.interceptor_options.analyze_request_bodies else None,
            Timestamp=datetime.utcnow(),
            UserAgent=headers.get("User-Agent"),
            ContentType=headers.get("Content-Type")
        )
        
        # Limit body size
        if fraud_request.body and len(fraud_request.body) > self.interceptor_options.max_body_size:
            fraud_request.body = fraud_request.body[:self.interceptor_options.max_body_size] + "...[truncated]"
        
        return fraud_request
    
    async def _analyze_fraud_risk(self, request: FraudAnalysisRequest) -> FraudRiskAnalysis:
        """Analyze request for fraud risk"""
        try:
            # Get user context if available
            user_id = await self.auth_handler.get_current_user_id_async()
            
            # Create fraud analysis payload
            analysis_payload = {
                "requestId": request.request_id,
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
                "body": request.body,
                "userId": user_id,
                "timestamp": request.timestamp.isoformat(),
                "userAgent": request.user_agent,
                "contentType": request.content_type
            }
            
            # In a real implementation, this would send to the fraud detection API
            # For now, we'll simulate the analysis
            risk_score = await self._simulate_fraud_analysis(analysis_payload)
            
            return FraudRiskAnalysis(
                RequestId=request.request_id,
                RiskScore=risk_score,
                RecommendedAction="BLOCK" if risk_score > self.interceptor_options.block_threshold else "ALLOW",
                ShouldBlock=risk_score > self.interceptor_options.block_threshold,
                BlockReason=self._get_block_reason(risk_score),
                AnalysisTimestamp=datetime.utcnow()
            )
        
        except Exception as ex:
            self.logger.error(f"Error analyzing fraud risk for request {request.request_id}: {ex}")
            return self._create_default_analysis(request, 0.0, "Analysis failed")
    
    async def _simulate_fraud_analysis(self, payload: Dict[str, Any]) -> float:
        """Simulate fraud analysis (replace with actual API call)"""
        risk_score = 0.0
        
        # Analyze URL patterns
        url = payload.get("url", "")
        if any(pattern in url.lower() for pattern in ["admin", "root", "config", "backup"]):
            risk_score += 0.3
        
        # Analyze method
        method = payload.get("method", "").upper()
        if method in ["DELETE", "PUT", "PATCH"]:
            risk_score += 0.2
        
        # Analyze headers
        headers = payload.get("headers", {})
        if not headers.get("User-Agent"):
            risk_score += 0.1
        
        # Analyze body content
        body = payload.get("body", "")
        if body:
            if any(pattern in body.lower() for pattern in ["password", "secret", "key"]):
                risk_score += 0.2
            if len(body) > 10000:  # Large payload
                risk_score += 0.1
        
        # Analyze user agent
        user_agent = payload.get("userAgent", "")
        if not user_agent or "bot" in user_agent.lower():
            risk_score += 0.2
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    def _get_block_reason(self, risk_score: float) -> str:
        """Get block reason based on risk score"""
        if risk_score > 0.8:
            return "High risk detected"
        elif risk_score > 0.6:
            return "Medium risk detected"
        elif risk_score > 0.3:
            return "Low risk detected"
        else:
            return "No significant risk"
    
    def _create_default_analysis(self, request: FraudAnalysisRequest, risk_score: float, reason: str) -> FraudRiskAnalysis:
        """Create default analysis result"""
        return FraudRiskAnalysis(
            RequestId=request.request_id,
            RiskScore=risk_score,
            RecommendedAction="BLOCK" if risk_score > 0.7 else "ALLOW",
            ShouldBlock=risk_score > 0.8,
            BlockReason=reason,
            AnalysisTimestamp=datetime.utcnow()
        )
    
    async def _send_response_analysis(self, response_analysis: Dict[str, Any]):
        """Send response analysis to fraud detection API"""
        try:
            # In a real implementation, this would send to the fraud detection API
            # For now, we'll just log it
            self.logger.debug(f"Response analysis for request {response_analysis['request_id']}")
        except Exception as ex:
            self.logger.debug(f"Failed to send response analysis: {ex}")
    
    async def _fire_request_handlers(self, request: FraudAnalysisRequest, analysis: FraudRiskAnalysis):
        """Fire request analysis handlers"""
        for handler in self._request_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(request, analysis)
                else:
                    handler(request, analysis)
            except Exception as ex:
                self.logger.error(f"Error in request handler: {ex}")
    
    async def _fire_response_handlers(self, response_analysis: Dict[str, Any]):
        """Fire response analysis handlers"""
        for handler in self._response_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(response_analysis)
                else:
                    handler(response_analysis)
            except Exception as ex:
                self.logger.error(f"Error in response handler: {ex}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())


class MockFraudDetectionInterceptor(IHttpInterceptor):
    """Mock interceptor for testing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def intercept_request_async(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock request interception"""
        # Simple mock logic
        risk_score = 0.1
        if "admin" in url.lower():
            risk_score = 0.8
        
        return {
            "should_block": risk_score > 0.7,
            "risk_score": risk_score,
            "reason": "Mock analysis",
            "recommended_action": "BLOCK" if risk_score > 0.7 else "ALLOW",
            "request_id": f"mock_{hash(url)}"
        }
    
    async def intercept_response_async(
        self, 
        request_id: str, 
        status_code: int, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> None:
        """Mock response interception"""
        self.logger.debug(f"Mock response analysis for request {request_id}")
    
    def should_intercept(self, url: str, method: str) -> bool:
        """Mock intercept decision"""
        return method.upper() not in ["OPTIONS", "HEAD"]


class UniversalHttpInterceptor:
    """Universal HTTP interceptor that works with any HTTP client"""
    
    def __init__(
        self,
        interceptor: FraudDetectionInterceptor,
        logger: Optional[logging.Logger] = None
    ):
        self.interceptor = interceptor
        self.logger = logger or logging.getLogger(__name__)
    
    async def intercept_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Intercept HTTP request"""
        if not self.interceptor.should_intercept(url, method):
            return None
        
        analysis = await self.interceptor.intercept_request_async(method, url, headers, body)
        
        if analysis.get("should_block", False):
            self.logger.warning(
                f"Blocking high-risk request: {method} {url} (Risk: {analysis.get('risk_score', 0)})"
            )
            return {
                "blocked": True,
                "status_code": 403,
                "error": "Request blocked due to fraud risk",
                "risk_score": analysis.get("risk_score", 0),
                "reason": analysis.get("reason", "High risk detected")
            }
        
        return analysis
    
    async def intercept_response(
        self, 
        request_id: str, 
        status_code: int, 
        headers: Dict[str, str], 
        body: Optional[str] = None
    ) -> None:
        """Intercept HTTP response"""
        await self.interceptor.intercept_response_async(request_id, status_code, headers, body)
