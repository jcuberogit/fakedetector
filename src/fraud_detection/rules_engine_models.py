"""
Advanced Rules Engine Models
Migrated from C# FraudDetectionAgent.Api.Models.AdvancedRulesEngine
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class RuleOperator(str, Enum):
    """Rule condition operators"""
    GREATER_THAN = "GreaterThan"
    LESS_THAN = "LessThan"
    EQUALS = "Equals"
    NOT_EQUALS = "NotEquals"
    CONTAINS = "Contains"
    NOT_CONTAINS = "NotContains"
    IN = "In"
    NOT_IN = "NotIn"
    REGEX_MATCH = "RegexMatch"
    REGEX_NOT_MATCH = "RegexNotMatch"


class RuleActionType(str, Enum):
    """Rule action types"""
    BLOCK_TRANSACTION = "BLOCK_TRANSACTION"
    VERIFY_IDENTITY = "VERIFY_IDENTITY"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    INCREASE_RISK_SCORE = "INCREASE_RISK_SCORE"
    ALERT = "ALERT"
    APPROVE = "APPROVE"
    MONITOR_CLOSELY = "MONITOR_CLOSELY"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class RuleCondition(BaseModel):
    """Represents a single condition within a dynamic rule"""
    field: str = Field(..., description="Transaction field name to evaluate")
    operator: RuleOperator = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")
    description: Optional[str] = Field(None, description="Human-readable description")


class RuleAction(BaseModel):
    """Represents the action to be taken when a rule's conditions are met"""
    type: RuleActionType = Field(..., description="Action type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    description: Optional[str] = Field(None, description="Human-readable description")


class DynamicRule(BaseModel):
    """Represents a dynamic rule that can be configured and managed at runtime"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    is_enabled: bool = Field(True, description="Whether the rule is enabled")
    priority: int = Field(100, description="Rule priority (lower numbers have higher priority)")
    conditions: List[RuleCondition] = Field(default_factory=list, description="Rule conditions")
    action: RuleAction = Field(..., description="Rule action")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created the rule")
    updated_by: Optional[str] = Field(None, description="User who last updated the rule")
    tags: List[str] = Field(default_factory=list, description="Rule tags for categorization")
    version: int = Field(1, description="Rule version number")


class RuleResult(BaseModel):
    """Result of rule evaluation"""
    rule_id: str = Field(..., description="Rule identifier")
    rule_name: str = Field(..., description="Rule name")
    matched: bool = Field(..., description="Whether the rule matched")
    risk_factors: List[str] = Field(default_factory=list, description="Generated risk factors")
    action: Optional[RuleAction] = Field(None, description="Action to take")
    execution_time_ms: float = Field(..., description="Rule execution time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if evaluation failed")


class RuleEvaluationResult(BaseModel):
    """Complete result of rules engine evaluation"""
    transaction_id: str = Field(..., description="Transaction identifier")
    account_id: str = Field(..., description="Account identifier")
    risk_factors: List[str] = Field(default_factory=list, description="All risk factors")
    recommended_action: str = Field(..., description="Recommended action")
    score: float = Field(..., description="Overall risk score")
    rule_results: List[RuleResult] = Field(default_factory=list, description="Individual rule results")
    execution_time_ms: float = Field(..., description="Total execution time")
    evaluated_rules_count: int = Field(..., description="Number of rules evaluated")
    matched_rules_count: int = Field(..., description="Number of rules that matched")


class RuleManagementRequest(BaseModel):
    """Request for rule management operations"""
    operation: str = Field(..., description="Operation type: create, update, delete, enable, disable")
    rule: Optional[DynamicRule] = Field(None, description="Rule data for create/update operations")
    rule_id: Optional[str] = Field(None, description="Rule ID for delete/enable/disable operations")
    user_id: Optional[str] = Field(None, description="User performing the operation")


class RuleManagementResponse(BaseModel):
    """Response for rule management operations"""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Operation result message")
    rule: Optional[DynamicRule] = Field(None, description="Rule data for successful operations")
    error: Optional[str] = Field(None, description="Error message for failed operations")


class RuleStatistics(BaseModel):
    """Statistics about rule usage and performance"""
    total_rules: int = Field(..., description="Total number of rules")
    enabled_rules: int = Field(..., description="Number of enabled rules")
    disabled_rules: int = Field(..., description="Number of disabled rules")
    rules_by_priority: Dict[int, int] = Field(default_factory=dict, description="Rules count by priority")
    most_triggered_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Most frequently triggered rules")
    average_execution_time_ms: float = Field(..., description="Average rule execution time")
    total_evaluations: int = Field(..., description="Total rule evaluations performed")
    successful_evaluations: int = Field(..., description="Successful evaluations")
    failed_evaluations: int = Field(..., description="Failed evaluations")


class RuleTemplate(BaseModel):
    """Template for creating new rules"""
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Rule category")
    conditions_template: List[Dict[str, Any]] = Field(..., description="Template for conditions")
    action_template: Dict[str, Any] = Field(..., description="Template for action")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Configurable parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")


class RuleValidationResult(BaseModel):
    """Result of rule validation"""
    is_valid: bool = Field(..., description="Whether the rule is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class RuleTestResult(BaseModel):
    """Result of rule testing with sample data"""
    test_id: str = Field(..., description="Test identifier")
    rule_id: str = Field(..., description="Rule identifier")
    test_data: Dict[str, Any] = Field(..., description="Test transaction data")
    expected_result: bool = Field(..., description="Expected match result")
    actual_result: bool = Field(..., description="Actual match result")
    passed: bool = Field(..., description="Whether the test passed")
    execution_time_ms: float = Field(..., description="Test execution time")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
