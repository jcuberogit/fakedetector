"""
Authentication Service for the Python Fraud Detection Agent.
Handles user authentication, login, logout, and session management.
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import request

from .security_models import (
    LoginRequest, LoginResponse, RefreshTokenRequest, LogoutRequest,
    UserInfo, UserContext, SecuritySettings, UserRole, Permission,
    DeviceInfo, SessionInfo, SecurityAuditLog, SecurityMetrics
)
from .jwt_service import JWTService, PasswordService

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service for user login, logout, and session management."""
    
    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        self.jwt_service = JWTService(settings)
        self.password_service = PasswordService(settings)
        
        # In-memory storage for demo (replace with database in production)
        self._users: Dict[str, UserInfo] = {}
        self._user_passwords: Dict[str, str] = {}
        self._login_attempts: Dict[str, List[datetime]] = {}
        self._blocked_users: Dict[str, datetime] = {}
        self._security_metrics = SecurityMetrics()
        self._audit_logs: List[SecurityAuditLog] = []
        
        # Initialize demo users
        self._initialize_demo_users()
        
        logger.info("Authentication Service initialized")
    
    def _initialize_demo_users(self):
        """Initialize demo users for testing."""
        demo_users = [
            {
                'user_id': 'demo-user-123',
                'email': 'demo@bank.com',
                'name': 'Demo Customer',
                'password': 'password',
                'roles': [UserRole.CUSTOMER],
                'permissions': [
                    Permission.VIEW_TRANSACTIONS,
                    Permission.ANALYZE_TRANSACTIONS,
                    Permission.VIEW_FRAUD_ALERTS
                ],
                'account_id': 'ACC-789456123'
            },
            {
                'user_id': 'admin-user-456',
                'email': 'admin@bank.com',
                'name': 'Admin User',
                'password': 'admin123',
                'roles': [UserRole.ADMIN],
                'permissions': [
                    Permission.VIEW_FRAUD_ALERTS,
                    Permission.CREATE_FRAUD_ALERTS,
                    Permission.UPDATE_FRAUD_ALERTS,
                    Permission.DELETE_FRAUD_ALERTS,
                    Permission.VIEW_TRANSACTIONS,
                    Permission.ANALYZE_TRANSACTIONS,
                    Permission.BLOCK_TRANSACTIONS,
                    Permission.APPROVE_TRANSACTIONS,
                    Permission.VIEW_ML_MODELS,
                    Permission.TRAIN_ML_MODELS,
                    Permission.DEPLOY_ML_MODELS,
                    Permission.VIEW_GRAPHS,
                    Permission.CREATE_GRAPHS,
                    Permission.ANALYZE_GRAPHS,
                    Permission.VIEW_CONFIG,
                    Permission.UPDATE_CONFIG,
                    Permission.VIEW_ANALYTICS,
                    Permission.EXPORT_DATA,
                    Permission.VIEW_SYSTEM_HEALTH,
                    Permission.MANAGE_USERS,
                    Permission.VIEW_AUDIT_LOGS
                ],
                'account_id': 'ACC-ADMIN-001'
            },
            {
                'user_id': 'analyst-user-789',
                'email': 'analyst@bank.com',
                'name': 'Fraud Analyst',
                'password': 'analyst123',
                'roles': [UserRole.ANALYST],
                'permissions': [
                    Permission.VIEW_FRAUD_ALERTS,
                    Permission.UPDATE_FRAUD_ALERTS,
                    Permission.VIEW_TRANSACTIONS,
                    Permission.ANALYZE_TRANSACTIONS,
                    Permission.BLOCK_TRANSACTIONS,
                    Permission.APPROVE_TRANSACTIONS,
                    Permission.VIEW_ML_MODELS,
                    Permission.VIEW_GRAPHS,
                    Permission.ANALYZE_GRAPHS,
                    Permission.VIEW_ANALYTICS,
                    Permission.EXPORT_DATA
                ],
                'account_id': 'ACC-ANALYST-001'
            }
        ]
        
        for user_data in demo_users:
            password_hash = self.password_service.hash_password(user_data['password'])
            
            user = UserInfo(
                user_id=user_data['user_id'],
                email=user_data['email'],
                name=user_data['name'],
                roles=user_data['roles'],
                permissions=user_data['permissions'],
                account_id=user_data['account_id'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            self._users[user_data['user_id']] = user
            self._user_passwords[user_data['user_id']] = password_hash
        
        logger.info(f"Initialized {len(demo_users)} demo users")
    
    def login(self, login_request: LoginRequest) -> Optional[LoginResponse]:
        """
        Authenticate user and return login response.
        
        Args:
            login_request: Login request data
            
        Returns:
            Login response if successful, None otherwise
        """
        try:
            # Find user by email
            user = None
            for u in self._users.values():
                if u.email == login_request.email:
                    user = u
                    break
            
            if not user:
                self._log_security_event(
                    action="LOGIN_FAILED",
                    resource=f"email:{login_request.email}",
                    result="USER_NOT_FOUND",
                    details={"email": login_request.email}
                )
                return None
            
            # Check if user is blocked
            if user.user_id in self._blocked_users:
                block_until = self._blocked_users[user.user_id]
                if datetime.utcnow() < block_until:
                    self._log_security_event(
                        action="LOGIN_BLOCKED",
                        resource=f"user:{user.user_id}",
                        result="USER_BLOCKED",
                        details={"blocked_until": block_until.isoformat()}
                    )
                    return None
                else:
                    # Unblock user
                    del self._blocked_users[user.user_id]
            
            # Check login attempts
            if not self._check_login_attempts(user.user_id):
                self._log_security_event(
                    action="LOGIN_BLOCKED",
                    resource=f"user:{user.user_id}",
                    result="TOO_MANY_ATTEMPTS",
                    details={"max_attempts": self.settings.max_login_attempts}
                )
                return None
            
            # Verify password
            stored_password = self._user_passwords.get(user.user_id)
            if not stored_password or not self.password_service.verify_password(login_request.password, stored_password):
                self._record_failed_login(user.user_id)
                self._log_security_event(
                    action="LOGIN_FAILED",
                    resource=f"user:{user.user_id}",
                    result="INVALID_PASSWORD",
                    details={"email": login_request.email}
                )
                return None
            
            # Clear failed login attempts
            if user.user_id in self._login_attempts:
                del self._login_attempts[user.user_id]
            
            # Create device info
            device_info = self._extract_device_info(login_request.device_info)
            
            # Generate tokens
            access_token = self.jwt_service.generate_access_token(user, device_info)
            refresh_token = self.jwt_service.generate_refresh_token(user, device_info)
            
            # Create session
            session = self.jwt_service.create_session(user, device_info)
            
            # Update user last login
            user.last_login = datetime.utcnow()
            
            # Update metrics
            self._security_metrics.successful_logins += 1
            self._security_metrics.total_logins += 1
            
            # Log successful login
            self._log_security_event(
                action="LOGIN_SUCCESS",
                resource=f"user:{user.user_id}",
                result="SUCCESS",
                details={
                    "email": user.email,
                    "session_id": session.session_id,
                    "device_id": device_info.device_id if device_info else None
                }
            )
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.settings.jwt_expiry_minutes * 60,
                expires_at=datetime.utcnow() + timedelta(minutes=self.settings.jwt_expiry_minutes),
                user=user
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error during login: {e}")
            self._log_security_event(
                action="LOGIN_ERROR",
                resource="authentication",
                result="ERROR",
                details={"error": str(e)}
            )
            return None
    
    def refresh_token(self, refresh_request: RefreshTokenRequest) -> Optional[str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_request: Refresh token request
            
        Returns:
            New access token if successful, None otherwise
        """
        try:
            new_access_token = self.jwt_service.refresh_access_token(refresh_request.refresh_token)
            
            if new_access_token:
                self._log_security_event(
                    action="TOKEN_REFRESHED",
                    resource="authentication",
                    result="SUCCESS",
                    details={"device_info": refresh_request.device_info}
                )
            else:
                self._log_security_event(
                    action="TOKEN_REFRESH_FAILED",
                    resource="authentication",
                    result="INVALID_TOKEN",
                    details={"device_info": refresh_request.device_info}
                )
            
            return new_access_token
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error refreshing token: {e}")
            self._log_security_event(
                action="TOKEN_REFRESH_ERROR",
                resource="authentication",
                result="ERROR",
                details={"error": str(e)}
            )
            return None
    
    def logout(self, logout_request: LogoutRequest, user_context: Optional[UserContext] = None) -> bool:
        """
        Logout user and revoke tokens.
        
        Args:
            logout_request: Logout request
            user_context: Optional user context
            
        Returns:
            True if logout successful, False otherwise
        """
        try:
            if user_context:
                # Revoke all user tokens
                revoked_count = self.jwt_service.revoke_user_tokens(user_context.user_id)
                
                self._log_security_event(
                    action="LOGOUT",
                    resource=f"user:{user_context.user_id}",
                    result="SUCCESS",
                    details={"revoked_tokens": revoked_count}
                )
                
                return True
            else:
                # Revoke specific refresh token
                if logout_request.refresh_token:
                    success = self.jwt_service.revoke_token(logout_request.refresh_token)
                    
                    self._log_security_event(
                        action="LOGOUT_TOKEN",
                        resource="authentication",
                        result="SUCCESS" if success else "FAILED",
                        details={"refresh_token_provided": True}
                    )
                    
                    return success
            
            return False
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error during logout: {e}")
            self._log_security_event(
                action="LOGOUT_ERROR",
                resource="authentication",
                result="ERROR",
                details={"error": str(e)}
            )
            return False
    
    def validate_user_context(self, token: str) -> Optional[UserContext]:
        """
        Validate token and return user context.
        
        Args:
            token: JWT token
            
        Returns:
            User context if valid, None otherwise
        """
        try:
            return self.jwt_service.extract_user_context(token)
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error validating user context: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInfo]:
        """
        Get user information by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User information if found, None otherwise
        """
        return self._users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserInfo]:
        """
        Get user information by email.
        
        Args:
            email: User email
            
        Returns:
            User information if found, None otherwise
        """
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def create_user(self, user_info: UserInfo, password: str) -> bool:
        """
        Create a new user account.
        
        Args:
            user_info: User information
            password: Plain text password
            
        Returns:
            True if user created successfully, False otherwise
        """
        try:
            # Validate password strength
            password_validation = self.password_service.validate_password_strength(password)
            if not password_validation['is_valid']:
                logger.warning(f"Password validation failed: {password_validation['issues']}")
                return False
            
            # Check if user already exists
            if user_info.user_id in self._users or self.get_user_by_email(user_info.email):
                logger.warning(f"User already exists: {user_info.email}")
                return False
            
            # Hash password
            password_hash = self.password_service.hash_password(password)
            
            # Create user
            user_info.created_at = datetime.utcnow()
            user_info.is_active = True
            
            self._users[user_info.user_id] = user_info
            self._user_passwords[user_info.user_id] = password_hash
            
            self._log_security_event(
                action="USER_CREATED",
                resource=f"user:{user_info.user_id}",
                result="SUCCESS",
                details={"email": user_info.email, "roles": [role.value for role in user_info.roles]}
            )
            
            logger.info(f"Created user: {user_info.email}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def update_user_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User identifier
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password updated successfully, False otherwise
        """
        try:
            # Verify old password
            stored_password = self._user_passwords.get(user_id)
            if not stored_password or not self.password_service.verify_password(old_password, stored_password):
                self._log_security_event(
                    action="PASSWORD_UPDATE_FAILED",
                    resource=f"user:{user_id}",
                    result="INVALID_OLD_PASSWORD",
                    details={}
                )
                return False
            
            # Validate new password
            password_validation = self.password_service.validate_password_strength(new_password)
            if not password_validation['is_valid']:
                self._log_security_event(
                    action="PASSWORD_UPDATE_FAILED",
                    resource=f"user:{user_id}",
                    result="WEAK_PASSWORD",
                    details={"issues": password_validation['issues']}
                )
                return False
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(new_password)
            
            # Update password
            self._user_passwords[user_id] = new_password_hash
            
            # Revoke all user tokens for security
            self.jwt_service.revoke_user_tokens(user_id)
            
            self._log_security_event(
                action="PASSWORD_UPDATED",
                resource=f"user:{user_id}",
                result="SUCCESS",
                details={}
            )
            
            logger.info(f"Updated password for user: {user_id}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error updating password: {e}")
            return False
    
    def _check_login_attempts(self, user_id: str) -> bool:
        """Check if user has exceeded maximum login attempts."""
        if user_id not in self._login_attempts:
            return True
        
        attempts = self._login_attempts[user_id]
        now = datetime.utcnow()
        
        # Remove attempts older than lockout duration
        recent_attempts = [
            attempt for attempt in attempts
            if now - attempt < timedelta(minutes=self.settings.lockout_duration_minutes)
        ]
        
        self._login_attempts[user_id] = recent_attempts
        
        return len(recent_attempts) < self.settings.max_login_attempts
    
    def _record_failed_login(self, user_id: str):
        """Record a failed login attempt."""
        if user_id not in self._login_attempts:
            self._login_attempts[user_id] = []
        
        self._login_attempts[user_id].append(datetime.utcnow())
        self._security_metrics.failed_logins += 1
        self._security_metrics.total_logins += 1
        
        # Block user if too many attempts
        if len(self._login_attempts[user_id]) >= self.settings.max_login_attempts:
            block_until = datetime.utcnow() + timedelta(minutes=self.settings.lockout_duration_minutes)
            self._blocked_users[user_id] = block_until
            
            self._log_security_event(
                action="USER_BLOCKED",
                resource=f"user:{user_id}",
                result="TOO_MANY_FAILED_ATTEMPTS",
                details={"blocked_until": block_until.isoformat()}
            )
    
    def _extract_device_info(self, device_info: Optional[Dict[str, Any]]) -> Optional[DeviceInfo]:
        """Extract device information from request."""
        if not device_info:
            return None
        
        try:
            return DeviceInfo(
                device_id=device_info.get('device_id', secrets.token_urlsafe(16)),
                device_type=device_info.get('device_type', 'unknown'),
                os_name=device_info.get('os_name', 'unknown'),
                os_version=device_info.get('os_version', 'unknown'),
                browser_name=device_info.get('browser_name'),
                browser_version=device_info.get('browser_version'),
                app_version=device_info.get('app_version'),
                ip_address=self._get_client_ip(),
                location=device_info.get('location'),
                is_trusted=device_info.get('is_trusted', False)
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error extracting device info: {e}")
            return None
    
    def _get_client_ip(self) -> Optional[str]:
        """Get client IP address from request."""
        try:
            # Check for forwarded headers first
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
            
            # Fallback to remote address
            return request.remote_addr
            
        except Exception:
            return None
    
    def _log_security_event(self, action: str, resource: str, result: str, details: Dict[str, Any]):
        """Log security event."""
        try:
            log_entry = SecurityAuditLog(
                log_id=secrets.token_urlsafe(16),
                action=action,
                resource=resource,
                result=result,
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                timestamp=datetime.utcnow(),
                details=details
            )
            
            self._audit_logs.append(log_entry)
            
            # Keep only last 1000 logs
            if len(self._audit_logs) > 1000:
                self._audit_logs = self._audit_logs[-1000:]
            
            logger.info(f"Security event: {action} on {resource} - {result}")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error logging security event: {e}")
    
    def get_security_metrics(self) -> SecurityMetrics:
        """Get security metrics."""
        return self._security_metrics
    
    def get_audit_logs(self, limit: int = 100) -> List[SecurityAuditLog]:
        """Get recent audit logs."""
        return self._audit_logs[-limit:] if self._audit_logs else []
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired tokens and sessions."""
        return self.jwt_service.cleanup_expired_tokens()
