"""
Pytest configuration and fixtures for comprehensive test suite
Migrated from C# xUnit/Moq to Python pytest/unittest.mock
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import all services for testing
from fraud_detection import (
    InvestmentFraudDetectionService, MLService, GNNService, FraudToolsService,
    FraudConversationService, AdvancedFraudAlgorithmsService, DatabaseService,
    DataQualityService, MLTrainingPipeline, FeatureEngineeringService,
    AdvancedRulesEngine, MessagingService, CustomerPortalService
)


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing"""
    return {
        'transaction_id': 'test_txn_001',
        'amount': 1000.0,
        'merchant_name': 'TestMerchant',
        'location': 'TestLocation',
        'user_id': 'test_user_001',
        'timestamp': datetime.utcnow().isoformat(),
        'device_id': 'test_device_001'
    }


@pytest.fixture
def high_risk_transaction():
    """High-risk transaction for testing"""
    return {
        'transaction_id': 'high_risk_txn',
        'amount': 25000.0,
        'merchant_name': 'HighRiskMerchant',
        'location': 'UnknownCountry',
        'user_id': 'test_user_002',
        'timestamp': datetime.utcnow().isoformat(),
        'device_id': 'suspicious_device'
    }


@pytest.fixture
def feature_vector():
    """Sample feature vector for ML testing"""
    return {
        'amount': 1000.0,
        'merchant_risk': 0.3,
        'location_risk': 0.2,
        'time_risk': 0.1,
        'device_risk': 0.4,
        'velocity_risk': 0.2,
        'network_risk': 0.1
    }


@pytest.fixture
def mock_fraud_tools():
    """Mock fraud tools service"""
    mock = Mock()
    mock.calculate_risk_score.return_value = 0.5
    mock.analyze_pattern.return_value = []
    mock.detect_velocity_anomalies.return_value = []
    return mock


@pytest.fixture
def mock_ml_service():
    """Mock ML service"""
    mock = Mock()
    mock.predict.return_value = {'risk_score': 0.6, 'confidence': 0.8}
    mock.ensemble_predict.return_value = {'risk_score': 0.65, 'confidence': 0.85}
    mock.get_all_models.return_value = []
    return mock


@pytest.fixture
def mock_gnn_service():
    """Mock GNN service"""
    mock = Mock()
    mock.create_graph.return_value = 'test_graph_id'
    mock.detect_fraud_rings.return_value = []
    mock.detect_communities.return_value = []
    return mock


@pytest.fixture
def mock_rules_engine():
    """Mock rules engine"""
    mock = AsyncMock()
    mock.evaluate_async.return_value = {
        'risk_factors': [],
        'recommended_action': 'APPROVE',
        'score': 0.3
    }
    return mock


@pytest.fixture
def mock_messaging_service():
    """Mock messaging service"""
    mock = AsyncMock()
    mock.get_health_status.return_value = Mock(overall_status='healthy')
    mock.get_metrics.return_value = Mock(service_bus_messages_published=0)
    mock.send_fraud_alert.return_value = True
    return mock


@pytest.fixture
def mock_customer_portal():
    """Mock customer portal service"""
    mock = AsyncMock()
    mock.create_fraud_case.return_value = Mock(case_number='TEST-001')
    mock.get_case_statistics.return_value = Mock(total_cases=0)
    mock.health_check.return_value = {'status': 'healthy'}
    return mock


@pytest.fixture
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test markers
pytestmark = pytest.mark.comprehensive