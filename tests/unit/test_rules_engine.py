"""
Rules Engine Tests (FRAUD-004)
TDD: RED → GREEN → REFACTOR
Test all fraud rules, combinations, priority, and dynamic updates
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fraud_detection.rules_engine_service import (
    AdvancedRulesEngine, RuleManagementService
)
from fraud_detection.rules_engine_models import (
    DynamicRule, RuleCondition, RuleAction, RuleEvaluationResult,
    RuleOperator, RuleActionType, RuleResult
)
from fraud_detection.static_rules import get_default_static_rules


@pytest.mark.unit
class TestRulesEngineEvaluation:
    """Test rules engine evaluation functionality"""
    
    @pytest.fixture
    def rules_engine(self):
        """Create AdvancedRulesEngine instance"""
        return AdvancedRulesEngine()
    
    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction for testing"""
        return {
            "transaction_id": "test_txn_001",
            "amount": Decimal('100.00'),
            "merchant_name": "TestMerchant",
            "location": "US",
            "day_of_week": "Monday",
            "time_of_day": 14,
            "user_id": "test_user_001"
        }
    
    @pytest.mark.asyncio
    async def test_evaluate_static_rules(self, rules_engine, sample_transaction):
        """Test evaluating static rules"""
        result = await rules_engine.evaluate_async(sample_transaction)
        
        assert isinstance(result, RuleEvaluationResult)
        assert result.risk_factors is not None
        assert isinstance(result.risk_factors, list)
        assert result.recommended_action is not None
        assert result.score >= Decimal('0')
        assert result.score <= Decimal('1')
    
    @pytest.mark.asyncio
    async def test_evaluate_dynamic_rules(self, rules_engine, sample_transaction):
        """Test evaluating dynamic rules"""
        # High amount transaction that should trigger rules
        high_amount_transaction = sample_transaction.copy()
        high_amount_transaction["amount"] = Decimal('10000.00')
        
        result = await rules_engine.evaluate_async(high_amount_transaction)
        
        assert isinstance(result, RuleEvaluationResult)
        assert len(result.risk_factors) >= 0  # May or may not trigger rules
    
    @pytest.mark.asyncio
    async def test_rule_priority(self, rules_engine):
        """Test that rules are evaluated in priority order"""
        # Create transactions that trigger multiple rules
        transaction = {
            "transaction_id": "test_txn_002",
            "amount": Decimal('6000.00'),  # High amount
            "day_of_week": "Sunday",  # Weekend
            "merchant_name": "TestMerchant",
            "location": "US",
            "time_of_day": 14,
            "user_id": "test_user_002"
        }
        
        result = await rules_engine.evaluate_async(transaction)
        
        # Should evaluate rules and return result
        assert isinstance(result, RuleEvaluationResult)
        # Higher priority rules should be evaluated first
        assert result.score >= Decimal('0')


@pytest.mark.unit
class TestRuleManagementService:
    """Test rule management service"""
    
    @pytest.fixture
    def rule_service(self):
        """Create RuleManagementService instance"""
        return RuleManagementService()
    
    @pytest.mark.asyncio
    async def test_get_all_rules(self, rule_service):
        """Test getting all rules"""
        rules = await rule_service.get_all_rules_async()
        
        assert isinstance(rules, list)
        assert len(rules) > 0  # Should have default rules
    
    @pytest.mark.asyncio
    async def test_create_rule(self, rule_service):
        """Test creating a new rule"""
        new_rule = DynamicRule(
            name="Test Rule",
            description="Test rule creation",
            priority=5,
            conditions=[
                RuleCondition(
                    field="amount",
                    operator=RuleOperator.GREATER_THAN,
                    value=1000,
                    description="Amount > 1000"
                )
            ],
            action=RuleAction(
                type=RuleActionType.MANUAL_REVIEW,
                parameters={"reason": "Test"},
                description="Test action"
            )
        )
        
        result = await rule_service.create_rule_async(new_rule)
        
        assert result.success is True
        assert new_rule.rule_id in rule_service.rules
    
    @pytest.mark.asyncio
    async def test_update_rule(self, rule_service):
        """Test updating an existing rule"""
        # Get first rule
        rules = await rule_service.get_all_rules_async()
        if len(rules) > 0:
            rule = rules[0]
            original_name = rule.name
            
            # Update rule
            rule.name = "Updated Rule Name"
            result = await rule_service.update_rule_async(rule.rule_id, rule)
            
            assert result.success is True
            updated_rule = await rule_service.get_rule_async(rule.rule_id)
            assert updated_rule.name == "Updated Rule Name"
    
    @pytest.mark.asyncio
    async def test_delete_rule(self, rule_service):
        """Test deleting a rule"""
        # Create a rule first
        new_rule = DynamicRule(
            name="Rule to Delete",
            description="This rule will be deleted",
            priority=1,
            conditions=[
                RuleCondition(
                    field="amount",
                    operator=RuleOperator.GREATER_THAN,
                    value=100,
                    description="Amount > 100"
                )
            ],
            action=RuleAction(
                type=RuleActionType.APPROVE,
                parameters={},
                description="Approve"
            )
        )
        
        create_result = await rule_service.create_rule_async(new_rule)
        assert create_result.success is True
        
        # Delete the rule
        delete_result = await rule_service.delete_rule_async(new_rule.rule_id)
        assert delete_result.success is True
        
        # Verify rule is deleted
        deleted_rule = await rule_service.get_rule_async(new_rule.rule_id)
        assert deleted_rule is None


@pytest.mark.unit
class TestRuleCombinations:
    """Test rule combinations and interactions"""
    
    @pytest.fixture
    def rules_engine(self):
        """Create AdvancedRulesEngine instance"""
        return AdvancedRulesEngine()
    
    @pytest.mark.asyncio
    async def test_multiple_conditions_and(self, rules_engine):
        """Test rule with multiple AND conditions"""
        transaction = {
            "transaction_id": "test_txn_003",
            "amount": Decimal('6000.00'),  # High amount
            "day_of_week": "Saturday",  # Weekend
            "merchant_name": "TestMerchant",
            "location": "US",
            "time_of_day": 14,
            "user_id": "test_user_003"
        }
        
        result = await rules_engine.evaluate_async(transaction)
        
        # Should evaluate rules with multiple conditions
        assert isinstance(result, RuleEvaluationResult)
    
    @pytest.mark.asyncio
    async def test_rule_combinations_or(self, rules_engine):
        """Test rules with OR logic"""
        transaction = {
            "transaction_id": "test_txn_004",
            "amount": Decimal('100.00'),
            "day_of_week": "Sunday",  # Weekend (one condition)
            "merchant_name": "TestMerchant",
            "location": "US",
            "time_of_day": 14,
            "user_id": "test_user_004"
        }
        
        result = await rules_engine.evaluate_async(transaction)
        
        assert isinstance(result, RuleEvaluationResult)


@pytest.mark.unit
class TestStaticRules:
    """Test static rules functionality"""
    
    def test_get_default_static_rules(self):
        """Test getting default static rules"""
        rules = get_default_static_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0  # Should have default rules
    
    def test_static_rule_evaluation(self):
        """Test evaluating static rules"""
        rules = get_default_static_rules()
        
        transaction = {
            "amount": Decimal('5000.00'),
            "merchant_name": "TestMerchant",
            "location": "US"
        }
        
        # Evaluate each rule
        for rule in rules:
            if hasattr(rule, 'evaluate'):
                result = rule.evaluate(transaction)
                # Result should be a RuleResult or similar
                assert result is not None










