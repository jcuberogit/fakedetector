"""
JWT Authentication Service for the Python Fraud Detection Agent.
Handles JWT token generation, validation, and user authentication.
"""

import jwt
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import base64
import os

from .security_models import (
    LoginRequest, LoginResponse, RefreshTokenRequest, LogoutRequest,
    UserInfo, UserContext, JWTPayload, SecuritySettings, TokenType,
    UserRole, Permission, DeviceInfo, SessionInfo, SecurityAuditLog
)

logger = logging.getLogger(__name__)


class JWTService:
    """JWT token service for authentication and authorization."""
    
    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        self._secret_key = settings.jwt_secret_key.encode('utf-8')
        self._algorithm = 'HS256'
        
        # In-memory storage for demo (replace with Redis/database in production)
        self._refresh_tokens: Dict[str, Dict[str, Any]] = {}
        self._revoked_tokens: set = set()
        self._user_sessions: Dict[str, SessionInfo] = {}
        
        logger.info("JWT Service initialized")
    
    def generate_access_token(self, user: UserInfo, device_info: Optional[DeviceInfo] = None) -> str:
        """
        Generate JWT access token for user.
        
        Args:
            user: User information
            device_info: Optional device information
            
        Returns:
            JWT access token string
        """
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=self.settings.jwt_expiry_minutes)
            
            payload = JWTPayload(
                sub=user.user_id,
                email=user.email,
                name=user.name,
                roles=[role.value for role in user.roles],
                permissions=[perm.value for perm in user.permissions],
                iat=now,
                exp=expires_at,
                iss=self.settings.jwt_issuer,
                aud=self.settings.jwt_audience,
                jti=secrets.token_urlsafe(32),
                token_type=TokenType.ACCESS,
                device_id=device_info.device_id if device_info else None,
                session_id=secrets.token_urlsafe(32)
            )
            
            token = jwt.encode(
                payload.dict(),
                self._secret_key,
                algorithm=self._algorithm
            )
            
            logger.info(f"Generated access token for user {user.user_id}")
            return token
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error generating access token: {e}")
            raise
    
    def generate_refresh_token(self, user: UserInfo, device_info: Optional[DeviceInfo] = None) -> str:
        """
        Generate JWT refresh token for user.
        
        Args:
            user: User information
            device_info: Optional device information
            
        Returns:
            JWT refresh token string
        """
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(days=self.settings.refresh_token_expiry_days)
            
            payload = JWTPayload(
                sub=user.user_id,
                email=user.email,
                name=user.name,
                roles=[role.value for role in user.roles],
                permissions=[perm.value for perm in user.permissions],
                iat=now,
                exp=expires_at,
                iss=self.settings.jwt_issuer,
                aud=self.settings.jwt_audience,
                jti=secrets.token_urlsafe(32),
                token_type=TokenType.REFRESH,
                device_id=device_info.device_id if device_info else None,
                session_id=secrets.token_urlsafe(32)
            )
            
            token = jwt.encode(
                payload.dict(),
                self._secret_key,
                algorithm=self._algorithm
            )
            
            # Store refresh token for validation
            self._refresh_tokens[payload.jti] = {
                'user_id': user.user_id,
                'device_id': device_info.device_id if device_info else None,
                'created_at': now,
                'expires_at': expires_at,
                'is_active': True
            }
            
            logger.info(f"Generated refresh token for user {user.user_id}")
            return token
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error generating refresh token: {e}")
            raise
    
    def validate_token(self, token: str) -> Optional[JWTPayload]:
        """
        Validate JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            JWT payload if valid, None otherwise
        """
        try:
            # Check if token is revoked
            if token in self._revoked_tokens:
                logger.warning("Token is revoked")
                return None
            
            # Decode and validate token
            payload_dict = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                audience=self.settings.jwt_audience,
                issuer=self.settings.jwt_issuer
            )
            
            payload = JWTPayload(**payload_dict)
            
            # Additional validation
            if payload.exp < datetime.utcnow():
                logger.warning("Token is expired")
                return None
            
            logger.debug(f"Token validated for user {payload.sub}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        try:
            payload = self.validate_token(refresh_token)
            if not payload or payload.token_type != TokenType.REFRESH:
                logger.warning("Invalid refresh token")
                return None
            
            # Check if refresh token exists in storage
            if payload.jti not in self._refresh_tokens:
                logger.warning("Refresh token not found in storage")
                return None
            
            refresh_info = self._refresh_tokens[payload.jti]
            if not refresh_info['is_active']:
                logger.warning("Refresh token is inactive")
                return None
            
            # Create user info from payload
            user = UserInfo(
                user_id=payload.sub,
                email=payload.email,
                name=payload.name,
                roles=[UserRole(role) for role in payload.roles],
                permissions=[Permission(perm) for perm in payload.permissions]
            )
            
            # Generate new access token
            new_access_token = self.generate_access_token(user)
            
            logger.info(f"Refreshed access token for user {payload.sub}")
            return new_access_token
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error refreshing access token: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a JWT token.
        
        Args:
            token: JWT token to revoke
            
        Returns:
            True if token was revoked, False otherwise
        """
        try:
            payload = self.validate_token(token)
            if payload:
                self._revoked_tokens.add(token)
                logger.info(f"Token revoked for user {payload.sub}")
                return True
            return False
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of tokens revoked
        """
        try:
            revoked_count = 0
            
            # Revoke refresh tokens
            for jti, refresh_info in self._refresh_tokens.items():
                if refresh_info['user_id'] == user_id:
                    refresh_info['is_active'] = False
                    revoked_count += 1
            
            # Revoke sessions
            for session_id, session in self._user_sessions.items():
                if session.user_id == user_id:
                    session.is_active = False
                    revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
            return revoked_count
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error revoking user tokens: {e}")
            return 0
    
    def extract_user_context(self, token: str) -> Optional[UserContext]:
        """
        Extract user context from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User context if token is valid, None otherwise
        """
        try:
            payload = self.validate_token(token)
            if not payload:
                return None
            
            return UserContext(
                user_id=payload.sub,
                user_name=payload.name,
                email=payload.email,
                roles=[UserRole(role) for role in payload.roles],
                permissions=[Permission(perm) for perm in payload.permissions],
                claims={
                    'sub': payload.sub,
                    'email': payload.email,
                    'name': payload.name,
                    'iat': payload.iat.isoformat(),
                    'exp': payload.exp.isoformat(),
                    'jti': payload.jti
                },
                session_id=payload.session_id,
                device_id=payload.device_id
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error extracting user context: {e}")
            return None
    
    def create_session(self, user: UserInfo, device_info: Optional[DeviceInfo] = None) -> SessionInfo:
        """
        Create a new user session.
        
        Args:
            user: User information
            device_info: Optional device information
            
        Returns:
            Session information
        """
        try:
            session_id = secrets.token_urlsafe(32)
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=self.settings.jwt_expiry_minutes)
            
            session = SessionInfo(
                session_id=session_id,
                user_id=user.user_id,
                device_id=device_info.device_id if device_info else None,
                created_at=now,
                last_activity=now,
                expires_at=expires_at,
                is_active=True
            )
            
            self._user_sessions[session_id] = session
            
            logger.info(f"Created session {session_id} for user {user.user_id}")
            return session
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def validate_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Validate user session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information if valid, None otherwise
        """
        try:
            if session_id not in self._user_sessions:
                return None
            
            session = self._user_sessions[session_id]
            
            if not session.is_active or session.expires_at < datetime.utcnow():
                session.is_active = False
                return None
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            return session
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens and sessions.
        
        Returns:
            Number of items cleaned up
        """
        try:
            now = datetime.utcnow()
            cleaned_count = 0
            
            # Clean up expired refresh tokens
            expired_refresh_tokens = [
                jti for jti, info in self._refresh_tokens.items()
                if info['expires_at'] < now
            ]
            
            for jti in expired_refresh_tokens:
                del self._refresh_tokens[jti]
                cleaned_count += 1
            
            # Clean up expired sessions
            expired_sessions = [
                session_id for session_id, session in self._user_sessions.items()
                if session.expires_at < now
            ]
            
            for session_id in expired_sessions:
                del self._user_sessions[session_id]
                cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired tokens and sessions")
            return cleaned_count
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0


class PasswordService:
    """Password hashing and validation service."""
    
    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        logger.info("Password Service initialized")
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using PBKDF2 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            # Generate random salt
            salt = os.urandom(32)
            
            # Use PBKDF2 for password hashing
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(password.encode('utf-8'))
            
            # Combine salt and key
            combined = salt + key
            
            # Encode as base64
            hashed = base64.b64encode(combined).decode('utf-8')
            
            return hashed
            
        except (OSError) as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password string
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Decode base64
            combined = base64.b64decode(hashed_password.encode('utf-8'))
            
            # Extract salt and key
            salt = combined[:32]
            stored_key = combined[32:]
            
            # Hash the provided password with the same salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(password.encode('utf-8'))
            
            # Compare keys
            return key == stored_key
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Validation result with details
        """
        try:
            result = {
                'is_valid': True,
                'score': 0,
                'issues': [],
                'suggestions': []
            }
            
            # Length check
            if len(password) < self.settings.password_min_length:
                result['is_valid'] = False
                result['issues'].append(f"Password must be at least {self.settings.password_min_length} characters long")
            else:
                result['score'] += 1
            
            # Character variety checks
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            if has_upper:
                result['score'] += 1
            else:
                result['issues'].append("Password should contain uppercase letters")
                result['suggestions'].append("Add uppercase letters")
            
            if has_lower:
                result['score'] += 1
            else:
                result['issues'].append("Password should contain lowercase letters")
                result['suggestions'].append("Add lowercase letters")
            
            if has_digit:
                result['score'] += 1
            else:
                result['issues'].append("Password should contain numbers")
                result['suggestions'].append("Add numbers")
            
            if has_special:
                result['score'] += 1
            else:
                result['issues'].append("Password should contain special characters")
                result['suggestions'].append("Add special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)")
            
            # Common password check
            common_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
            if password.lower() in common_passwords:
                result['is_valid'] = False
                result['issues'].append("Password is too common")
                result['suggestions'].append("Use a more unique password")
            
            # Overall validation
            if self.settings.require_strong_password and result['score'] < 3:
                result['is_valid'] = False
            
            return result
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error validating password strength: {e}")
            return {
                'is_valid': False,
                'score': 0,
                'issues': ['Password validation error'],
                'suggestions': ['Please try again']
            }
