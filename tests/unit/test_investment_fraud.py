"""
Unit tests for Investment Fraud Detection Service
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fraud_detection.investment_fraud_service import InvestmentFraudDetectionService
from fraud_detection.investment_models import (
    InvestmentTransactionRequest, InvestmentRiskAssessment,
    InvestmentValidationResult, TradingPattern
)


@pytest.mark.unit
class TestInvestmentFraudDetection:
    """Test investment fraud detection functionality"""
    
    @pytest.fixture
    def investment_service(self):
        """Create InvestmentFraudDetectionService instance"""
        return InvestmentFraudDetectionService()
    
    @pytest.mark.asyncio
    async def test_assess_investment_risk(self, investment_service):
        """Test assessing investment risk"""
        request = InvestmentTransactionRequest(
            transaction_id="inv_txn_001",
            amount=Decimal('10000.00'),
            investment_type="stock",
            user_id="test_user_001",
            timestamp=datetime.utcnow()
        )
        
        result = await investment_service.assess_investment_risk(request)
        
        assert isinstance(result, InvestmentRiskAssessment)
        assert result.risk_score >= Decimal('0')
        assert result.risk_score <= Decimal('1')
    
    @pytest.mark.asyncio
    async def test_validate_investment_transaction(self, investment_service):
        """Test validating investment transaction"""
        request = InvestmentTransactionRequest(
            transaction_id="inv_txn_002",
            amount=Decimal('5000.00'),
            investment_type="bond",
            user_id="test_user_002",
            timestamp=datetime.utcnow()
        )
        
        result = await investment_service.validate_investment_transaction(request)
        
        assert isinstance(result, InvestmentValidationResult)
        assert result.is_valid is not None
    
    @pytest.mark.asyncio
    async def test_detect_trading_patterns(self, investment_service):
        """Test detecting trading patterns"""
        user_id = "test_user_003"
        
        result = await investment_service.detect_trading_patterns(user_id)
        
        assert isinstance(result, list)
        # May return empty list or list of patterns










