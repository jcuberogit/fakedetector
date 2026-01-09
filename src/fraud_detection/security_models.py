"""
Security models for the Python Fraud Detection Agent.
Mirrors the C# security system with JWT authentication and authorization.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum


class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "Admin"
    ANALYST = "Analyst"
    LEAD = "Lead"
    USER = "User"
    CUSTOMER = "Customer"
    GUEST = "Guest"


class Permission(str, Enum):
    """Permissions for fine-grained access control."""
    # Fraud Detection Permissions
    VIEW_FRAUD_ALERTS = "view_fraud_alerts"
    CREATE_FRAUD_ALERTS = "create_fraud_alerts"
    UPDATE_FRAUD_ALERTS = "update_fraud_alerts"
    DELETE_FRAUD_ALERTS = "delete_fraud_alerts"
    
    # Transaction Permissions
    VIEW_TRANSACTIONS = "view_transactions"
    ANALYZE_TRANSACTIONS = "analyze_transactions"
    BLOCK_TRANSACTIONS = "block_transactions"
    APPROVE_TRANSACTIONS = "approve_transactions"
    
    # ML Model Permissions
    VIEW_ML_MODELS = "view_ml_models"
    TRAIN_ML_MODELS = "train_ml_models"
    DEPLOY_ML_MODELS = "deploy_ml_models"
    DELETE_ML_MODELS = "delete_ml_models"
    
    # GNN Permissions
    VIEW_GRAPHS = "view_graphs"
    CREATE_GRAPHS = "create_graphs"
    ANALYZE_GRAPHS = "analyze_graphs"
    DELETE_GRAPHS = "delete_graphs"
    
    # Configuration Permissions
    VIEW_CONFIG = "view_config"
    UPDATE_CONFIG = "update_config"
    
    # Analytics Permissions
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # System Permissions
    VIEW_SYSTEM_HEALTH = "view_system_health"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"


class TokenType(str, Enum):
    """JWT token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"


class LoginRequest(BaseModel):
    """Login request model."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Remember user session")
    device_info: Optional[Dict[str, Any]] = Field(default=None, description="Device information")


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    user: 'UserInfo' = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="Refresh token")
    device_info: Optional[Dict[str, Any]] = Field(default=None, description="Device information")


class LogoutRequest(BaseModel):
    """Logout request model."""
    refresh_token: Optional[str] = Field(default=None, description="Refresh token to revoke")
    logout_all_devices: bool = Field(default=False, description="Logout from all devices")


class UserInfo(BaseModel):
    """User information model."""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    roles: List[UserRole] = Field(default_factory=list, description="User roles")
    permissions: List[Permission] = Field(default_factory=list, description="User permissions")
    account_id: Optional[str] = Field(default=None, description="Associated account ID")
    is_active: bool = Field(default=True, description="User account status")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")


class UserContext(BaseModel):
    """User context for request processing."""
    user_id: str = Field(..., description="User identifier")
    user_name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    roles: List[UserRole] = Field(default_factory=list, description="User roles")
    permissions: List[Permission] = Field(default_factory=list, description="User permissions")
    claims: Dict[str, str] = Field(default_factory=dict, description="JWT claims")
    authenticated_at: datetime = Field(default_factory=datetime.utcnow, description="Authentication timestamp")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    device_info: Optional[Dict[str, Any]] = Field(default=None, description="Device information")


class JWTPayload(BaseModel):
    """JWT token payload."""
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    iat: datetime = Field(default_factory=datetime.utcnow, description="Issued at")
    exp: datetime = Field(..., description="Expiration time")
    iss: str = Field(..., description="Issuer")
    aud: str = Field(..., description="Audience")
    jti: str = Field(..., description="JWT ID")
    token_type: TokenType = Field(default=TokenType.ACCESS, description="Token type")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    jwt_secret_key: str = Field(..., description="JWT signing secret key")
    jwt_issuer: str = Field(default="FraudDetectionAgent", description="JWT issuer")
    jwt_audience: str = Field(default="FraudDetectionAgent.Users", description="JWT audience")
    jwt_expiry_minutes: int = Field(default=60, description="JWT expiration time in minutes")
    refresh_token_expiry_days: int = Field(default=30, description="Refresh token expiration in days")
    api_key_expiry_days: int = Field(default=365, description="API key expiration in days")
    max_login_attempts: int = Field(default=5, description="Maximum login attempts")
    lockout_duration_minutes: int = Field(default=15, description="Account lockout duration")
    password_min_length: int = Field(default=8, description="Minimum password length")
    require_strong_password: bool = Field(default=True, description="Require strong passwords")
    enable_two_factor: bool = Field(default=False, description="Enable two-factor authentication")
    enable_device_tracking: bool = Field(default=True, description="Enable device tracking")
    enable_session_management: bool = Field(default=True, description="Enable session management")
    enable_audit_logging: bool = Field(default=True, description="Enable security audit logging")
    cors_allowed_origins: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed origins")
    cors_allowed_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"], description="CORS allowed methods")
    cors_allowed_headers: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed headers")
    rate_limit_requests_per_minute: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_burst_size: int = Field(default=200, description="Rate limit burst size")


class AuthorizationPolicy(BaseModel):
    """Authorization policy definition."""
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    roles: List[UserRole] = Field(default_factory=list, description="Required roles")
    permissions: List[Permission] = Field(default_factory=list, description="Required permissions")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions")
    is_active: bool = Field(default=True, description="Policy status")


class SecurityAuditLog(BaseModel):
    """Security audit log entry."""
    log_id: str = Field(..., description="Unique log identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource accessed")
    result: str = Field(..., description="Action result")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    severity: str = Field(default="INFO", description="Log severity level")


class DeviceInfo(BaseModel):
    """Device information model."""
    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(..., description="Device type (mobile, desktop, etc.)")
    os_name: str = Field(..., description="Operating system name")
    os_version: str = Field(..., description="Operating system version")
    browser_name: Optional[str] = Field(default=None, description="Browser name")
    browser_version: Optional[str] = Field(default=None, description="Browser version")
    app_version: Optional[str] = Field(default=None, description="Application version")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    location: Optional[Dict[str, Any]] = Field(default=None, description="Geographic location")
    is_trusted: bool = Field(default=False, description="Trusted device status")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen timestamp")


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_active: bool = Field(default=True, description="Session status")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class ApiKeyInfo(BaseModel):
    """API key information model."""
    key_id: str = Field(..., description="Unique key identifier")
    name: str = Field(..., description="Key name")
    description: Optional[str] = Field(default=None, description="Key description")
    user_id: str = Field(..., description="Associated user ID")
    permissions: List[Permission] = Field(default_factory=list, description="Key permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Expiration timestamp")
    last_used: Optional[datetime] = Field(default=None, description="Last usage timestamp")
    usage_count: int = Field(default=0, description="Usage count")
    is_active: bool = Field(default=True, description="Key status")
    rate_limit_per_minute: int = Field(default=1000, description="Rate limit per minute")
    allowed_ips: List[str] = Field(default_factory=list, description="Allowed IP addresses")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SecurityMetrics(BaseModel):
    """Security metrics model."""
    total_logins: int = Field(default=0, description="Total login attempts")
    successful_logins: int = Field(default=0, description="Successful logins")
    failed_logins: int = Field(default=0, description="Failed logins")
    blocked_ips: int = Field(default=0, description="Blocked IP addresses")
    active_sessions: int = Field(default=0, description="Active sessions")
    revoked_tokens: int = Field(default=0, description="Revoked tokens")
    security_alerts: int = Field(default=0, description="Security alerts")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


# Update forward references
LoginResponse.model_rebuild()
