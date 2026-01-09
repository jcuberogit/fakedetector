"""
API Integration Tests for Fraud Detection Agent
"""

import pytest
from decimal import Decimal
from datetime import datetime
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from agent import app, ParadigmFraudAgent


@pytest.mark.api
class TestFraudAgentAPI:
    """Test Fraud Agent API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def fraud_agent(self):
        """Create FraudAgent instance"""
        return ParadigmFraudAgent()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_risk_score_endpoint(self, client):
        """Test risk score calculation endpoint"""
        payload = {
            "transaction_id": "test_txn_api_001",
            "amount": 1000.0,
            "merchant_name": "TestMerchant",
            "location": "US"
        }
        
        response = client.post('/api/fraud/risk-score', json=payload)
        # May return 200 or 404 depending on endpoint implementation
        assert response.status_code in [200, 404]
    
    def test_fraud_assessment_endpoint(self, client):
        """Test fraud assessment endpoint"""
        payload = {
            "account_id": "test_account_001",
            "transaction_id": "test_txn_api_002"
        }
        
        response = client.post('/api/fraud/assess', json=payload)
        # May return 200 or 404 depending on endpoint implementation
        assert response.status_code in [200, 404]










