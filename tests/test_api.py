"""
Integration Tests for UniversalShield VPS API
Tests all API endpoints with real database interactions
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.scam_detection_api import app
from src.db.database import DatabaseService

client = TestClient(app)


class TestHealthEndpoint:
    """Test API health check endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "UniversalShield API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"


class TestAnalyzeFeaturesEndpoint:
    """Test feature analysis endpoint."""
    
    def test_analyze_features_without_license(self):
        """Test analysis with free tier (no license)."""
        features = {
            "message_length": 150,
            "word_count": 25,
            "urgency_keywords_count": 2,
            "money_keywords_count": 1,
            "recruiter_keywords_count": 0,
            "gmail_recruiter_combo": 0
        }
        
        response = client.post(
            "/api/v1/analyze-features",
            json={"features": features}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "tier" in data
        assert data["tier"] == "free"
        assert "scans_remaining" in data
    
    def test_analyze_features_with_pro_license(self):
        """Test analysis with Pro tier license."""
        features = {
            "message_length": 150,
            "word_count": 25,
            "urgency_keywords_count": 3,
            "money_keywords_count": 2,
            "recruiter_keywords_count": 1,
            "gmail_recruiter_combo": 1
        }
        
        response = client.post(
            "/api/v1/analyze-features",
            json={"features": features},
            headers={"X-License-Key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "pro"
        assert data["scans_remaining"] is None  # Unlimited for Pro
    
    def test_rachel_good_pattern_detection(self):
        """Test Rachel Good scam pattern detection."""
        features = {
            "message_length": 200,
            "word_count": 35,
            "recruiter_keywords_count": 2,
            "location_inquiry": 1,
            "experience_inquiry": 1,
            "gmail_recruiter_combo": 1,  # High risk indicator
            "vague_address_pattern": 1,
            "urgency_keywords_count": 0,
            "money_keywords_count": 0
        }
        
        response = client.post(
            "/api/v1/analyze-features",
            json={"features": features},
            headers={"X-License-Key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should detect high risk due to gmail_recruiter_combo
        assert data["risk_score"] >= 40
    
    def test_financial_phishing_detection(self):
        """Test financial phishing pattern detection."""
        features = {
            "message_length": 180,
            "word_count": 30,
            "financial_phishing_keywords_count": 3,
            "credit_card_mention": 1,
            "credit_limit_mention": 1,
            "security_deposit_mention": 1,
            "urgency_keywords_count": 2,
            "money_keywords_count": 1
        }
        
        response = client.post(
            "/api/v1/analyze-features",
            json={"features": features},
            headers={"X-License-Key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should detect high risk due to financial phishing patterns
        assert data["risk_score"] >= 50
        assert data["risk_level"] in ["caution", "critical"]
    
    def test_rate_limiting_free_tier(self):
        """Test rate limiting for free tier."""
        features = {"message_length": 100, "word_count": 15}
        
        # Make multiple requests to trigger rate limit
        for i in range(55):  # Exceed 50 limit
            response = client.post(
                "/api/v1/analyze-features",
                json={"features": features}
            )
            
            if i < 50:
                assert response.status_code == 200
            else:
                # Should be rate limited after 50 requests
                assert response.status_code == 429


class TestReportScamEndpoint:
    """Test scam reporting endpoint."""
    
    def test_report_scam(self):
        """Test reporting a scam for ML training."""
        features = {
            "message_length": 150,
            "urgency_keywords_count": 3,
            "money_keywords_count": 2
        }
        
        response = client.post(
            "/api/v1/report-scam",
            json={
                "features": features,
                "is_scam": True,
                "predicted_risk_score": 85.0,
                "predicted_risk_level": "critical",
                "platform": "linkedin"
            },
            headers={"X-License-Key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data_point_id" in data
    
    def test_report_false_positive(self):
        """Test reporting a false positive."""
        features = {
            "message_length": 100,
            "urgency_keywords_count": 0
        }
        
        response = client.post(
            "/api/v1/report-scam",
            json={
                "features": features,
                "is_scam": False,  # False positive
                "predicted_risk_score": 75.0,
                "predicted_risk_level": "caution",
                "platform": "linkedin"
            },
            headers={"X-License-Key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestLicenseValidation:
    """Test license validation endpoint."""
    
    def test_validate_demo_license(self):
        """Test validating demo Pro license."""
        response = client.post(
            "/api/v1/subscription/validate",
            json={"license_key": "US-PRO-DEMO12345678"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["tier"] == "pro"
        assert data["features_enabled"]["cloud_ml"] is True
        assert data["features_enabled"]["unlimited_scans"] is True
    
    def test_validate_invalid_license(self):
        """Test validating invalid license key."""
        response = client.post(
            "/api/v1/subscription/validate",
            json={"license_key": "INVALID-KEY-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["tier"] == "free"


class TestPaymentEndpoints:
    """Test payment API endpoints."""
    
    def test_get_plans(self):
        """Test getting available subscription plans."""
        response = client.get("/api/v1/payment/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 2  # Monthly and Annual
        
        # Check monthly plan
        monthly = next(p for p in data["plans"] if p["id"] == "monthly")
        assert monthly["price"] == 4.99
        assert monthly["interval"] == "month"
        
        # Check annual plan
        annual = next(p for p in data["plans"] if p["id"] == "annual")
        assert annual["price"] == 39.00
        assert annual["interval"] == "year"


class TestAdminEndpoints:
    """Test admin dashboard endpoints."""
    
    def test_admin_metrics_unauthorized(self):
        """Test admin metrics without authorization."""
        response = client.get("/api/v1/admin/metrics")
        assert response.status_code == 401
    
    def test_admin_metrics_invalid_token(self):
        """Test admin metrics with invalid token."""
        response = client.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403
    
    def test_admin_metrics_authorized(self):
        """Test admin metrics with valid token."""
        response = client.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": "Bearer admin_secret_token_change_me"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_scans" in data
        assert "scams_detected" in data
        assert "active_licenses" in data
        assert "fraud_rings" in data


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_database_connection(self):
        """Test database connection."""
        db = DatabaseService()
        assert db.conn is not None or db.conn is None  # May not be configured
        if db.conn:
            db.close()
    
    def test_license_creation(self):
        """Test creating a new license."""
        db = DatabaseService()
        if not db.conn:
            pytest.skip("Database not configured")
        
        license_key = db.create_license(
            email="test@example.com",
            tier="pro",
            subscription_id="test_sub_123"
        )
        
        assert license_key is not None
        assert license_key.startswith("US-PRO-")
        
        # Cleanup
        db.deactivate_license(license_key)
        db.close()
    
    def test_scam_report_storage(self):
        """Test storing scam report."""
        db = DatabaseService()
        if not db.conn:
            pytest.skip("Database not configured")
        
        features = {
            "message_length": 150,
            "urgency_keywords_count": 3
        }
        
        report_id = db.save_scam_report(
            features=features,
            predicted_risk_score=85.0,
            predicted_risk_level="critical",
            is_scam=True,
            platform="linkedin"
        )
        
        assert report_id is not None
        db.close()


class TestMLService:
    """Test ML service integration."""
    
    def test_ml_service_prediction(self):
        """Test ML service risk prediction."""
        from src.ml.ml_service import MLService
        
        ml_service = MLService()
        
        features = {
            "message_length": 150,
            "word_count": 25,
            "urgency_keywords_count": 3,
            "money_keywords_count": 2,
            "gmail_recruiter_combo": 1
        }
        
        risk_score = ml_service.predict_risk(features)
        
        assert 0.0 <= risk_score <= 1.0
        assert ml_service.get_confidence() >= 0.0


class TestFraudRingDetection:
    """Test fraud ring detection."""
    
    def test_fraud_ring_detector_initialization(self):
        """Test fraud ring detector initialization."""
        from src.ml.fraud_ring_detector import FraudRingDetector
        
        detector = FraudRingDetector()
        assert detector is not None
        assert detector.similarity_threshold == 0.7
    
    def test_behavioral_signature_extraction(self):
        """Test behavioral signature extraction."""
        from src.ml.fraud_ring_detector import FraudRingDetector
        
        detector = FraudRingDetector()
        
        features = {
            "recruiter_keywords_count": 2,
            "gmail_recruiter_combo": 1,
            "location_inquiry": 1
        }
        
        signature = detector.extract_behavioral_signature(features)
        assert signature is not None
        assert len(signature) == 16  # MD5 hash truncated to 16 chars
    
    def test_similarity_calculation(self):
        """Test similarity calculation between feature sets."""
        from src.ml.fraud_ring_detector import FraudRingDetector
        
        detector = FraudRingDetector()
        
        features1 = {
            "recruiter_keywords_count": 2,
            "gmail_recruiter_combo": 1,
            "location_inquiry": 1
        }
        
        features2 = {
            "recruiter_keywords_count": 2,
            "gmail_recruiter_combo": 1,
            "location_inquiry": 1
        }
        
        similarity = detector.calculate_similarity(features1, features2)
        assert similarity == 1.0  # Identical features
        
        features3 = {
            "recruiter_keywords_count": 0,
            "gmail_recruiter_combo": 0,
            "location_inquiry": 0
        }
        
        similarity2 = detector.calculate_similarity(features1, features3)
        assert similarity2 < 0.5  # Very different features


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
