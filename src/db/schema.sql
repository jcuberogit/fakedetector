-- UniversalShield Database Schema
-- PostgreSQL schema for feedback storage, license management, and ML training data

-- Users and License Management
CREATE TABLE IF NOT EXISTS licenses (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    tier VARCHAR(20) NOT NULL DEFAULT 'free', -- 'free' or 'pro'
    active BOOLEAN DEFAULT TRUE,
    subscription_id VARCHAR(100), -- PayPal/Stripe subscription ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_validated TIMESTAMP,
    scans_used_today INTEGER DEFAULT 0,
    scans_reset_date DATE DEFAULT CURRENT_DATE
);

CREATE INDEX idx_licenses_key ON licenses(license_key);
CREATE INDEX idx_licenses_email ON licenses(email);

-- Scam Reports (User Feedback for ML Training)
CREATE TABLE IF NOT EXISTS scam_reports (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50),
    features JSONB NOT NULL, -- Anonymized feature vector
    predicted_risk_score FLOAT,
    predicted_risk_level VARCHAR(20),
    is_scam BOOLEAN NOT NULL, -- User label: true = scam, false = false positive
    platform VARCHAR(50), -- 'linkedin', 'gmail', 'outlook'
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_for_training BOOLEAN DEFAULT FALSE,
    training_batch_id INTEGER,
    FOREIGN KEY (license_key) REFERENCES licenses(license_key) ON DELETE SET NULL
);

CREATE INDEX idx_scam_reports_license ON scam_reports(license_key);
CREATE INDEX idx_scam_reports_training ON scam_reports(used_for_training);
CREATE INDEX idx_scam_reports_date ON scam_reports(reported_at);

-- API Request Logs (Rate Limiting & Analytics)
CREATE TABLE IF NOT EXISTS api_requests (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50),
    endpoint VARCHAR(100) NOT NULL,
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    risk_score INTEGER,
    risk_level VARCHAR(20),
    tier VARCHAR(20),
    FOREIGN KEY (license_key) REFERENCES licenses(license_key) ON DELETE SET NULL
);

CREATE INDEX idx_api_requests_license ON api_requests(license_key);
CREATE INDEX idx_api_requests_timestamp ON api_requests(request_timestamp);

-- ML Model Training History
CREATE TABLE IF NOT EXISTS model_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'xgboost', 'neural_network', etc.
    training_samples_count INTEGER,
    accuracy FLOAT,
    precision_score FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    model_path VARCHAR(255),
    feature_count INTEGER,
    notes TEXT
);

CREATE INDEX idx_model_versions_active ON model_versions(is_active);

-- Training Batches (Track which reports were used for which training run)
CREATE TABLE IF NOT EXISTS training_batches (
    id SERIAL PRIMARY KEY,
    model_version_id INTEGER,
    batch_size INTEGER,
    scam_count INTEGER,
    legitimate_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_version_id) REFERENCES model_versions(id) ON DELETE CASCADE
);

-- Fraud Ring Detection (Future: GNN)
CREATE TABLE IF NOT EXISTS fraud_rings (
    id SERIAL PRIMARY KEY,
    ring_identifier VARCHAR(100) UNIQUE NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    member_count INTEGER DEFAULT 1,
    confidence_score FLOAT,
    pattern_type VARCHAR(50), -- 'rachel_good', 'financial_phishing', etc.
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'resolved', 'false_positive'
    notes TEXT
);

-- Fraud Ring Members (Anonymized identifiers)
CREATE TABLE IF NOT EXISTS fraud_ring_members (
    id SERIAL PRIMARY KEY,
    ring_id INTEGER NOT NULL,
    anonymized_identifier VARCHAR(255) NOT NULL, -- Hash of email/profile
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 1,
    FOREIGN KEY (ring_id) REFERENCES fraud_rings(id) ON DELETE CASCADE
);

CREATE INDEX idx_fraud_ring_members_ring ON fraud_ring_members(ring_id);
CREATE INDEX idx_fraud_ring_members_identifier ON fraud_ring_members(anonymized_identifier);

-- Analytics & Metrics
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE UNIQUE NOT NULL,
    total_scans INTEGER DEFAULT 0,
    scams_detected INTEGER DEFAULT 0,
    false_positives_reported INTEGER DEFAULT 0,
    free_tier_scans INTEGER DEFAULT 0,
    pro_tier_scans INTEGER DEFAULT 0,
    new_licenses INTEGER DEFAULT 0,
    active_licenses INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_daily_metrics_date ON daily_metrics(metric_date);

-- Initial demo license
INSERT INTO licenses (license_key, email, tier, active) 
VALUES ('US-PRO-DEMO12345678', 'demo@universalshield.dev', 'pro', TRUE)
ON CONFLICT (license_key) DO NOTHING;
