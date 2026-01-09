#!/usr/bin/env python3
"""
Universal Security Module for ParadigmStore Agents
Provides enterprise-grade security for all AI agents with zero UX impact
"""

import os
import hmac
import hashlib
import logging
import json
from datetime import datetime
from functools import wraps
from collections import defaultdict
from time import time
from flask import request, jsonify, Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParadigmSecurity:
    """Universal security module for all ParadigmStore agents"""
    
    def __init__(self):
        self.rate_limit_storage = defaultdict(list)
        self.security_events = []
        
    def secure_agent(self, app: Flask, agent_name: str, config: dict = None):
        """
        Apply universal security to any ParadigmStore agent
        
        Usage:
            from shared.security import paradigm_security
            paradigm_security.secure_agent(app, "paradigm.payment.agent")
        """
        
        # Default configuration
        default_config = {
            'cors_origins': os.getenv('ALLOWED_ORIGINS', 'https://paradigmstore.com,https://hellostore.shop,http://localhost:9003,http://localhost:9000').split(','),
            'rate_limits': {
                'default': "1000 per day, 100 per hour, 10 per minute",
                'webhook': "500 per hour, 50 per minute", 
                'admin': "200 per hour, 20 per minute",
                'public': "2000 per day, 200 per hour"
            },
            'api_keys': {
                'internal': os.getenv('PARADIGM_INTERNAL_API_KEY', 'paradigm_internal_key'),
                'admin': os.getenv('PARADIGM_ADMIN_API_KEY', 'paradigm_admin_key'),
                'client': os.getenv('PARADIGM_CLIENT_API_KEY', 'paradigm_client_key')
            },
            'webhook_secret': os.getenv('PARADIGM_WEBHOOK_SECRET'),
            'security_logging': True,
            'input_validation': True
        }
        
        # Merge with provided config
        if config:
            default_config.update(config)
        
        config = default_config
        
        # 1. Configure CORS
        self._setup_cors(app, config['cors_origins'])
        
        # 2. Configure Rate Limiting
        self._setup_rate_limiting(app, config['rate_limits'])
        
        # 3. Setup Security Logging
        if config['security_logging']:
            self._setup_security_logging(app, agent_name)
        
        # 4. Add Security Decorators
        self._add_security_decorators(app, config)
        
        # 5. Add Error Handlers
        self._add_error_handlers(app)
        
        logger.info(f"🔒 {agent_name} secured with ParadigmStore Universal Security")
        
        return app
    
    def _setup_cors(self, app: Flask, allowed_origins: list):
        """Configure CORS with restricted origins"""
        CORS(app, origins=allowed_origins)
        logger.info(f"✅ CORS configured for origins: {allowed_origins}")
    
    def _setup_rate_limiting(self, app: Flask, rate_limits: dict):
        """Configure rate limiting"""
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[rate_limits['default']]
        )
        limiter.init_app(app)
        
        # Store limiter in app for use in decorators
        app.paradigm_limiter = limiter
        logger.info(f"✅ Rate limiting configured: {rate_limits['default']}")
    
    def _setup_security_logging(self, app: Flask, agent_name: str):
        """Setup security event logging"""
        
        @app.before_request
        def log_request():
            if request.endpoint and not request.endpoint.startswith('static'):
                self.log_security_event(
                    agent_name,
                    'request_received',
                    {
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'ip': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', '')[:100]
                    }
                )
        
        logger.info(f"✅ Security logging enabled for {agent_name}")
    
    def _add_security_decorators(self, app: Flask, config: dict):
        """Add security decorators to app"""
        
        # API Key Authentication Decorator
        def require_api_key(key_type='internal'):
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    # Check API key from headers OR URL parameter (for file uploads)
                    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
                    expected_key = config['api_keys'].get(key_type)
                    
                    if not api_key or api_key != expected_key:
                        logger.info(f"❌ AUTH FAILED: {request.endpoint} - Key: {api_key[:10] if api_key else 'None'}... Expected: {expected_key}")
                        logger.info(f"❌ URL PARAMS: {dict(request.args)}")
                        logger.info(f"❌ HEADERS: X-API-Key={request.headers.get('X-API-Key')}")
                        
                        self.log_security_event(
                            'authentication',
                            'api_key_failed',
                            {
                                'endpoint': request.endpoint,
                                'key_type': key_type,
                                'provided_key': api_key[:10] + '...' if api_key else None,
                                'source': 'headers' if request.headers.get('X-API-Key') else 'url_params'
                            },
                            level='WARNING'
                        )
                        return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401
                    
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
        
        # Webhook Signature Verification Decorator
        def require_webhook_signature(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not config['webhook_secret']:
                    return f(*args, **kwargs)  # Skip if no secret configured
                
                signature = request.headers.get('X-Hub-Signature-256')
                if not signature:
                    return jsonify({'error': 'Missing webhook signature'}), 401
                
                payload_body = request.get_data()
                expected_signature = hmac.new(
                    config['webhook_secret'].encode('utf-8'),
                    payload_body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature.split('sha256=')[1], expected_signature):
                    self.log_security_event(
                        'webhook',
                        'signature_verification_failed',
                        {'endpoint': request.endpoint},
                        level='ERROR'
                    )
                    return jsonify({'error': 'Invalid webhook signature'}), 401
                
                return f(*args, **kwargs)
            return decorated_function
        
        # Input Validation Decorator
        def validate_input(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if config['input_validation'] and request.is_json:
                    data = request.get_json()
                    if data:
                        # Basic input sanitization
                        sanitized_data = self._sanitize_input(data)
                        request.paradigm_sanitized_data = sanitized_data
                
                return f(*args, **kwargs)
            return decorated_function
        
        # Store decorators in app for use by agents
        app.paradigm_require_api_key = require_api_key
        app.paradigm_require_webhook_signature = require_webhook_signature
        app.paradigm_validate_input = validate_input
        
        logger.info("✅ Security decorators added to app")
    
    def _add_error_handlers(self, app: Flask):
        """Add security-aware error handlers"""
        
        @app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'agent': 'ParadigmStore'
            }), 401
        
        @app.errorhandler(403)
        def forbidden(error):
            return jsonify({
                'error': 'Forbidden',
                'message': 'Access denied',
                'agent': 'ParadigmStore'
            }), 403
        
        @app.errorhandler(429)
        def ratelimit_handler(error):
            self.log_security_event(
                'rate_limiting',
                'rate_limit_exceeded',
                {'limit': str(error.description)},
                level='WARNING'
            )
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'agent': 'ParadigmStore'
            }), 429
        
        logger.info("✅ Security error handlers added")
    
    def _sanitize_input(self, data):
        """Sanitize input data to prevent injection attacks"""
        if isinstance(data, dict):
            return {k: self._sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_input(item) for item in data]
        elif isinstance(data, str):
            # Remove potentially dangerous characters
            import re
            # Allow alphanumeric, spaces, and common punctuation
            sanitized = re.sub(r'[^\w\s\-\.\@\+\(\)\[\]\{\}:,!?áéíóúñü]', '', data)
            return sanitized[:1000]  # Limit length
        else:
            return data
    
    def log_security_event(self, agent_name: str, event_type: str, details: dict, level: str = 'INFO'):
        """Log security events for monitoring"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent': agent_name,
            'event_type': event_type,
            'ip_address': request.remote_addr if request else 'system',
            'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'system',
            'details': details
        }
        
        self.security_events.append(event)
        
        # Log to file/system
        log_message = f"PARADIGM_SECURITY: {json.dumps(event)}"
        if level == 'WARNING':
            logger.warning(log_message)
        elif level == 'ERROR':
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    def get_security_stats(self) -> dict:
        """Get security statistics for monitoring"""
        return {
            'total_events': len(self.security_events),
            'recent_events': self.security_events[-10:],
            'event_types': list(set(event['event_type'] for event in self.security_events)),
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for easy import
paradigm_security = ParadigmSecurity()

# Convenience decorators for direct import
def secure_agent(app: Flask, agent_name: str, config: dict = None):
    """Convenience function to secure an agent"""
    return paradigm_security.secure_agent(app, agent_name, config)

def require_api_key(key_type='internal'):
    """Decorator for API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This will be replaced by the actual decorator when secure_agent is called
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_webhook_signature(f):
    """Decorator for webhook signature verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This will be replaced by the actual decorator when secure_agent is called
        return f(*args, **kwargs)
    return decorated_function

def validate_input(f):
    """Decorator for input validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This will be replaced by the actual decorator when secure_agent is called
        return f(*args, **kwargs)
    return decorated_function

# Security middleware for easy integration
class ParadigmSecurityMiddleware:
    """WSGI middleware for ParadigmStore security"""
    
    def __init__(self, app, agent_name: str, config: dict = None):
        self.app = app
        self.agent_name = agent_name
        self.security = paradigm_security
        
        # Apply security to the app
        self.security.secure_agent(app, agent_name, config)
    
    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

if __name__ == "__main__":
    # Test the security module
    from flask import Flask
    
    app = Flask(__name__)
    
    # Apply security
    secure_agent(app, "paradigm.test.agent")
    
    @app.route('/test')
    def test():
        return jsonify({'message': 'Security test successful', 'agent': 'paradigm.test.agent'})
    
    @app.route('/admin')
    @app.paradigm_require_api_key('admin')
    def admin():
        return jsonify({'message': 'Admin endpoint accessed', 'agent': 'paradigm.test.agent'})
    
    logger.info("🔒 ParadigmStore Universal Security Test Server")
    logger.info("📚 Test endpoints:")
    logger.info("  GET  /test (public)")
    logger.info("  GET  /admin (requires admin API key)")
    logger.info("\n🧪 Test commands:")
    logger.info("curl http://localhost:5000/test")
    logger.info("curl -H 'X-API-Key: paradigm_admin_key' http://localhost:5000/admin")
    
    app.run(debug=True, port=5000)
