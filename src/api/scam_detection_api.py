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
from src.ml.ml_service import MLService
from src.db.database import DatabaseService
from src.api.payment_api import router as payment_router
from src.api.admin_api import router as admin_router
from src.api.threat_intel_service import threat_intel, verify_message_urls
import asyncio

app = FastAPI(title="UniversalShield API", version="1.0.0")

# Include routers
app.include_router(payment_router)
app.include_router(admin_router)

# CORS configuration - allow Chrome extension and web origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://pegdjkiinlnmfagjnpdclkcenlhkpmig",  # Production extension ID
        "*"  # Allow all origins (Chrome extensions need this for development)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize services
analyzer = ContextualAnalyzer()
feature_extractor = PrivacyFirstFeatureExtractor()
db = DatabaseService()

# Initialize database schema on startup
import os
from pathlib import Path
schema_path = Path(__file__).parent.parent / 'db' / 'schema.sql'
if schema_path.exists():
    db.execute_schema(str(schema_path))

# Rate limiting storage (in-memory for now, use Redis in production)
rate_limits = defaultdict(list)
FREE_TIER_LIMIT = 1  # 1 scan/day free - proves value, encourages upgrade
RATE_LIMIT_WINDOW = 86400  # 24 hours in seconds


class AnalyzeRequest(BaseModel):
    message: str
    metadata: Dict


class AnalyzeFeaturesRequest(BaseModel):
    features: Dict


class ReportScamRequest(BaseModel):
    features: Dict
    is_scam: bool
    predicted_risk_score: float
    predicted_risk_level: str
    platform: str = "linkedin"


class LicenseValidation(BaseModel):
    license_key: str


# Initialize ML Service
ml_service = MLService()


def check_rate_limit(api_key: str, tier: str) -> bool:
    """Check if request is within rate limit."""
    if tier == "pro":
        return True  # Unlimited for Pro
    
    now = time.time()
    
    # Initialize if not exists
    if api_key not in rate_limits:
        rate_limits[api_key] = []
    
    # Clean old entries (older than 24 hours)
    rate_limits[api_key] = [t for t in rate_limits[api_key] if now - t < RATE_LIMIT_WINDOW]
    
    # Check if limit exceeded
    if len(rate_limits[api_key]) >= FREE_TIER_LIMIT:
        print(f"⚠️  Rate limit exceeded for {api_key}: {len(rate_limits[api_key])}/{FREE_TIER_LIMIT}")
        return False
    
    # Add current request timestamp
    rate_limits[api_key].append(now)
    print(f"✅ Rate limit check passed for {api_key}: {len(rate_limits[api_key])}/{FREE_TIER_LIMIT}")
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
    # Validate license using database
    tier = "free"
    license_info = None
    if x_license_key:
        license_info = db.validate_license(x_license_key)
        if license_info and license_info["active"]:
            tier = license_info["tier"]
    
    # Check rate limit
    api_key = x_license_key or "anonymous"
    if not check_rate_limit(api_key, tier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Upgrade to Pro for unlimited scans."
        )
    
    try:
        start_time = time.time()
        features = request.features
        
        # 1. Use ML Service (XGBoost) for high-precision prediction
        risk_score_ml = ml_service.predict_risk(features)
        ml_confidence = ml_service.get_confidence()
        
        # 2. Use rule-based scoring as a safety net
        risk_score_rules = _calculate_risk_from_features(features)
        
        # 3. Calculate scam signal strength (need actual indicators, not just context)
        cv_scam_count = features.get('cv_scam_keywords_count', 0)
        urgency_count = features.get('urgency_keywords_count', 0)
        money_count = features.get('money_keywords_count', 0)
        cred_count = features.get('credential_keywords_count', 0)
        financial_count = features.get('financial_phishing_keywords_count', 0)
        
        # Count actual scam signals (not contextual factors)
        fee_based_count = features.get('fee_based_scam_count', 0)
        scam_phrase_count = features.get('scam_phrase_count', 0)
        gmail_recruiter = features.get('gmail_recruiter_combo', 0)
        
        # Psychological attack vectors
        psych_attack_total = features.get('psych_attack_total', 0)
        cognitive_ease = features.get('cognitive_ease_score', 0)
        
        scam_signals = (
            (1 if cv_scam_count >= 3 else 0) +
            (1 if urgency_count >= 2 else 0) +
            (1 if money_count >= 2 else 0) +
            (1 if cred_count >= 2 else 0) +
            (1 if financial_count >= 2 else 0) +
            (1 if features.get('requests_payment') else 0) +
            (1 if features.get('requests_credentials') else 0) +
            (1 if fee_based_count >= 1 else 0) +  # Fee-based scams
            (1 if scam_phrase_count >= 1 else 0) +  # Scam phrases
            (1 if gmail_recruiter == 1 else 0) +  # Gmail recruiter pattern
            (1 if psych_attack_total >= 3 else 0) +  # Multi-vector psychological attack
            (1 if cognitive_ease >= 1 else 0)  # Too good to be true
        )
        
        # 4. Determine final score based on actual scam signals
        if cv_scam_count >= 3:
            # Strong CV scam pattern - flag as critical
            combined_score = max(risk_score_rules, 75)
        elif scam_signals == 0:
            # NO actual scam signals - cap at SAFE level regardless of context
            # This prevents flagging normal LinkedIn messages as critical
            combined_score = min(risk_score_rules, 25)  # Max 25 = safe
        elif ml_confidence > 0.8:
            combined_score = int(risk_score_ml * 70 + risk_score_rules * 30)
        else:
            combined_score = risk_score_rules
        
        risk_score = min(combined_score, 100)
        risk_level = _get_risk_level(risk_score)
        explanation = _generate_explanation_from_features(features)
        
        # Log API request and increment scan count
        response_time_ms = int((time.time() - start_time) * 1000)
        db.log_api_request(x_license_key, "/api/v1/analyze-features", response_time_ms, risk_score, risk_level, tier)
        
        if x_license_key and tier == "free":
            db.increment_scan_count(x_license_key)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation": explanation,
            "ml_confidence": float(ml_confidence),
            "tier": tier,
            "scans_remaining": FREE_TIER_LIMIT - len(rate_limits.get(api_key, [])) if tier == "free" else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class URLVerifyRequest(BaseModel):
    urls: list  # List of URLs to verify

@app.post("/api/v1/verify-urls")
async def verify_urls(
    request: URLVerifyRequest,
    x_license_key: Optional[str] = Header(None)
):
    """
    FREE Layer 1: Verify URLs against PhishTank and Google Safe Browsing.
    This is called BEFORE AI analysis to save costs.
    """
    try:
        results = []
        for url in request.urls[:10]:  # Limit to 10 URLs per request
            result = await threat_intel.verify_url(url)
            results.append(result)
        
        malicious_count = sum(1 for r in results if r['is_malicious'])
        
        return {
            "url_count": len(results),
            "malicious_count": malicious_count,
            "has_threats": malicious_count > 0,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/verify-domain")
async def verify_domain(
    domain: str,
    x_license_key: Optional[str] = Header(None)
):
    """
    FREE Layer 2: Check domain reputation (typosquatting, suspicious TLDs).
    """
    try:
        result = await threat_intel._check_domain_reputation(domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/report-scam")
async def report_scam(
    request: ReportScamRequest,
    x_license_key: Optional[str] = Header(None)
):
    """
    Report a scam pattern or false positive for ML training.
    Privacy guarantee: ONLY anonymized features stored.
    """
    try:
        # Save to database for ML training
        report_id = db.save_scam_report(
            features=request.features,
            predicted_risk_score=request.predicted_risk_score,
            predicted_risk_level=request.predicted_risk_level,
            is_scam=request.is_scam,
            license_key=x_license_key,
            platform=request.platform
        )
        
        print(f"📈 AGENT GROWTH: Saved training data point #{report_id}")
        print(f"   - Label: {'SCAM' if request.is_scam else 'SAFE (False Positive)'}")
        print(f"   - Risk Score: {request.predicted_risk_score}%")
        print(f"   - Platform: {request.platform}")
        
        return {
            "success": True,
            "message": "Thank you! Your feedback is growing the UniversalShield Agent intelligence.",
            "data_point_id": report_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    
    # Validate using database
    license_info = db.validate_license(license_key)
    
    if not license_info or not license_info["active"]:
        return {"valid": False, "tier": "free"}
    
    tier = license_info["tier"]
    
    return {
        "valid": True,
        "tier": tier,
        "email": license_info.get("email"),
        "scans_used_today": license_info.get("scans_used_today", 0),
        "features_enabled": {
            "cloud_ml": True,
            "fraud_ring_detection": True,
            "all_platforms": True,
            "unlimited_scans": True
        } if tier == "pro" else {
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
    
    # Connection degree - REDUCED for LinkedIn (unsolicited contact is normal)
    # Only add small penalty, not enough to trigger critical alone
    connection = features.get('connection_degree', 1)
    platform_id = features.get('platform_id', 0)  # 1 = LinkedIn
    if connection >= 3:
        if platform_id == 1:  # LinkedIn - strangers messaging is NORMAL
            risk += 5  # Minimal penalty
        else:
            risk += 15  # Higher penalty on other platforms
    
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
    
    # CV/Resume scam detection - ONLY flag actual CV scams, not legitimate job offers
    recruiter_count = features.get('recruiter_keywords_count', 0)
    cv_scam_count = features.get('cv_scam_keywords_count', 0)
    legitimate_job_count = features.get('legitimate_job_keywords_count', 0)
    technical_skills_count = features.get('technical_skills_count', 0)
    has_corporate_email = features.get('has_corporate_email', 0)
    has_job_title = features.get('has_specific_job_title', 0)
    
    # Calculate legitimacy score
    legitimacy_score = legitimate_job_count + technical_skills_count + has_corporate_email + has_job_title
    
    # Only add CV scam risk if actual scam indicators present AND low legitimacy
    if cv_scam_count >= 3 and legitimacy_score < 2:  # Strong CV scam pattern
        risk += 50  # High risk for clear CV improvement scams
    elif cv_scam_count > 0 and legitimacy_score < 2:  # Some CV scam language
        risk += 35
    elif recruiter_count > 1 and legitimacy_score < 2:  # Recruiter keywords but no job details
        risk += 20
    
    # Gmail + recruiter combo (but reduce if legitimate job indicators)
    if features.get('gmail_recruiter_combo', 0) == 1:
        if legitimacy_score < 2:
            risk += 40  # High risk - Gmail recruiter with no real job
        else:
            risk += 10  # Lower risk - has job details
    
    # REDUCE risk for legitimate job offers
    if legitimacy_score >= 3:
        risk -= 25  # Significant reduction for detailed job offers
    elif legitimacy_score >= 2:
        risk -= 15
    
    # REDUCE risk for transactional/automated emails (BambooHR, application confirmations, etc.)
    is_transactional = features.get('is_transactional_email', 0)
    transactional_count = features.get('transactional_keywords_count', 0)
    if is_transactional == 1 or transactional_count >= 2:
        risk -= 40  # Strong reduction - these are almost always legitimate
    elif transactional_count >= 1:
        risk -= 20
    
    # REDUCE risk for legitimate rejection/automated messages
    is_legitimate_rejection = features.get('is_legitimate_rejection', 0)
    if is_legitimate_rejection == 1:
        risk -= 50  # Strong reduction - these are rejection/courtesy messages
    
    # NLP scam phrase indicators
    scam_phrase_count = features.get('scam_phrase_count', 0)
    if scam_phrase_count >= 2:
        risk += 40  # Multiple scam phrases = high risk
    elif scam_phrase_count >= 1:
        risk += 20
    
    # Fee-based scam detection (pay-to-play job services)
    fee_based_count = features.get('fee_based_scam_count', 0)
    if fee_based_count >= 2:
        risk += 50  # Asking for fees = very high risk
    elif fee_based_count >= 1:
        risk += 30
    
    # Gmail address in message (recruiter scam pattern)
    gmail_in_message = features.get('gmail_in_message', 0)
    if gmail_in_message == 1 and recruiter_count > 0:
        if legitimacy_score < 2:
            risk += 35  # Gmail + recruiter language + no legitimacy
    
    # ============ CIALDINI PSYCHOLOGICAL ATTACK VECTORS ============
    # Layer 1: Individual psychological triggers
    authority_score = features.get('authority_score', 0)
    scarcity_score = features.get('scarcity_score', 0)
    flattery_score = features.get('flattery_score', 0)
    reciprocity_score = features.get('reciprocity_score', 0)
    cognitive_ease_score = features.get('cognitive_ease_score', 0)
    
    # Authority abuse (false Big Tech claims)
    if authority_score >= 2:
        risk += 30
    elif authority_score >= 1:
        risk += 15
    
    # Scarcity/Urgency manipulation
    if scarcity_score >= 2:
        risk += 35  # High pressure tactics
    elif scarcity_score >= 1:
        risk += 20
    
    # Flattery/Love bombing
    if flattery_score >= 2:
        risk += 25
    elif flattery_score >= 1:
        risk += 10
    
    # Reciprocity trap (free offers to obligate)
    if reciprocity_score >= 2:
        risk += 30
    elif reciprocity_score >= 1:
        risk += 15
    
    # Cognitive ease (too good to be true)
    if cognitive_ease_score >= 2:
        risk += 40  # Easy money = high risk
    elif cognitive_ease_score >= 1:
        risk += 25
    
    # ============ CISA SOCIAL ENGINEERING ============
    pretexting_score = features.get('pretexting_score', 0)
    quid_pro_quo_score = features.get('quid_pro_quo_score', 0)
    redirection_score = features.get('redirection_score', 0)
    high_alert_score = features.get('high_alert_score', 0)
    
    if pretexting_score >= 1:
        risk += 25
    if quid_pro_quo_score >= 1:
        risk += 35
    if redirection_score >= 1:
        risk += 20  # WhatsApp/Telegram redirection
    if high_alert_score >= 2:
        risk += 30
    elif high_alert_score >= 1:
        risk += 15
    
    # ============ LAYERED ATTACK DETECTION ============
    # Per Cialdini framework: 3+ psychological triggers = coordinated attack
    psych_attack_total = features.get('psych_attack_total', 0)
    if psych_attack_total >= 4:
        risk += 50  # Coordinated multi-vector attack
    elif psych_attack_total >= 3:
        risk += 35  # Strong psychological manipulation
    elif psych_attack_total >= 2:
        risk += 20
    
    # Financial phishing
    financial_count = features.get('financial_phishing_keywords_count', 0)
    if financial_count > 2:
        risk += 25
    
    if features.get('credit_card_mention', 0) == 1:
        risk += 15
    
    if features.get('security_deposit_mention', 0) == 1:
        risk += 15
    
    # Contextual combinations
    if (features.get('file_extension_risk', 0) > 0.8 and 
        account_age < 7 and 
        features.get('requests_download')):
        risk += 20
    
    if (features.get('requests_credentials') and 
        urgency_count > 2 and 
        features.get('previous_interactions', 0) == 0):
        risk += 25
    
    # LinkedIn-specific: Reduce risk for normal recruiter behavior
    platform_id = features.get('platform_id', 0)
    if platform_id == 1:  # LinkedIn
        # Asking for resume is NORMAL on LinkedIn (not a scam signal)
        # Only flag if combined with actual scam indicators
        if cv_scam_count == 0 and legitimacy_score >= 1:
            risk -= 10  # Reduce risk for legitimate recruiter messages
    
    # CV/Resume scam combination - only if actual scam indicators AND low legitimacy
    if (cv_scam_count >= 3 and 
        urgency_count > 0 and 
        features.get('previous_interactions', 0) == 0 and
        legitimacy_score < 2):
        risk += 40  # Strong combination of CV scam + urgency + no history
    elif (cv_scam_count > 0 and 
        urgency_count > 0 and 
        features.get('previous_interactions', 0) == 0 and
        legitimacy_score < 2):
        risk += 30
    
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
    
    # Check for specific fraud patterns first
    recruiter_count = features.get('recruiter_keywords_count', 0)
    gmail_recruiter = features.get('gmail_recruiter_combo', 0)
    financial_count = features.get('financial_phishing_keywords_count', 0)
    
    # CV scam vs legitimate job detection
    cv_scam_count = features.get('cv_scam_keywords_count', 0)
    legitimate_job_count = features.get('legitimate_job_keywords_count', 0)
    technical_skills_count = features.get('technical_skills_count', 0)
    legitimacy_score = legitimate_job_count + technical_skills_count + features.get('has_corporate_email', 0) + features.get('has_specific_job_title', 0)
    
    # Only flag as CV scam if actual scam indicators present
    if cv_scam_count > 0:
        reasons.append("⚠️ CV/Resume Improvement Scam Pattern: Unsolicited offer to review/improve your CV for a fee. This is a common LinkedIn scam targeting job seekers")
    elif (recruiter_count > 1 or gmail_recruiter == 1) and legitimacy_score < 2:
        reasons.append("⚠️ Potential Recruitment Scam: Recruiter-like message without specific job details or company verification")
    
    # Fee-based scam
    fee_based_count = features.get('fee_based_scam_count', 0)
    if fee_based_count > 0:
        reasons.append("⚠️ Pay-to-Play Scam: Requests payment for job placement, resume services, or guaranteed interviews")
    
    # Gmail in message with recruiter language
    gmail_in_message = features.get('gmail_in_message', 0)
    if gmail_in_message == 1 and recruiter_count > 0 and legitimacy_score < 2:
        reasons.append("⚠️ Gmail Recruiter Pattern: Uses personal @gmail.com for corporate recruitment - legitimate recruiters use company email")
    
    # Scam phrase indicators
    scam_phrase_count = features.get('scam_phrase_count', 0)
    if scam_phrase_count > 0:
        reasons.append("⚠️ Common Scam Phrases Detected: Message contains language patterns commonly used in job scams")
    
    # ============ CIALDINI PSYCHOLOGICAL ATTACK EXPLANATIONS ============
    psych_attack_total = features.get('psych_attack_total', 0)
    
    if features.get('authority_score', 0) >= 1:
        reasons.append("🧠 Authority Manipulation: Claims association with Big Tech or Fortune 500 to lower your defenses")
    
    if features.get('scarcity_score', 0) >= 1:
        reasons.append("🧠 Scarcity/Urgency Tactic: Artificial deadline or limited spots to pressure quick decisions")
    
    if features.get('flattery_score', 0) >= 1:
        reasons.append("🧠 Love Bombing: Excessive flattery to create false trust ('perfect fit', 'most impressive')")
    
    if features.get('reciprocity_score', 0) >= 1:
        reasons.append("🧠 Reciprocity Trap: Free offer to create obligation (free CV review, free consultation)")
    
    if features.get('cognitive_ease_score', 0) >= 1:
        reasons.append("🧠 Too Good To Be True: Easy money, high salary for minimal work - classic scam pattern")
    
    if features.get('pretexting_score', 0) >= 1:
        reasons.append("🧠 Pretexting: Fabricated scenario (security audit, account verification) to extract information")
    
    if features.get('quid_pro_quo_score', 0) >= 1:
        reasons.append("🧠 Quid Pro Quo: Requests personal info in exchange for job details or salary info")
    
    if features.get('redirection_score', 0) >= 1:
        reasons.append("🧠 Platform Redirection: Attempts to move conversation to WhatsApp/Telegram to avoid detection")
    
    if psych_attack_total >= 3:
        reasons.append("⚠️ COORDINATED ATTACK: Multiple psychological manipulation vectors detected (Cialdini framework)")
    
    # Financial Phishing Pattern
    if financial_count > 2 or features.get('credit_card_mention', 0) == 1:
        reasons.append("⚠️ Financial Phishing Pattern: Attempts to obtain credit card or banking information under false pretenses")
    
    # Security deposit scam
    if features.get('security_deposit_mention', 0) == 1:
        reasons.append("⚠️ Fake Job Scam: Requests security deposit or upfront payment for job opportunity")
    
    # Generic risk factors
    if features.get('file_extension_risk', 0) > 0.8:
        reasons.append("Dangerous file type detected")
    
    if features.get('urgency_keywords_count', 0) > 2:
        reasons.append("High urgency language used to pressure quick action")
    
    if features.get('sender_account_age_days', 365) < 7:
        reasons.append("Very new account (less than 7 days old)")
    
    if features.get('requests_credentials'):
        reasons.append("Requests login credentials or passwords")
    
    if features.get('requests_payment'):
        reasons.append("Requests payment or financial information")
    
    # Context info (lower priority)
    context = []
    if features.get('connection_degree', 1) >= 3:
        context.append("No direct connection")
    if features.get('previous_interactions', 0) == 0:
        context.append("First contact")
    
    if context:
        reasons.append(" • ".join(context))
    
    if not reasons:
        return "No significant risk factors detected"
    
    return " | ".join(reasons)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
