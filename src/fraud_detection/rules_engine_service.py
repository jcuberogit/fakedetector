"""
Advanced Rules Engine Service
Migrated from C# FraudDetectionAgent.Api.Services.RuleEngine
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from .rules_engine_models import (
    DynamicRule, RuleCondition, RuleAction, RuleResult, RuleEvaluationResult,
    RuleOperator, RuleActionType, RuleManagementRequest, RuleManagementResponse,
    RuleStatistics, RuleTemplate, RuleValidationResult, RuleTestResult
)
from .static_rules import IRule, get_default_static_rules
from .fraud_tools_models import RiskFactor, RiskLevel

logger = logging.getLogger(__name__)


class RuleManagementService:
    """Service for managing dynamic rules"""
    
    def __init__(self):
        self.rules: Dict[str, DynamicRule] = {}
        self.rule_statistics = {
            'total_evaluations': 0,
            'successful_evaluations': 0,
            'failed_evaluations': 0,
            'rule_trigger_counts': {},
            'execution_times': []
        }
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize with some default dynamic rules"""
        default_rules = [
            DynamicRule(
                name="High Amount Weekend Rule",
                description="Block high amounts on weekends",
                priority=10,
                conditions=[
                    RuleCondition(
                        field="amount",
                        operator=RuleOperator.GREATER_THAN,
                        value=5000,
                        description="Amount greater than $5000"
                    ),
                    RuleCondition(
                        field="day_of_week",
                        operator=RuleOperator.IN,
                        value=["Saturday", "Sunday"],
                        description="Weekend day"
                    )
                ],
                action=RuleAction(
                    type=RuleActionType.BLOCK_TRANSACTION,
                    parameters={"reason": "High amount on weekend"},
                    description="Block transaction"
                )
            ),
            DynamicRule(
                name="Rapid Successive Transactions",
                description="Alert on rapid successive transactions",
                priority=20,
                conditions=[
                    RuleCondition(
                        field="time_since_last_transaction",
                        operator=RuleOperator.LESS_THAN,
                        value=60,  # seconds
                        description="Less than 60 seconds since last transaction"
                    ),
                    RuleCondition(
                        field="amount",
                        operator=RuleOperator.GREATER_THAN,
                        value=1000,
                        description="Amount greater than $1000"
                    )
                ],
                action=RuleAction(
                    type=RuleActionType.MANUAL_REVIEW,
                    parameters={"reason": "Rapid successive transactions"},
                    description="Require manual review"
                )
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
    
    async def get_all_rules_async(self) -> List[DynamicRule]:
        """Get all dynamic rules"""
        return list(self.rules.values())
    
    async def get_rule_async(self, rule_id: str) -> Optional[DynamicRule]:
        """Get a specific rule by ID"""
        return self.rules.get(rule_id)
    
    async def create_rule_async(self, rule: DynamicRule) -> RuleManagementResponse:
        """Create a new rule"""
        try:
            # Validate rule
            validation = self.validate_rule(rule)
            if not validation.is_valid:
                return RuleManagementResponse(
                    success=False,
                    message="Rule validation failed",
                    error="; ".join(validation.errors)
                )
            
            self.rules[rule.rule_id] = rule
            logger.info(f"Created rule: {rule.name} ({rule.rule_id})")
            
            return RuleManagementResponse(
                success=True,
                message=f"Rule '{rule.name}' created successfully",
                rule=rule
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error creating rule: {e}")
            return RuleManagementResponse(
                success=False,
                message="Failed to create rule",
                error=str(e)
            )
    
    async def update_rule_async(self, rule_id: str, rule: DynamicRule) -> RuleManagementResponse:
        """Update an existing rule"""
        try:
            if rule_id not in self.rules:
                return RuleManagementResponse(
                    success=False,
                    message="Rule not found",
                    error=f"Rule {rule_id} does not exist"
                )
            
            # Validate rule
            validation = self.validate_rule(rule)
            if not validation.is_valid:
                return RuleManagementResponse(
                    success=False,
                    message="Rule validation failed",
                    error="; ".join(validation.errors)
                )
            
            rule.updated_at = datetime.utcnow()
            rule.version += 1
            self.rules[rule_id] = rule
            
            logger.info(f"Updated rule: {rule.name} ({rule_id})")
            
            return RuleManagementResponse(
                success=True,
                message=f"Rule '{rule.name}' updated successfully",
                rule=rule
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error updating rule: {e}")
            return RuleManagementResponse(
                success=False,
                message="Failed to update rule",
                error=str(e)
            )
    
    async def delete_rule_async(self, rule_id: str) -> RuleManagementResponse:
        """Delete a rule"""
        try:
            if rule_id not in self.rules:
                return RuleManagementResponse(
                    success=False,
                    message="Rule not found",
                    error=f"Rule {rule_id} does not exist"
                )
            
            rule_name = self.rules[rule_id].name
            del self.rules[rule_id]
            
            logger.info(f"Deleted rule: {rule_name} ({rule_id})")
            
            return RuleManagementResponse(
                success=True,
                message=f"Rule '{rule_name}' deleted successfully"
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error deleting rule: {e}")
            return RuleManagementResponse(
                success=False,
                message="Failed to delete rule",
                error=str(e)
            )
    
    async def enable_rule_async(self, rule_id: str) -> RuleManagementResponse:
        """Enable a rule"""
        try:
            if rule_id not in self.rules:
                return RuleManagementResponse(
                    success=False,
                    message="Rule not found",
                    error=f"Rule {rule_id} does not exist"
                )
            
            self.rules[rule_id].is_enabled = True
            self.rules[rule_id].updated_at = datetime.utcnow()
            
            logger.info(f"Enabled rule: {self.rules[rule_id].name} ({rule_id})")
            
            return RuleManagementResponse(
                success=True,
                message=f"Rule '{self.rules[rule_id].name}' enabled successfully",
                rule=self.rules[rule_id]
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error enabling rule: {e}")
            return RuleManagementResponse(
                success=False,
                message="Failed to enable rule",
                error=str(e)
            )
    
    async def disable_rule_async(self, rule_id: str) -> RuleManagementResponse:
        """Disable a rule"""
        try:
            if rule_id not in self.rules:
                return RuleManagementResponse(
                    success=False,
                    message="Rule not found",
                    error=f"Rule {rule_id} does not exist"
                )
            
            self.rules[rule_id].is_enabled = False
            self.rules[rule_id].updated_at = datetime.utcnow()
            
            logger.info(f"Disabled rule: {self.rules[rule_id].name} ({rule_id})")
            
            return RuleManagementResponse(
                success=True,
                message=f"Rule '{self.rules[rule_id].name}' disabled successfully",
                rule=self.rules[rule_id]
            )
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error disabling rule: {e}")
            return RuleManagementResponse(
                success=False,
                message="Failed to disable rule",
                error=str(e)
            )
    
    def validate_rule(self, rule: DynamicRule) -> RuleValidationResult:
        """Validate a rule"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check rule name
        if not rule.name or len(rule.name.strip()) == 0:
            errors.append("Rule name is required")
        
        # Check conditions
        if not rule.conditions:
            errors.append("Rule must have at least one condition")
        
        for i, condition in enumerate(rule.conditions):
            if not condition.field:
                errors.append(f"Condition {i+1}: Field is required")
            
            if not condition.operator:
                errors.append(f"Condition {i+1}: Operator is required")
            
            if condition.value is None:
                errors.append(f"Condition {i+1}: Value is required")
        
        # Check action
        if not rule.action:
            errors.append("Rule action is required")
        elif not rule.action.type:
            errors.append("Rule action type is required")
        
        # Check priority
        if rule.priority < 1 or rule.priority > 1000:
            warnings.append("Priority should be between 1 and 1000")
        
        # Suggestions
        if len(rule.conditions) > 5:
            suggestions.append("Consider simplifying rules with many conditions")
        
        if not rule.description:
            suggestions.append("Add a description to help with rule maintenance")
        
        return RuleValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def get_statistics(self) -> RuleStatistics:
        """Get rule statistics"""
        enabled_rules = sum(1 for rule in self.rules.values() if rule.is_enabled)
        disabled_rules = len(self.rules) - enabled_rules
        
        # Group rules by priority
        rules_by_priority = {}
        for rule in self.rules.values():
            priority = rule.priority
            rules_by_priority[priority] = rules_by_priority.get(priority, 0) + 1
        
        # Most triggered rules
        most_triggered = sorted(
            self.rule_statistics['rule_trigger_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        most_triggered_rules = [
            {'rule_id': rule_id, 'trigger_count': count}
            for rule_id, count in most_triggered
        ]
        
        # Average execution time
        execution_times = self.rule_statistics['execution_times']
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return RuleStatistics(
            total_rules=len(self.rules),
            enabled_rules=enabled_rules,
            disabled_rules=disabled_rules,
            rules_by_priority=rules_by_priority,
            most_triggered_rules=most_triggered_rules,
            average_execution_time_ms=avg_execution_time,
            total_evaluations=self.rule_statistics['total_evaluations'],
            successful_evaluations=self.rule_statistics['successful_evaluations'],
            failed_evaluations=self.rule_statistics['failed_evaluations']
        )
    
    def record_rule_evaluation(self, rule_id: str, execution_time_ms: float, success: bool):
        """Record rule evaluation statistics"""
        self.rule_statistics['total_evaluations'] += 1
        if success:
            self.rule_statistics['successful_evaluations'] += 1
            self.rule_statistics['rule_trigger_counts'][rule_id] = \
                self.rule_statistics['rule_trigger_counts'].get(rule_id, 0) + 1
        else:
            self.rule_statistics['failed_evaluations'] += 1
        
        self.rule_statistics['execution_times'].append(execution_time_ms)
        
        # Keep only last 1000 execution times for memory efficiency
        if len(self.rule_statistics['execution_times']) > 1000:
            self.rule_statistics['execution_times'] = self.rule_statistics['execution_times'][-1000:]


class AdvancedRulesEngine:
    """Advanced Rules Engine - main service for evaluating fraud detection rules"""
    
    def __init__(self, static_rules: List[IRule] = None, rule_management_service: RuleManagementService = None, settings: Dict[str, Any] = None):
        self.static_rules = static_rules or get_default_static_rules()
        self.rule_management_service = rule_management_service or RuleManagementService()
        self.settings = settings or {}
        self.is_enabled = self.settings.get('is_enabled', True)
        
        logger.info(f"Advanced Rules Engine initialized with {len(self.static_rules)} static rules")
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Tuple[List[RiskFactor], str, float]:
        """Evaluate all rules against a transaction and return risk factors, recommended action, and overall score"""
        start_time = time.time()
        factors = []
        
        try:
            # Evaluate static, code-based rules
            for rule in self.static_rules:
                try:
                    factor = await rule.evaluate_async(transaction, account_id)
                    if factor and factor.weight > 0:
                        factors.append(factor)
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error(f"Error evaluating static rule {rule.name}: {e}")
            
            # Evaluate dynamic, data-driven rules if the feature is enabled
            if self.is_enabled:
                dynamic_rules = await self.rule_management_service.get_all_rules_async()
                for rule in sorted([r for r in dynamic_rules if r.is_enabled], key=lambda x: x.priority):
                    try:
                        rule_start_time = time.time()
                        is_match = self._evaluate_dynamic_rule(transaction, rule)
                        rule_execution_time = (time.time() - rule_start_time) * 1000
                        
                        self.rule_management_service.record_rule_evaluation(
                            rule.rule_id, rule_execution_time, True
                        )
                        
                        if is_match:
                            # Apply rule action
                            risk_factor = self._apply_rule_action(rule)
                            if risk_factor:
                                factors.append(risk_factor)
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.error(f"Error evaluating dynamic rule {rule.name}: {e}")
                        self.rule_management_service.record_rule_evaluation(
                            rule.rule_id, 0, False
                        )
            
            # Calculate overall risk score and determine action
            total_score = sum(f.weight for f in factors) if factors else 0.0
            risk_level = self._determine_risk_level(total_score)
            recommended_action = self._determine_recommended_action(total_score)
            
            execution_time = (time.time() - start_time) * 1000
            logger.debug(f"Rules evaluation completed in {execution_time:.2f}ms with score {total_score:.2f}")
            
            return factors, recommended_action, total_score
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in rules engine evaluation: {e}")
            return [], "ERROR", 0.0
    
    def _evaluate_dynamic_rule(self, transaction: Dict[str, Any], rule: DynamicRule) -> bool:
        """Evaluate a dynamic rule against a transaction"""
        # For simplicity, we'll assume conditions are ANDed together
        for condition in rule.conditions:
            if not self._is_condition_met(transaction, condition):
                return False  # If any condition is not met, the rule doesn't match
        return True  # All conditions were met
    
    def _is_condition_met(self, transaction: Dict[str, Any], condition: RuleCondition) -> bool:
        """Check if a condition is met for a transaction"""
        try:
            transaction_value = self._get_transaction_value(transaction, condition.field)
            if transaction_value is None:
                return False
            
            condition_value = condition.value
            
            # Convert values to appropriate types for comparison
            if isinstance(condition_value, (int, float)) and isinstance(transaction_value, (int, float)):
                return self._compare_numeric_values(transaction_value, condition.operator, condition_value)
            elif isinstance(condition_value, str) and isinstance(transaction_value, str):
                return self._compare_string_values(transaction_value, condition.operator, condition_value)
            elif isinstance(condition_value, list):
                return self._compare_list_values(transaction_value, condition.operator, condition_value)
            else:
                # Try to convert to string for comparison
                return self._compare_string_values(str(transaction_value), condition.operator, str(condition_value))
        
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error evaluating condition {condition.field}: {e}")
            return False
    
    def _get_transaction_value(self, transaction: Dict[str, Any], field_name: str) -> Any:
        """Get a value from transaction by field name"""
        field_name_lower = field_name.lower()
        
        # Direct field mapping
        if field_name_lower in transaction:
            return transaction[field_name_lower]
        
        # Special field mappings
        field_mappings = {
            'amount': 'amount',
            'day_of_week': lambda t: self._get_day_of_week(t.get('timestamp')),
            'time_since_last_transaction': lambda t: self._get_time_since_last_transaction(t),
            'merchant_name': 'merchant_name',
            'location': 'location',
            'device_id': 'device_id',
            'ip_address': 'ip_address'
        }
        
        if field_name_lower in field_mappings:
            mapping = field_mappings[field_name_lower]
            if callable(mapping):
                return mapping(transaction)
            else:
                return transaction.get(mapping)
        
        return None
    
    def _get_day_of_week(self, timestamp_str: str) -> str:
        """Get day of week from timestamp"""
        try:
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return days[timestamp.weekday()]
        except:
            return 'Unknown'
    
    def _get_time_since_last_transaction(self, transaction: Dict[str, Any]) -> float:
        """Get time since last transaction in seconds (mock implementation)"""
        # This would normally query the database for the last transaction
        # For now, return a mock value
        return 120.0  # 2 minutes
    
    def _compare_numeric_values(self, transaction_value: float, operator: RuleOperator, condition_value: float) -> bool:
        """Compare numeric values"""
        if operator == RuleOperator.GREATER_THAN:
            return transaction_value > condition_value
        elif operator == RuleOperator.LESS_THAN:
            return transaction_value < condition_value
        elif operator == RuleOperator.EQUALS:
            return abs(transaction_value - condition_value) < 0.001  # Float comparison
        elif operator == RuleOperator.NOT_EQUALS:
            return abs(transaction_value - condition_value) >= 0.001
        else:
            return False
    
    def _compare_string_values(self, transaction_value: str, operator: RuleOperator, condition_value: str) -> bool:
        """Compare string values"""
        if operator == RuleOperator.EQUALS:
            return transaction_value.lower() == condition_value.lower()
        elif operator == RuleOperator.NOT_EQUALS:
            return transaction_value.lower() != condition_value.lower()
        elif operator == RuleOperator.CONTAINS:
            return condition_value.lower() in transaction_value.lower()
        elif operator == RuleOperator.NOT_CONTAINS:
            return condition_value.lower() not in transaction_value.lower()
        else:
            return False
    
    def _compare_list_values(self, transaction_value: Any, operator: RuleOperator, condition_value: List[Any]) -> bool:
        """Compare with list values"""
        if operator == RuleOperator.IN:
            return str(transaction_value).lower() in [str(v).lower() for v in condition_value]
        elif operator == RuleOperator.NOT_IN:
            return str(transaction_value).lower() not in [str(v).lower() for v in condition_value]
        else:
            return False
    
    def _apply_rule_action(self, rule: DynamicRule) -> Optional[RiskFactor]:
        """Apply a rule action and return a risk factor"""
        action = rule.action
        
        if action.type == RuleActionType.INCREASE_RISK_SCORE:
            amount = action.parameters.get('Amount', 0.5)
            description = action.parameters.get('Description', f"Dynamic rule triggered: {rule.name}")
            rule_type = action.parameters.get('Type', description)
            
            return RiskFactor(
                type=rule_type,
                weight=float(amount),
                description=description,
                severity=self._weight_to_severity(float(amount))
            )
        
        return None
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _determine_recommended_action(self, score: float) -> str:
        """Determine recommended action based on score"""
        if score >= 0.9:
            return "BLOCK_TRANSACTION"
        elif score >= 0.7:
            return "VERIFY_IDENTITY"
        elif score >= 0.5:
            return "MONITOR_CLOSELY"
        elif score >= 0.3:
            return "CONTINUE_MONITORING"
        else:
            return "APPROVE"
    
    def _weight_to_severity(self, weight: float) -> RiskLevel:
        """Convert weight score to risk level"""
        if weight >= 0.8:
            return RiskLevel.CRITICAL
        elif weight >= 0.6:
            return RiskLevel.HIGH
        elif weight >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def get_rule_statistics(self) -> RuleStatistics:
        """Get rule statistics"""
        return self.rule_management_service.get_statistics()
    
    async def test_rule(self, rule: DynamicRule, test_data: Dict[str, Any]) -> RuleTestResult:
        """Test a rule with sample data"""
        test_id = f"test_{int(time.time())}"
        start_time = time.time()
        
        try:
            expected_result = test_data.get('expected_result', True)
            actual_result = self._evaluate_dynamic_rule(test_data, rule)
            execution_time = (time.time() - start_time) * 1000
            
            return RuleTestResult(
                test_id=test_id,
                rule_id=rule.rule_id,
                test_data=test_data,
                expected_result=expected_result,
                actual_result=actual_result,
                passed=actual_result == expected_result,
                execution_time_ms=execution_time
            )
        except (ValueError, TypeError, AttributeError) as e:
            execution_time = (time.time() - start_time) * 1000
            return RuleTestResult(
                test_id=test_id,
                rule_id=rule.rule_id,
                test_data=test_data,
                expected_result=test_data.get('expected_result', True),
                actual_result=False,
                passed=False,
                execution_time_ms=execution_time,
                error_message=str(e)
            )


# Global instance
rules_engine = AdvancedRulesEngine()
