"""
Universal Fraud Detection SDK Authentication Handler
Python implementation of authentication operations
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from .models import (
    AuthenticationResult, LoginRequest, TokenResponse, UserInfo,
    AuthenticationStateChangedEventArgs, TokenExpiringEventArgs
)
from .interfaces import IAuthenticationHandler, IStorage


class AuthenticationHandler(IAuthenticationHandler):
    """Handles authentication operations for the Fraud Detection SDK"""
    
    def __init__(
        self,
        storage: IStorage,
        base_url: str,
        logger: Optional[logging.Logger] = None
    ):
        self.storage = storage
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
        self._state_changed_handlers: List[callable] = []
        self._token_expiring_handlers: List[callable] = []
        self._is_test_mode = "test" in base_url.lower()
    
    def add_state_changed_handler(self, handler: callable):
        """Add authentication state changed event handler"""
        self._state_changed_handlers.append(handler)
    
    def add_token_expiring_handler(self, handler: callable):
        """Add token expiring event handler"""
        self._token_expiring_handlers.append(handler)
    
    async def login_async(self, login_request: LoginRequest) -> AuthenticationResult:
        """Authenticate user with credentials"""
        if not login_request.username.strip():
            return AuthenticationResult(
                IsSuccess=False,
                ErrorMessage="Username is required",
                ErrorCode="invalid_username"
            )
        
        if not login_request.password.strip():
            return AuthenticationResult(
                IsSuccess=False,
                ErrorMessage="Password is required",
                ErrorCode="invalid_password"
            )
        
        try:
            self.logger.info(f"Attempting login for user: {login_request.username}")
            
            if self._is_test_mode:
                return await self._handle_test_mode_login(login_request)
            
            # In production, this would make an actual API call
            # For now, we'll simulate a successful login
            token_response = TokenResponse(
                AccessToken=self._create_test_token(),
                RefreshToken="refresh-token-123",
                ExpiresIn=3600,
                TokenType="Bearer"
            )
            
            # Store tokens securely
            await self.storage.set_token_async("access_token", token_response.access_token)
            await self.storage.set_token_async("refresh_token", token_response.refresh_token)
            
            # Extract and store user info from token
            user_info = self._extract_user_info_from_token(token_response.access_token)
            if user_info:
                await self.storage.set_user_info_async(user_info)
            
            self.logger.info(f"Login successful for user: {login_request.username}")
            
            # Fire authentication state changed event
            await self._fire_state_changed_event(True, user_info, "Login successful")
            
            return AuthenticationResult(
                IsSuccess=True,
                TokenResponse=token_response
            )
        
        except Exception as ex:
            self.logger.error(f"Exception during login for user: {login_request.username}: {ex}")
            
            return AuthenticationResult(
                IsSuccess=False,
                ErrorMessage=f"Login error: {str(ex)}",
                ErrorCode="exception"
            )
    
    async def refresh_token_async(self) -> AuthenticationResult:
        """Refresh access token using refresh token"""
        try:
            refresh_token = await self.storage.get_token_async("refresh_token")
            if not refresh_token:
                self.logger.warning("No refresh token available")
                return AuthenticationResult(
                    IsSuccess=False,
                    ErrorMessage="No refresh token available",
                    ErrorCode="no_refresh_token"
                )
            
            if self._is_test_mode:
                return await self._handle_test_mode_refresh(refresh_token)
            
            # In production, this would make an actual API call
            # For now, we'll simulate a successful refresh
            new_token_response = TokenResponse(
                AccessToken=self._create_test_token(),
                RefreshToken="new-refresh-token-456",
                ExpiresIn=3600,
                TokenType="Bearer"
            )
            
            # Store new tokens
            await self.storage.set_token_async("access_token", new_token_response.access_token)
            await self.storage.set_token_async("refresh_token", new_token_response.refresh_token)
            
            # Update user info from new token
            user_info = self._extract_user_info_from_token(new_token_response.access_token)
            if user_info:
                await self.storage.set_user_info_async(user_info)
            
            self.logger.info("Token refresh successful")
            
            return AuthenticationResult(
                IsSuccess=True,
                TokenResponse=new_token_response
            )
        
        except Exception as ex:
            self.logger.error(f"Exception during token refresh: {ex}")
            
            return AuthenticationResult(
                IsSuccess=False,
                ErrorMessage=f"Token refresh error: {str(ex)}",
                ErrorCode="exception"
            )
    
    async def logout_async(self) -> bool:
        """Logout and revoke tokens"""
        try:
            self.logger.info("Performing logout")
            
            access_token = await self.storage.get_token_async("access_token")
            refresh_token = await self.storage.get_token_async("refresh_token")
            
            # In test mode, skip server revocation
            if not self._is_test_mode:
                # In production, attempt to revoke tokens on server
                if access_token:
                    try:
                        # This would make an actual API call to revoke tokens
                        self.logger.debug("Revoking tokens on server")
                    except Exception as ex:
                        self.logger.warning(f"Failed to revoke tokens on server: {ex}")
            
            # Clear stored tokens and user info
            await self.storage.remove_token_async("access_token")
            await self.storage.remove_token_async("refresh_token")
            await self.storage.remove_async("user_info")
            
            self.logger.info("Logout completed")
            
            # Fire authentication state changed event
            await self._fire_state_changed_event(False, None, "Logout")
            
            return True
        
        except Exception as ex:
            self.logger.error(f"Exception during logout: {ex}")
            return False
    
    async def is_authenticated_async(self) -> bool:
        """Check if user is currently authenticated"""
        try:
            access_token = await self.storage.get_token_async("access_token")
            return self.validate_token(access_token)
        except Exception as ex:
            self.logger.error(f"Exception checking authentication status: {ex}")
            return False
    
    async def get_current_user_async(self) -> Optional[UserInfo]:
        """Get current user information from token"""
        try:
            access_token = await self.storage.get_token_async("access_token")
            if not self.validate_token(access_token):
                return None
            
            # Try to get cached user info first
            user_info = await self.storage.get_user_info_async()
            if user_info:
                return user_info
            
            # Extract from token if not cached
            if access_token:
                return self._extract_user_info_from_token(access_token)
            
            return None
        
        except Exception as ex:
            self.logger.error(f"Exception getting current user: {ex}")
            return None
    
    async def get_current_user_id_async(self) -> Optional[str]:
        """Get current user ID from token"""
        try:
            user_info = await self.get_current_user_async()
            return user_info.user_id if user_info else None
        except Exception as ex:
            self.logger.error(f"Error getting current user ID: {ex}")
            return None
    
    async def get_access_token_async(self) -> Optional[str]:
        """Get current access token"""
        try:
            access_token = await self.storage.get_token_async("access_token")
            
            if self.validate_token(access_token):
                return access_token
            
            # Token is expired, try to refresh
            refresh_result = await self.refresh_token_async()
            if refresh_result.is_success and refresh_result.token_response:
                return refresh_result.token_response.access_token
            
            return None
        
        except Exception as ex:
            self.logger.error(f"Exception getting access token: {ex}")
            return None
    
    def validate_token(self, token: Optional[str]) -> bool:
        """Validate a JWT token"""
        if not token:
            return False
        
        try:
            # Decode token without verification for testing
            # In production, you would verify the signature
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp:
                exp_time = datetime.fromtimestamp(exp)
                now = datetime.utcnow()
                
                if exp_time <= now:
                    self.logger.debug(f"Token is expired. Expires: {exp_time}, Now: {now}")
                    return False
                
                # Check if token is about to expire (within 5 minutes)
                time_to_expiry = exp_time - now
                if time_to_expiry <= timedelta(minutes=5):
                    await self._fire_token_expiring_event(exp_time, time_to_expiry.total_seconds(), True)
            
            return True
        
        except (InvalidTokenError, ExpiredSignatureError) as ex:
            self.logger.debug(f"Invalid token format: {ex}")
            return False
        except Exception as ex:
            self.logger.debug(f"Error validating token: {ex}")
            return False
    
    def _extract_user_info_from_token(self, token: str) -> Optional[UserInfo]:
        """Extract user information from JWT token"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            return UserInfo(
                UserId=payload.get('sub', payload.get('user_id', '')),
                Username=payload.get('email', payload.get('username', '')),
                Name=payload.get('name', ''),
                Email=payload.get('email'),
                Roles=payload.get('roles', []),
                Claims=payload,
                PreferredLanguage=payload.get('locale')
            )
        
        except Exception as ex:
            self.logger.error(f"Failed to extract user info from token: {ex}")
            return None
    
    async def _handle_test_mode_login(self, login_request: LoginRequest) -> AuthenticationResult:
        """Handle login in test mode"""
        # Simulate test authentication logic
        if login_request.username == "testuser@example.com" and login_request.password == "TestPassword123!":
            # Create test tokens
            access_token = self._create_test_token()
            refresh_token = "refresh-token-123"
            
            # Store tokens
            await self.storage.set_token_async("access_token", access_token)
            await self.storage.set_token_async("refresh_token", refresh_token)
            
            # Create test user info
            user_info = UserInfo(
                UserId="user123",
                Username=login_request.username,
                Email=login_request.username,
                Name="Test User"
            )
            
            await self.storage.set_user_info_async(user_info)
            
            self.logger.info(f"Test mode login successful for user: {login_request.username}")
            
            await self._fire_state_changed_event(True, user_info, "Test login successful")
            
            return AuthenticationResult(
                IsSuccess=True,
                TokenResponse=TokenResponse(
                    AccessToken=access_token,
                    RefreshToken=refresh_token,
                    ExpiresIn=3600,
                    TokenType="Bearer"
                )
            )
        
        return AuthenticationResult(
            IsSuccess=False,
            ErrorMessage="Invalid credentials",
            ErrorCode="invalid_credentials"
        )
    
    async def _handle_test_mode_refresh(self, refresh_token: str) -> AuthenticationResult:
        """Handle token refresh in test mode"""
        # Check if refresh token is expired (for test purposes)
        if "expired" in refresh_token:
            return AuthenticationResult(
                IsSuccess=False,
                ErrorMessage="Refresh token expired",
                ErrorCode="refresh_token_expired"
            )
        
        self.logger.info("Test mode token refresh successful")
        
        return AuthenticationResult(
            IsSuccess=True,
            TokenResponse=TokenResponse(
                AccessToken=self._create_test_token(),
                RefreshToken="new-refresh-token-456",
                ExpiresIn=3600,
                TokenType="Bearer"
            )
        )
    
    def _create_test_token(self) -> str:
        """Create a test JWT token"""
        payload = {
            'sub': 'user123',
            'email': 'testuser@example.com',
            'name': 'Test User',
            'roles': ['User'],
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'iss': 'test-issuer',
            'aud': 'test-audience'
        }
        
        # Create token without signature for testing
        return jwt.encode(payload, "test-secret", algorithm="HS256")
    
    async def _fire_state_changed_event(self, is_authenticated: bool, user_info: Optional[UserInfo], reason: str):
        """Fire authentication state changed event"""
        event_data = AuthenticationStateChangedEventArgs(
            IsAuthenticated=is_authenticated,
            UserInfo=user_info,
            Reason=reason
        )
        
        for handler in self._state_changed_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as ex:
                self.logger.error(f"Error in state changed handler: {ex}")
    
    async def _fire_token_expiring_event(self, expires_at: datetime, time_remaining: float, should_auto_refresh: bool):
        """Fire token expiring event"""
        event_data = TokenExpiringEventArgs(
            ExpiresAt=expires_at,
            TimeRemaining=time_remaining,
            ShouldAutoRefresh=should_auto_refresh
        )
        
        for handler in self._token_expiring_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as ex:
                self.logger.error(f"Error in token expiring handler: {ex}")


class MockAuthenticationHandler(IAuthenticationHandler):
    """Mock authentication handler for testing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._is_authenticated = False
        self._user_info: Optional[UserInfo] = None
    
    async def login_async(self, login_request: LoginRequest) -> AuthenticationResult:
        """Mock login"""
        if login_request.username == "test@example.com" and login_request.password == "password":
            self._is_authenticated = True
            self._user_info = UserInfo(
                UserId="test_user_123",
                Username=login_request.username,
                Name="Test User",
                Email=login_request.username
            )
            return AuthenticationResult(IsSuccess=True)
        return AuthenticationResult(IsSuccess=False, ErrorMessage="Invalid credentials")
    
    async def refresh_token_async(self) -> AuthenticationResult:
        """Mock token refresh"""
        return AuthenticationResult(IsSuccess=True)
    
    async def logout_async(self) -> bool:
        """Mock logout"""
        self._is_authenticated = False
        self._user_info = None
        return True
    
    async def is_authenticated_async(self) -> bool:
        """Mock authentication check"""
        return self._is_authenticated
    
    async def get_current_user_async(self) -> Optional[UserInfo]:
        """Mock get current user"""
        return self._user_info
    
    async def get_current_user_id_async(self) -> Optional[str]:
        """Mock get current user ID"""
        return self._user_info.user_id if self._user_info else None
    
    async def get_access_token_async(self) -> Optional[str]:
        """Mock get access token"""
        return "mock_access_token" if self._is_authenticated else None
    
    def validate_token(self, token: Optional[str]) -> bool:
        """Mock token validation"""
        return token == "mock_access_token"
