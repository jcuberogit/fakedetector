"""
Unit tests for FraudTools service
TDD: RED → GREEN → REFACTOR
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fraud_detection.fraud_tools_service import FraudTools
from fraud_detection.fraud_tools_models import (
    FraudRiskScore, FraudAssessment, FraudRiskAssessment, Transaction,
    RiskFactor, RiskLevel, Severity, RecommendedAction, TransactionType
)


@pytest.mark.unit
class TestFraudToolsRiskScoring:
    """Test risk scoring functionality"""
    
    @pytest.fixture
    def fraud_tools(self):
        """Create FraudTools instance"""
        return FraudTools()
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_risk_score_low_risk(self, fraud_tools):
        """Test calculating risk score for low-risk transaction"""
        # RED: Test should fail initially, then pass after implementation
        transaction_id = "test_txn_001"
        amount = Decimal('100.00')
        merchant_name = "Amazon"
        location = "San Francisco, CA"
        
        result = await fraud_tools.calculate_transaction_risk_score(
            transaction_id, amount, merchant_name, location
        )
        
        # GREEN: Assertions
        assert isinstance(result, FraudRiskScore)
        assert result.transaction_id == transaction_id
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(result.risk_factors) > 0
        assert result.recommended_action in [RecommendedAction.ALLOW, RecommendedAction.MONITOR, RecommendedAction.REVIEW, RecommendedAction.BLOCK]
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_risk_score_high_amount(self, fraud_tools):
        """Test calculating risk score for high-amount transaction"""
        transaction_id = "test_txn_002"
        amount = Decimal('50000.00')  # High amount
        merchant_name = "Unknown Merchant"
        location = "High Risk Location"
        
        result = await fraud_tools.calculate_transaction_risk_score(
            transaction_id, amount, merchant_name, location
        )
        
        # High amount + unknown merchant + high risk location should increase risk
        assert result.risk_score >= Decimal('0.5')  # Should be medium-high risk
        assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_risk_score_invalid_input(self, fraud_tools):
        """Test risk score calculation with invalid input"""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            await fraud_tools.calculate_transaction_risk_score(
                "", Decimal('-100'), "", ""
            )


@pytest.mark.unit
class TestFraudToolsPatternAnalysis:
    """Test pattern analysis functionality"""
    
    @pytest.fixture
    def fraud_tools(self):
        """Create FraudTools instance"""
        return FraudTools()
    
    @pytest.mark.asyncio
    async def test_analyze_transaction_pattern(self, fraud_tools):
        """Test analyzing transaction patterns"""
        account_id = "test_account_001"
        transaction_id = "test_txn_003"
        
        result = await fraud_tools.analyze_transaction_pattern(account_id, transaction_id)
        
        assert isinstance(result, FraudAssessment)
        assert result.transaction_id == transaction_id
        assert result.account_id == account_id
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
        assert len(result.risk_factors) >= 0
        assert result.analysis_methods is not None
    
    @pytest.mark.asyncio
    async def test_detect_velocity_anomalies_normal(self, fraud_tools):
        """Test velocity anomaly detection for normal transactions"""
        user_id = "test_user_001"
        amount = Decimal('100.00')
        transaction_time = datetime.utcnow()
        
        result = await fraud_tools.detect_velocity_anomalies(user_id, amount, transaction_time)
        
        assert isinstance(result, list)
        # Normal transaction should have few or no anomalies
        assert len(result) <= 2
    
    @pytest.mark.asyncio
    async def test_detect_velocity_anomalies_high_velocity(self, fraud_tools):
        """Test velocity anomaly detection for high-velocity transactions"""
        user_id = "test_user_002"
        amount = Decimal('1000.00')
        transaction_time = datetime.utcnow()
        
        # Mock high velocity by adding many transactions
        with patch.object(fraud_tools, '_get_user_recent_transactions', new_callable=AsyncMock) as mock_get:
            # Simulate 15 transactions in last hour
            mock_transactions = [
                Transaction(
                    transaction_id=f"txn_{i}",
                    amount=Decimal('100.00'),
                    merchant_name="TestMerchant",
                    location="TestLocation",
                    user_id=user_id,
                    timestamp=transaction_time - timedelta(minutes=i*4),
                    device_id="test_device"
                )
                for i in range(15)
            ]
            mock_get.return_value = mock_transactions
            
            result = await fraud_tools.detect_velocity_anomalies(user_id, amount, transaction_time)
            
            # Should detect high velocity anomaly
            assert len(result) > 0
            velocity_anomalies = [rf for rf in result if "VELOCITY" in rf.type]
            assert len(velocity_anomalies) > 0


@pytest.mark.unit
class TestFraudToolsHistoryAnalysis:
    """Test transaction history analysis"""
    
    @pytest.fixture
    def fraud_tools(self):
        """Create FraudTools instance"""
        return FraudTools()
    
    @pytest.mark.asyncio
    async def test_analyze_transaction_history_risk(self, fraud_tools):
        """Test analyzing transaction history risk"""
        account_id = "test_account_002"
        user_id = "test_user_003"
        
        result = await fraud_tools.analyze_transaction_history_risk(account_id, user_id)
        
        assert isinstance(result, FraudRiskAssessment)
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
        assert len(result.risk_factors) > 0
        assert result.analysis_methods is not None
    
    @pytest.mark.asyncio
    async def test_analyze_card_operation_risk(self, fraud_tools):
        """Test analyzing card operation risk"""
        card_id = "test_card_001"
        action = "purchase"
        user_id = "test_user_004"
        
        result = await fraud_tools.analyze_card_operation_risk(card_id, action, user_id)
        
        assert isinstance(result, FraudRiskAssessment)
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
        assert len(result.risk_factors) > 0


@pytest.mark.unit
class TestFraudToolsHelperMethods:
    """Test helper methods"""
    
    @pytest.fixture
    def fraud_tools(self):
        """Create FraudTools instance"""
        return FraudTools()
    
    def test_determine_risk_level(self, fraud_tools):
        """Test risk level determination"""
        # Test different risk score ranges
        assert fraud_tools._determine_risk_level(Decimal('0.1')) == RiskLevel.LOW
        assert fraud_tools._determine_risk_level(Decimal('0.4')) == RiskLevel.MEDIUM
        assert fraud_tools._determine_risk_level(Decimal('0.7')) == RiskLevel.HIGH
        assert fraud_tools._determine_risk_level(Decimal('0.9')) == RiskLevel.CRITICAL
    
    def test_get_recommended_action(self, fraud_tools):
        """Test recommended action determination"""
        # Low risk should allow
        assert fraud_tools._get_recommended_action(Decimal('0.2')) == RecommendedAction.ALLOW
        
        # Medium risk should monitor
        assert fraud_tools._get_recommended_action(Decimal('0.5')) == RecommendedAction.MONITOR
        
        # High risk should review
        assert fraud_tools._get_recommended_action(Decimal('0.7')) == RecommendedAction.REVIEW
        
        # Critical risk should block
        assert fraud_tools._get_recommended_action(Decimal('0.8')) == RecommendedAction.BLOCK
    
    def test_calculate_amount_risk(self, fraud_tools):
        """Test amount-based risk calculation"""
        # Low amount
        low_risk = fraud_tools._calculate_amount_risk(Decimal('50.00'))
        assert low_risk.weight < Decimal('0.5')
        
        # High amount
        high_risk = fraud_tools._calculate_amount_risk(Decimal('10000.00'))
        assert high_risk.weight >= Decimal('0.5')
    
    def test_calculate_location_risk(self, fraud_tools):
        """Test location-based risk calculation"""
        # Known location
        known_risk = fraud_tools._calculate_location_risk("San Francisco, CA")
        assert isinstance(known_risk, RiskFactor)
        
        # Unknown location
        unknown_risk = fraud_tools._calculate_location_risk("Unknown Location")
        assert isinstance(unknown_risk, RiskFactor)
        # Unknown locations should have higher risk
        assert unknown_risk.weight >= known_risk.weight

