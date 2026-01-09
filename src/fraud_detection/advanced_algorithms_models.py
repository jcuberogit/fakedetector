#!/usr/bin/env python3
"""
Advanced Fraud Algorithms Models
Python equivalent of C# AdvancedFraudAlgorithms data structures
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class Platform(str, Enum):
    """Platform types"""
    MOBILE = "mobile"
    WEB = "web"
    API = "api"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Severity(str, Enum):
    """Severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskFactor(BaseModel):
    """Individual risk factor contributing to overall risk assessment"""
    type: str = Field(..., description="Type of risk factor")
    weight: Decimal = Field(..., description="Risk weight (0.0 to 1.0)")
    description: str = Field(..., description="Description of the risk factor")
    severity: Severity = Field(default=Severity.LOW, description="Severity level")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudRiskScore(BaseModel):
    """Comprehensive fraud risk score with contributing factors"""
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    risk_score: Decimal = Field(..., description="Overall risk score (0.0 to 1.0)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Contributing risk factors")
    recommended_action: str = Field(..., description="Recommended action")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    platform: str = Field(default="api", description="Platform")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PlatformRiskWeights(BaseModel):
    """Platform-specific risk weights"""
    behavioral_weight: float = Field(default=0.25, description="Behavioral risk weight")
    transactional_weight: float = Field(default=0.20, description="Transactional risk weight")
    network_weight: float = Field(default=0.20, description="Network risk weight")
    device_weight: float = Field(default=0.20, description="Device risk weight")
    velocity_weight: float = Field(default=0.15, description="Velocity risk weight")


class BehavioralProfile(BaseModel):
    """User behavioral profile"""
    user_id: str = Field(..., description="User identifier")
    average_amount: Decimal = Field(default=Decimal('0'), description="Average transaction amount")
    typical_merchants: List[str] = Field(default_factory=list, description="Typical merchants")
    typical_locations: List[str] = Field(default_factory=list, description="Typical locations")
    typical_hours: List[int] = Field(default_factory=list, description="Typical transaction hours")
    transaction_frequency: float = Field(default=0.0, description="Transactions per day")
    risk_tolerance: Decimal = Field(default=Decimal('0.5'), description="Risk tolerance")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation time")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DeviceProfile(BaseModel):
    """Device profile for fraud detection"""
    device_id: str = Field(..., description="Device identifier")
    user_id: str = Field(..., description="User identifier")
    device_type: str = Field(default="", description="Device type")
    os_version: str = Field(default="", description="Operating system version")
    browser_version: str = Field(default="", description="Browser version")
    screen_resolution: str = Field(default="", description="Screen resolution")
    timezone: str = Field(default="", description="Timezone")
    language: str = Field(default="", description="Language")
    fingerprint: str = Field(default="", description="Device fingerprint")
    risk_score: Decimal = Field(default=Decimal('0.5'), description="Device risk score")
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First seen")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen")
    transaction_count: int = Field(default=0, description="Transaction count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class NetworkProfile(BaseModel):
    """Network profile for fraud detection"""
    user_id: str = Field(..., description="User identifier")
    ip_address: str = Field(default="", description="IP address")
    location: str = Field(default="", description="Location")
    isp: str = Field(default="", description="Internet service provider")
    proxy_detected: bool = Field(default=False, description="Proxy detected")
    vpn_detected: bool = Field(default=False, description="VPN detected")
    tor_detected: bool = Field(default=False, description="Tor detected")
    risk_score: Decimal = Field(default=Decimal('0.5'), description="Network risk score")
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First seen")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Last seen")
    transaction_count: int = Field(default=0, description="Transaction count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VelocityProfile(BaseModel):
    """Velocity profile for fraud detection"""
    user_id: str = Field(..., description="User identifier")
    time_window: int = Field(default=24, description="Time window in hours")
    transaction_count: int = Field(default=0, description="Transaction count")
    total_amount: Decimal = Field(default=Decimal('0'), description="Total amount")
    average_amount: Decimal = Field(default=Decimal('0'), description="Average amount")
    max_amount: Decimal = Field(default=Decimal('0'), description="Maximum amount")
    min_amount: Decimal = Field(default=Decimal('0'), description="Minimum amount")
    velocity_score: Decimal = Field(default=Decimal('0'), description="Velocity risk score")
    is_anomalous: bool = Field(default=False, description="Is velocity anomalous")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TransactionData(BaseModel):
    """Transaction data for analysis"""
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    amount: Decimal = Field(..., description="Transaction amount")
    merchant: str = Field(default="", description="Merchant name")
    location: str = Field(default="", description="Transaction location")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    device_id: str = Field(default="", description="Device identifier")
    ip_address: str = Field(default="", description="IP address")
    platform: str = Field(default="api", description="Platform")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ComprehensiveRiskAnalysis(BaseModel):
    """Comprehensive risk analysis result"""
    user_id: str = Field(..., description="User identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    behavioral_score: Decimal = Field(..., description="Behavioral risk score")
    transactional_score: Decimal = Field(..., description="Transactional risk score")
    network_score: Decimal = Field(..., description="Network risk score")
    device_score: Decimal = Field(..., description="Device risk score")
    velocity_score: Decimal = Field(..., description="Velocity risk score")
    composite_score: Decimal = Field(..., description="Composite risk score")
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    recommended_action: str = Field(..., description="Recommended action")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Analysis confidence")
    platform: str = Field(default="api", description="Platform")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    processing_time_ms: float = Field(default=0.0, description="Processing time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudPattern(BaseModel):
    """Fraud pattern detection result"""
    pattern_id: str = Field(..., description="Pattern identifier")
    pattern_type: str = Field(..., description="Pattern type")
    pattern_name: str = Field(..., description="Pattern name")
    description: str = Field(..., description="Pattern description")
    risk_score: Decimal = Field(..., description="Pattern risk score")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Detection confidence")
    affected_transactions: List[str] = Field(default_factory=list, description="Affected transactions")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AdvancedAnalyticsData(BaseModel):
    """Advanced analytics data"""
    user_id: str = Field(..., description="User identifier")
    analysis_type: str = Field(..., description="Analysis type")
    data_points: List[Dict[str, Any]] = Field(default_factory=list, description="Data points")
    trends: Dict[str, Any] = Field(default_factory=dict, description="Trend analysis")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list, description="Detected anomalies")
    predictions: Dict[str, Any] = Field(default_factory=dict, description="Predictions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
