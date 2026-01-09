"""
Security Middleware for the Python Fraud Detection Agent.
Handles JWT authentication, authorization, and security headers.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from functools import wraps
from flask import request, jsonify, g, current_app
from datetime import datetime

from .security_models import (
    UserContext, SecuritySettings, SecurityAuditLog, Permission, UserRole
)
from .jwt_service import JWTService
from .authentication_service import AuthenticationService
from .authorization_service import AuthorizationService

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for authentication and authorization."""
    
    def __init__(self, settings: SecuritySettings):
        self.settings = settings
        self.jwt_service = JWTService(settings)
        self.auth_service = AuthenticationService(settings)
        self.authz_service = AuthorizationService()
        
        # Rate limiting storage (in-memory for demo)
        self._rate_limit_storage: Dict[str, List[float]] = {}
        
        logger.info("Security Middleware initialized")
    
    def authenticate_request(self, f):
        """
        Decorator to authenticate requests using JWT tokens.
        
        Args:
            f: Flask route function
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extract token from Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return self._unauthorized_response("Missing Authorization header")
                
                # Check Bearer token format
                if not auth_header.startswith('Bearer '):
                    return self._unauthorized_response("Invalid token format")
                
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                
                # Validate token
                user_context = self.jwt_service.extract_user_context(token)
                if not user_context:
                    return self._unauthorized_response("Invalid or expired token")
                
                # Store user context in Flask g object
                g.user_context = user_context
                
                # Log authentication
                self._log_security_event(
                    action="AUTHENTICATE",
                    resource=f"endpoint:{request.endpoint}",
                    result="SUCCESS",
                    details={
                        "user_id": user_context.user_id,
                        "method": request.method,
                        "path": request.path
                    }
                )
                
                return f(*args, **kwargs)
                
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Authentication error: {e}")
                return self._unauthorized_response("Authentication error")
        
        return decorated_function
    
    def require_permission(self, permission: Permission):
        """
        Decorator to require specific permission.
        
        Args:
            permission: Required permission
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Check if user is authenticated
                    if not hasattr(g, 'user_context') or not g.user_context:
                        return self._unauthorized_response("Authentication required")
                    
                    user_context = g.user_context
                    
                    # Check permission
                    if not self.authz_service.has_permission(user_context, permission):
                        self._log_security_event(
                            action="AUTHORIZATION_DENIED",
                            resource=f"endpoint:{request.endpoint}",
                            result="INSUFFICIENT_PERMISSIONS",
                            details={
                                "user_id": user_context.user_id,
                                "required_permission": permission.value,
                                "user_permissions": [p.value for p in user_context.permissions]
                            }
                        )
                        return self._forbidden_response(f"Insufficient permissions: {permission.value}")
                    
                    # Log authorization
                    self._log_security_event(
                        action="AUTHORIZE",
                        resource=f"endpoint:{request.endpoint}",
                        result="SUCCESS",
                        details={
                            "user_id": user_context.user_id,
                            "permission": permission.value,
                            "method": request.method,
                            "path": request.path
                        }
                    )
                    
                    return f(*args, **kwargs)
                    
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Authorization error: {e}")
                    return self._forbidden_response("Authorization error")
            
            return decorated_function
        return decorator
    
    def require_role(self, role: UserRole):
        """
        Decorator to require specific role.
        
        Args:
            role: Required role
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Check if user is authenticated
                    if not hasattr(g, 'user_context') or not g.user_context:
                        return self._unauthorized_response("Authentication required")
                    
                    user_context = g.user_context
                    
                    # Check role
                    if not self.authz_service.has_role(user_context, role):
                        self._log_security_event(
                            action="AUTHORIZATION_DENIED",
                            resource=f"endpoint:{request.endpoint}",
                            result="INSUFFICIENT_ROLE",
                            details={
                                "user_id": user_context.user_id,
                                "required_role": role.value,
                                "user_roles": [r.value for r in user_context.roles]
                            }
                        )
                        return self._forbidden_response(f"Insufficient role: {role.value}")
                    
                    return f(*args, **kwargs)
                    
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Role authorization error: {e}")
                    return self._forbidden_response("Role authorization error")
            
            return decorated_function
        return decorator
    
    def require_policy(self, policy_name: str):
        """
        Decorator to require specific authorization policy.
        
        Args:
            policy_name: Required policy name
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Check if user is authenticated
                    if not hasattr(g, 'user_context') or not g.user_context:
                        return self._unauthorized_response("Authentication required")
                    
                    user_context = g.user_context
                    
                    # Check policy
                    if not self.authz_service.check_policy(user_context, policy_name):
                        self._log_security_event(
                            action="AUTHORIZATION_DENIED",
                            resource=f"endpoint:{request.endpoint}",
                            result="POLICY_VIOLATION",
                            details={
                                "user_id": user_context.user_id,
                                "required_policy": policy_name,
                                "user_roles": [r.value for r in user_context.roles],
                                "user_permissions": [p.value for p in user_context.permissions]
                            }
                        )
                        return self._forbidden_response(f"Policy violation: {policy_name}")
                    
                    return f(*args, **kwargs)
                    
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Policy authorization error: {e}")
                    return self._forbidden_response("Policy authorization error")
            
            return decorated_function
        return decorator
    
    def rate_limit(self, requests_per_minute: int = None):
        """
        Decorator to implement rate limiting.
        
        Args:
            requests_per_minute: Maximum requests per minute
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Get client identifier
                    client_id = self._get_client_identifier()
                    
                    # Use default rate limit if not specified
                    limit = requests_per_minute or self.settings.rate_limit_requests_per_minute
                    
                    # Check rate limit
                    if not self._check_rate_limit(client_id, limit):
                        self._log_security_event(
                            action="RATE_LIMIT_EXCEEDED",
                            resource=f"endpoint:{request.endpoint}",
                            result="RATE_LIMITED",
                            details={
                                "client_id": client_id,
                                "limit": limit,
                                "method": request.method,
                                "path": request.path
                            }
                        )
                        return self._rate_limit_response()
                    
                    return f(*args, **kwargs)
                    
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Rate limiting error: {e}")
                    return f(*args, **kwargs)  # Continue on error
            
            return decorated_function
        return decorator
    
    def add_security_headers(self, f):
        """
        Decorator to add security headers to responses.
        
        Args:
            f: Flask route function
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                response = f(*args, **kwargs)
                
                # Add security headers
                if hasattr(response, 'headers'):
                    self._add_security_headers(response.headers)
                
                return response
                
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Security headers error: {e}")
                return f(*args, **kwargs)
        
        return decorated_function
    
    def audit_request(self, f):
        """
        Decorator to audit requests.
        
        Args:
            f: Flask route function
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Get user context if available
                user_id = None
                if hasattr(g, 'user_context') and g.user_context:
                    user_id = g.user_context.user_id
                
                # Execute the function
                response = f(*args, **kwargs)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Log audit event
                self._log_security_event(
                    action="REQUEST_PROCESSED",
                    resource=f"endpoint:{request.endpoint}",
                    result="SUCCESS",
                    details={
                        "user_id": user_id,
                        "method": request.method,
                        "path": request.path,
                        "processing_time": processing_time,
                        "status_code": getattr(response, 'status_code', 200) if hasattr(response, 'status_code') else 200
                    }
                )
                
                return response
                
            except (ValueError, TypeError, AttributeError) as e:
                processing_time = time.time() - start_time
                
                # Log error audit event
                self._log_security_event(
                    action="REQUEST_ERROR",
                    resource=f"endpoint:{request.endpoint}",
                    result="ERROR",
                    details={
                        "user_id": user_id,
                        "method": request.method,
                        "path": request.path,
                        "processing_time": processing_time,
                        "error": str(e)
                    }
                )
                
                raise
        
        return decorated_function
    
    def _check_rate_limit(self, client_id: str, limit: int) -> bool:
        """Check if client has exceeded rate limit."""
        try:
            now = time.time()
            minute_ago = now - 60
            
            # Get or create client request times
            if client_id not in self._rate_limit_storage:
                self._rate_limit_storage[client_id] = []
            
            request_times = self._rate_limit_storage[client_id]
            
            # Remove requests older than 1 minute
            request_times[:] = [t for t in request_times if t > minute_ago]
            
            # Check if limit exceeded
            if len(request_times) >= limit:
                return False
            
            # Add current request
            request_times.append(now)
            
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    def _get_client_identifier(self) -> str:
        """Get unique client identifier for rate limiting."""
        try:
            # Try to get user ID first
            if hasattr(g, 'user_context') and g.user_context:
                return f"user:{g.user_context.user_id}"
            
            # Fallback to IP address
            ip_address = self._get_client_ip()
            return f"ip:{ip_address}"
            
        except Exception:
            return "unknown"
    
    def _get_client_ip(self) -> str:
        """Get client IP address."""
        try:
            # Check for forwarded headers first
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
            
            # Fallback to remote address
            return request.remote_addr or 'unknown'
            
        except Exception:
            return 'unknown'
    
    def _add_security_headers(self, headers: Dict[str, Any]):
        """Add security headers to response."""
        try:
            # Security headers
            headers['X-Content-Type-Options'] = 'nosniff'
            headers['X-Frame-Options'] = 'DENY'
            headers['X-XSS-Protection'] = '1; mode=block'
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            headers['Content-Security-Policy'] = "default-src 'self'"
            headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error adding security headers: {e}")
    
    def _log_security_event(self, action: str, resource: str, result: str, details: Dict[str, Any]):
        """Log security event."""
        try:
            log_entry = SecurityAuditLog(
                log_id=f"log_{int(time.time() * 1000)}",
                action=action,
                resource=resource,
                result=result,
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                timestamp=datetime.utcnow(),
                details=details
            )
            
            # In a real application, this would be stored in a database
            logger.info(f"Security event: {action} on {resource} - {result}")
            
        except (ValueError) as e:
            logger.error(f"Error logging security event: {e}")
    
    def _unauthorized_response(self, message: str = "Unauthorized"):
        """Return unauthorized response."""
        return jsonify({
            'error': 'Unauthorized',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    def _forbidden_response(self, message: str = "Forbidden"):
        """Return forbidden response."""
        return jsonify({
            'error': 'Forbidden',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    def _rate_limit_response(self):
        """Return rate limit response."""
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'timestamp': datetime.utcnow().isoformat()
        }), 429


def get_current_user() -> Optional[UserContext]:
    """
    Get current authenticated user context.
    
    Returns:
        User context if authenticated, None otherwise
    """
    return getattr(g, 'user_context', None)


def require_auth(f):
    """
    Decorator to require authentication.
    
    Args:
        f: Flask route function
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user_context') or not g.user_context:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
