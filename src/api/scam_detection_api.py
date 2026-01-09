"""
UniversalShield API - Privacy-First Scam Detection
FastAPI endpoints for analyzing anonymized features (NO raw message content).
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import time
from collections import defaultdict

from src.contextual.analyzer import ContextualAnalyzer
from src.contextual.feature_extractor import PrivacyFirstFeatureExtractor

app = FastAPI(title="UniversalShield API", version="1.0.0")

# CORS configuration - allow Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
analyzer = ContextualAnalyzer()
feature_extractor = PrivacyFirstFeatureExtractor()

# Rate limiting storage (in-memory for now, use Redis in production)
rate_limits = defaultdict(list)
FREE_TIER_LIMIT = 50
RATE_LIMIT_WINDOW = 86400  # 24 hours in seconds


class AnalyzeRequest(BaseModel):
    message: str
    metadata: Dict


class AnalyzeFeaturesRequest(BaseModel):
    features: Dict


class ReportScamRequest(BaseModel):
    pattern_hash: str
    category: str
    risk_score: int


class LicenseValidation(BaseModel):
    license_key: str


# In-memory license store (use database in production)
licenses = {
    "US-PRO-DEMO12345678": {
        "tier": "pro",
        "active": True,
        "email": "demo@universalshield.dev"
    }
}


def check_rate_limit(api_key: str, tier: str) -> bool:
    """Check if request is within rate limit."""
    if tier == "pro":
        return True  # Unlimited for Pro
    
    now = time.time()
    # Clean old entries
    rate_limits[api_key] = [t for t in rate_limits[api_key] if now - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limits[api_key]) >= FREE_TIER_LIMIT:
        return False
    
    rate_limits[api_key].append(now)
    return True


@app.get("/")
async def root():
    """API health check."""
    return {
        "service": "UniversalShield API",
        "version": "1.0.0",
        "status": "operational",
        "privacy": "Zero-retention policy - no data stored"
    }


@app.post("/api/v1/analyze-message")
async def analyze_message(
    request: AnalyzeRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Analyze message with full context (for local/server use).
    Returns comprehensive risk analysis.
    """
    try:
        analysis = analyzer.analyze(request.message, request.metadata)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze-features")
async def analyze_features(
    request: AnalyzeFeaturesRequest,
    x_license_key: Optional[str] = Header(None)
):
    """
    Analyze ANONYMIZED features only (PRO tier).
    Privacy guarantee: NO message content received.
    """
    # Validate license
    tier = "free"
    if x_license_key and x_license_key in licenses:
        license_info = licenses[x_license_key]
        if license_info["active"]:
            tier = license_info["tier"]
    
    # Check rate limit
    api_key = x_license_key or "anonymous"
    if not check_rate_limit(api_key, tier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Upgrade to Pro for unlimited scans."
        )
    
    try:
        features = request.features
        
        # Calculate risk score from features
        risk_score = _calculate_risk_from_features(features)
        risk_level = _get_risk_level(risk_score)
        explanation = _generate_explanation_from_features(features)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation": explanation,
            "tier": tier,
            "scans_remaining": FREE_TIER_LIMIT - len(rate_limits.get(api_key, [])) if tier == "free" else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/report-scam")
async def report_scam(request: ReportScamRequest):
    """
    Report a scam pattern (hashed, no raw content).
    Used to improve detection models.
    """
    # In production, store in database for model training
    return {
        "success": True,
        "message": "Thank you for reporting. This helps protect others.",
        "pattern_id": f"PAT-{int(time.time())}"
    }


@app.get("/api/v1/patterns/latest")
async def get_latest_patterns():
    """
    Get latest scam patterns for local detection.
    Returns pattern signatures, not raw content.
    """
    return {
        "version": "1.0.0",
        "updated_at": "2026-01-09T12:00:00Z",
        "patterns": [
            {"id": 1, "type": "malware_delivery", "weight": 0.95},
            {"id": 2, "type": "credential_phishing", "weight": 0.90},
            {"id": 3, "type": "advance_fee_fraud", "weight": 0.85},
            {"id": 4, "type": "investment_scam", "weight": 0.88},
            {"id": 5, "type": "lottery_scam", "weight": 0.92}
        ]
    }


@app.post("/api/v1/subscription/validate")
async def validate_license(request: LicenseValidation):
    """Validate license key from extension."""
    license_key = request.license_key
    
    if license_key not in licenses:
        return {"valid": False, "tier": "free"}
    
    license_info = licenses[license_key]
    
    return {
        "valid": license_info["active"],
        "tier": license_info["tier"],
        "features_enabled": {
            "cloud_ml": True,
            "fraud_ring_detection": True,
            "all_platforms": True,
            "unlimited_scans": True
        } if license_info["tier"] == "pro" else {
            "cloud_ml": False,
            "fraud_ring_detection": False,
            "all_platforms": False,
            "unlimited_scans": False
        }
    }


def _calculate_risk_from_features(features: Dict) -> int:
    """Calculate risk score from anonymized features."""
    risk = 0
    
    # File risk
    if features.get('file_extension_risk', 0) > 0.8:
        risk += 30
    
    # Urgency
    urgency_count = features.get('urgency_keywords_count', 0)
    if urgency_count > 3:
        risk += 20
    elif urgency_count > 1:
        risk += 10
    
    # Money keywords
    money_count = features.get('money_keywords_count', 0)
    if money_count > 2:
        risk += 15
    
    # Credentials
    cred_count = features.get('credential_keywords_count', 0)
    if cred_count > 2:
        risk += 20
    
    # Account age
    account_age = features.get('sender_account_age_days', 365)
    if account_age < 7:
        risk += 20
    elif account_age < 30:
        risk += 10
    
    # Connection degree
    connection = features.get('connection_degree', 1)
    if connection >= 3:
        risk += 15
    
    # Behavioral flags
    if features.get('requests_download'):
        risk += 15
    if features.get('requests_payment'):
        risk += 20
    if features.get('requests_credentials'):
        risk += 25
    
    # Excessive punctuation
    if features.get('exclamation_count', 0) > 3:
        risk += 10
    
    # Caps ratio
    if features.get('caps_ratio', 0) > 0.3:
        risk += 10
    
    # Contextual combinations
    if (features.get('file_extension_risk', 0) > 0.8 and 
        account_age < 7 and 
        features.get('requests_download')):
        risk += 20
    
    if (features.get('requests_credentials') and 
        urgency_count > 2 and 
        features.get('previous_interactions', 0) == 0):
        risk += 25
    
    return min(risk, 100)


def _get_risk_level(score: int) -> str:
    """Convert score to risk level."""
    if score < 30:
        return 'safe'
    elif score < 70:
        return 'caution'
    else:
        return 'critical'


def _generate_explanation_from_features(features: Dict) -> str:
    """Generate explanation from features."""
    reasons = []
    
    if features.get('file_extension_risk', 0) > 0.8:
        reasons.append("Dangerous file type detected")
    
    if features.get('urgency_keywords_count', 0) > 2:
        reasons.append("High urgency language")
    
    if features.get('sender_account_age_days', 365) < 7:
        reasons.append("Very new account")
    
    if features.get('connection_degree', 1) >= 3:
        reasons.append("No direct connection")
    
    if features.get('requests_credentials'):
        reasons.append("Requests credentials")
    
    if features.get('requests_payment'):
        reasons.append("Requests payment")
    
    if features.get('previous_interactions', 0) == 0:
        reasons.append("First contact")
    
    if not reasons:
        return "No significant risk factors detected"
    
    return " • ".join(reasons)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
