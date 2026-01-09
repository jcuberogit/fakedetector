"""
Authorization Service for the Python Fraud Detection Agent.
Handles role-based access control and permission validation.
"""

import logging
from typing import List, Dict, Any, Optional, Set
from functools import wraps

from .security_models import (
    UserContext, UserRole, Permission, AuthorizationPolicy,
    SecurityAuditLog
)

logger = logging.getLogger(__name__)


class AuthorizationService:
    """Authorization service for role-based access control."""
    
    def __init__(self):
        # Define role-permission mappings
        self._role_permissions: Dict[UserRole, Set[Permission]] = {
            UserRole.ADMIN: {
                # Full access to all permissions
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
                Permission.DELETE_ML_MODELS,
                Permission.VIEW_GRAPHS,
                Permission.CREATE_GRAPHS,
                Permission.ANALYZE_GRAPHS,
                Permission.DELETE_GRAPHS,
                Permission.VIEW_CONFIG,
                Permission.UPDATE_CONFIG,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.VIEW_SYSTEM_HEALTH,
                Permission.MANAGE_USERS,
                Permission.VIEW_AUDIT_LOGS
            },
            UserRole.ANALYST: {
                # Fraud analysis and investigation permissions
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
            },
            UserRole.LEAD: {
                # Team lead permissions
                Permission.VIEW_FRAUD_ALERTS,
                Permission.CREATE_FRAUD_ALERTS,
                Permission.UPDATE_FRAUD_ALERTS,
                Permission.VIEW_TRANSACTIONS,
                Permission.ANALYZE_TRANSACTIONS,
                Permission.BLOCK_TRANSACTIONS,
                Permission.APPROVE_TRANSACTIONS,
                Permission.VIEW_ML_MODELS,
                Permission.TRAIN_ML_MODELS,
                Permission.VIEW_GRAPHS,
                Permission.CREATE_GRAPHS,
                Permission.ANALYZE_GRAPHS,
                Permission.VIEW_CONFIG,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.VIEW_SYSTEM_HEALTH
            },
            UserRole.USER: {
                # Basic user permissions
                Permission.VIEW_TRANSACTIONS,
                Permission.ANALYZE_TRANSACTIONS,
                Permission.VIEW_FRAUD_ALERTS
            },
            UserRole.CUSTOMER: {
                # Customer permissions
                Permission.VIEW_TRANSACTIONS,
                Permission.ANALYZE_TRANSACTIONS,
                Permission.VIEW_FRAUD_ALERTS
            },
            UserRole.GUEST: {
                # Limited guest permissions
                Permission.VIEW_SYSTEM_HEALTH
            }
        }
        
        # Define authorization policies
        self._policies: Dict[str, AuthorizationPolicy] = {
            'fraud_detection_admin': AuthorizationPolicy(
                name='fraud_detection_admin',
                description='Full fraud detection administration',
                roles=[UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_FRAUD_ALERTS,
                    Permission.CREATE_FRAUD_ALERTS,
                    Permission.UPDATE_FRAUD_ALERTS,
                    Permission.DELETE_FRAUD_ALERTS
                ]
            ),
            'fraud_analysis': AuthorizationPolicy(
                name='fraud_analysis',
                description='Fraud analysis and investigation',
                roles=[UserRole.ANALYST, UserRole.LEAD, UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_FRAUD_ALERTS,
                    Permission.UPDATE_FRAUD_ALERTS,
                    Permission.ANALYZE_TRANSACTIONS
                ]
            ),
            'transaction_management': AuthorizationPolicy(
                name='transaction_management',
                description='Transaction management and control',
                roles=[UserRole.ANALYST, UserRole.LEAD, UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_TRANSACTIONS,
                    Permission.BLOCK_TRANSACTIONS,
                    Permission.APPROVE_TRANSACTIONS
                ]
            ),
            'ml_model_management': AuthorizationPolicy(
                name='ml_model_management',
                description='ML model training and deployment',
                roles=[UserRole.LEAD, UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_ML_MODELS,
                    Permission.TRAIN_ML_MODELS,
                    Permission.DEPLOY_ML_MODELS,
                    Permission.DELETE_ML_MODELS
                ]
            ),
            'graph_analysis': AuthorizationPolicy(
                name='graph_analysis',
                description='Graph neural network analysis',
                roles=[UserRole.ANALYST, UserRole.LEAD, UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_GRAPHS,
                    Permission.CREATE_GRAPHS,
                    Permission.ANALYZE_GRAPHS
                ]
            ),
            'system_configuration': AuthorizationPolicy(
                name='system_configuration',
                description='System configuration management',
                roles=[UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_CONFIG,
                    Permission.UPDATE_CONFIG
                ]
            ),
            'user_management': AuthorizationPolicy(
                name='user_management',
                description='User account management',
                roles=[UserRole.ADMIN],
                permissions=[
                    Permission.MANAGE_USERS
                ]
            ),
            'audit_access': AuthorizationPolicy(
                name='audit_access',
                description='Audit log access',
                roles=[UserRole.ADMIN],
                permissions=[
                    Permission.VIEW_AUDIT_LOGS
                ]
            )
        }
        
        logger.info("Authorization Service initialized")
    
    def has_permission(self, user_context: UserContext, permission: Permission) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_context: User context
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Check if user has permission directly
            if permission in user_context.permissions:
                return True
            
            # Check if user has permission through roles
            for role in user_context.roles:
                if role in self._role_permissions:
                    if permission in self._role_permissions[role]:
                        return True
            
            logger.debug(f"User {user_context.user_id} does not have permission {permission.value}")
            return False
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    def has_role(self, user_context: UserContext, role: UserRole) -> bool:
        """
        Check if user has specific role.
        
        Args:
            user_context: User context
            role: Role to check
            
        Returns:
            True if user has role, False otherwise
        """
        try:
            return role in user_context.roles
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking role: {e}")
            return False
    
    def has_any_role(self, user_context: UserContext, roles: List[UserRole]) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            user_context: User context
            roles: List of roles to check
            
        Returns:
            True if user has any of the roles, False otherwise
        """
        try:
            return any(role in user_context.roles for role in roles)
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking roles: {e}")
            return False
    
    def has_all_permissions(self, user_context: UserContext, permissions: List[Permission]) -> bool:
        """
        Check if user has all specified permissions.
        
        Args:
            user_context: User context
            permissions: List of permissions to check
            
        Returns:
            True if user has all permissions, False otherwise
        """
        try:
            return all(self.has_permission(user_context, perm) for perm in permissions)
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking permissions: {e}")
            return False
    
    def has_any_permission(self, user_context: UserContext, permissions: List[Permission]) -> bool:
        """
        Check if user has any of the specified permissions.
        
        Args:
            user_context: User context
            permissions: List of permissions to check
            
        Returns:
            True if user has any of the permissions, False otherwise
        """
        try:
            return any(self.has_permission(user_context, perm) for perm in permissions)
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking permissions: {e}")
            return False
    
    def check_policy(self, user_context: UserContext, policy_name: str) -> bool:
        """
        Check if user satisfies authorization policy.
        
        Args:
            user_context: User context
            policy_name: Policy name to check
            
        Returns:
            True if user satisfies policy, False otherwise
        """
        try:
            if policy_name not in self._policies:
                logger.warning(f"Policy not found: {policy_name}")
                return False
            
            policy = self._policies[policy_name]
            
            if not policy.is_active:
                logger.debug(f"Policy {policy_name} is inactive")
                return False
            
            # Check roles
            if policy.roles and not self.has_any_role(user_context, policy.roles):
                logger.debug(f"User {user_context.user_id} does not have required roles for policy {policy_name}")
                return False
            
            # Check permissions
            if policy.permissions and not self.has_all_permissions(user_context, policy.permissions):
                logger.debug(f"User {user_context.user_id} does not have required permissions for policy {policy_name}")
                return False
            
            # Check additional conditions
            if policy.conditions:
                if not self._evaluate_conditions(user_context, policy.conditions):
                    logger.debug(f"User {user_context.user_id} does not satisfy conditions for policy {policy_name}")
                    return False
            
            logger.debug(f"User {user_context.user_id} satisfies policy {policy_name}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error checking policy: {e}")
            return False
    
    def get_user_permissions(self, user_context: UserContext) -> Set[Permission]:
        """
        Get all permissions for user (from roles and direct permissions).
        
        Args:
            user_context: User context
            
        Returns:
            Set of all user permissions
        """
        try:
            permissions = set(user_context.permissions)
            
            # Add permissions from roles
            for role in user_context.roles:
                if role in self._role_permissions:
                    permissions.update(self._role_permissions[role])
            
            return permissions
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error getting user permissions: {e}")
            return set()
    
    def get_accessible_resources(self, user_context: UserContext) -> Dict[str, List[str]]:
        """
        Get list of resources user can access based on permissions.
        
        Args:
            user_context: User context
            
        Returns:
            Dictionary of resource types and accessible resource IDs
        """
        try:
            resources = {
                'fraud_alerts': [],
                'transactions': [],
                'ml_models': [],
                'graphs': [],
                'users': [],
                'config': [],
                'analytics': [],
                'audit_logs': []
            }
            
            permissions = self.get_user_permissions(user_context)
            
            # Map permissions to resources
            if Permission.VIEW_FRAUD_ALERTS in permissions:
                resources['fraud_alerts'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_TRANSACTIONS in permissions:
                resources['transactions'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_ML_MODELS in permissions:
                resources['ml_models'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_GRAPHS in permissions:
                resources['graphs'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.MANAGE_USERS in permissions:
                resources['users'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_CONFIG in permissions:
                resources['config'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_ANALYTICS in permissions:
                resources['analytics'] = ['all']  # Simplified - in real app, filter by user access
            
            if Permission.VIEW_AUDIT_LOGS in permissions:
                resources['audit_logs'] = ['all']  # Simplified - in real app, filter by user access
            
            return resources
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error getting accessible resources: {e}")
            return {}
    
    def create_policy(self, policy: AuthorizationPolicy) -> bool:
        """
        Create new authorization policy.
        
        Args:
            policy: Policy to create
            
        Returns:
            True if policy created successfully, False otherwise
        """
        try:
            self._policies[policy.name] = policy
            logger.info(f"Created authorization policy: {policy.name}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error creating policy: {e}")
            return False
    
    def update_policy(self, policy_name: str, policy: AuthorizationPolicy) -> bool:
        """
        Update existing authorization policy.
        
        Args:
            policy_name: Name of policy to update
            policy: Updated policy
            
        Returns:
            True if policy updated successfully, False otherwise
        """
        try:
            if policy_name not in self._policies:
                logger.warning(f"Policy not found: {policy_name}")
                return False
            
            self._policies[policy_name] = policy
            logger.info(f"Updated authorization policy: {policy_name}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error updating policy: {e}")
            return False
    
    def delete_policy(self, policy_name: str) -> bool:
        """
        Delete authorization policy.
        
        Args:
            policy_name: Name of policy to delete
            
        Returns:
            True if policy deleted successfully, False otherwise
        """
        try:
            if policy_name not in self._policies:
                logger.warning(f"Policy not found: {policy_name}")
                return False
            
            del self._policies[policy_name]
            logger.info(f"Deleted authorization policy: {policy_name}")
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error deleting policy: {e}")
            return False
    
    def get_policy(self, policy_name: str) -> Optional[AuthorizationPolicy]:
        """
        Get authorization policy by name.
        
        Args:
            policy_name: Name of policy
            
        Returns:
            Policy if found, None otherwise
        """
        return self._policies.get(policy_name)
    
    def list_policies(self) -> List[AuthorizationPolicy]:
        """
        List all authorization policies.
        
        Returns:
            List of all policies
        """
        return list(self._policies.values())
    
    def _evaluate_conditions(self, user_context: UserContext, conditions: Dict[str, Any]) -> bool:
        """
        Evaluate additional policy conditions.
        
        Args:
            user_context: User context
            conditions: Conditions to evaluate
            
        Returns:
            True if conditions are satisfied, False otherwise
        """
        try:
            # Example conditions (can be extended)
            for condition_type, condition_value in conditions.items():
                if condition_type == 'time_based':
                    # Check if access is allowed at current time
                    current_hour = user_context.authenticated_at.hour
                    allowed_hours = condition_value.get('allowed_hours', [])
                    if allowed_hours and current_hour not in allowed_hours:
                        return False
                
                elif condition_type == 'ip_whitelist':
                    # Check if user IP is in whitelist
                    user_ip = user_context.claims.get('ip_address')
                    allowed_ips = condition_value.get('allowed_ips', [])
                    if allowed_ips and user_ip not in allowed_ips:
                        return False
                
                elif condition_type == 'device_trusted':
                    # Check if device is trusted
                    device_trusted = condition_value.get('require_trusted_device', False)
                    if device_trusted and not user_context.device_info.get('is_trusted', False):
                        return False
            
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False


def require_permission(permission: Permission):
    """
    Decorator to require specific permission for endpoint access.
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the Flask route handler
            # For now, just return the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """
    Decorator to require specific role for endpoint access.
    
    Args:
        role: Required role
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the Flask route handler
            # For now, just return the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_policy(policy_name: str):
    """
    Decorator to require specific authorization policy for endpoint access.
    
    Args:
        policy_name: Required policy name
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be implemented in the Flask route handler
            # For now, just return the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator
