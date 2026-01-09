#!/usr/bin/env python3
"""
Fraud Tools Models for Fraud Detection
Python equivalent of C# FraudTools data structures
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class RiskLevel(str, Enum):
    """Risk levels for fraud assessment"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Severity(str, Enum):
    """Severity levels for fraud alerts"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RecommendedAction(str, Enum):
    """Recommended actions for fraud detection"""
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    CHALLENGE = "CHALLENGE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class TransactionType(str, Enum):
    """Types of transactions"""
    PURCHASE = "Purchase"
    TRANSFER = "Transfer"
    WITHDRAWAL = "Withdrawal"
    DEPOSIT = "Deposit"
    PAYMENT = "Payment"
    REFUND = "Refund"
    OTHER = "Other"


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
    risk_score: Decimal = Field(..., description="Overall risk score (0.0 to 1.0)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Contributing risk factors")
    recommended_action: RecommendedAction = Field(..., description="Recommended action")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudAssessment(BaseModel):
    """Comprehensive fraud assessment with pattern analysis"""
    transaction_id: str = Field(..., description="Transaction identifier")
    account_id: str = Field(..., description="Account identifier")
    risk_score: Decimal = Field(..., description="Overall risk score")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    recommended_action: RecommendedAction = Field(..., description="Recommended action")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    pattern_analysis: Dict[str, Any] = Field(default_factory=dict, description="Pattern analysis results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudRiskAssessment(BaseModel):
    """General fraud risk assessment"""
    risk_score: Decimal = Field(..., description="Risk score (0.0 to 1.0)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    recommended_action: RecommendedAction = Field(..., description="Recommended action")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Assessment timestamp")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Transaction(BaseModel):
    """Transaction data structure"""
    id: str = Field(..., description="Transaction identifier")
    account_id: str = Field(..., description="Account identifier")
    user_id: str = Field(..., description="User identifier")
    amount: Decimal = Field(..., description="Transaction amount")
    merchant_name: str = Field(default="", description="Merchant name")
    location: str = Field(default="", description="Transaction location")
    transaction_type: TransactionType = Field(default=TransactionType.OTHER, description="Transaction type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    device_id: str = Field(default="", description="Device identifier")
    ip_address: str = Field(default="", description="IP address")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VelocityAnalysis(BaseModel):
    """Velocity analysis results"""
    transaction_count: int = Field(default=0, description="Transaction count in time window")
    total_amount: Decimal = Field(default=Decimal('0'), description="Total amount in time window")
    time_window_hours: int = Field(default=24, description="Time window in hours")
    velocity_score: Decimal = Field(default=Decimal('0'), description="Velocity risk score")
    is_anomalous: bool = Field(default=False, description="Is velocity anomalous")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FrequencyAnalysis(BaseModel):
    """Frequency analysis results"""
    transaction_frequency: Decimal = Field(default=Decimal('0'), description="Transactions per hour")
    frequency_score: Decimal = Field(default=Decimal('0'), description="Frequency risk score")
    is_anomalous: bool = Field(default=False, description="Is frequency anomalous")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AmountPatternAnalysis(BaseModel):
    """Amount pattern analysis results"""
    average_amount: Decimal = Field(default=Decimal('0'), description="Average transaction amount")
    amount_variance: Decimal = Field(default=Decimal('0'), description="Amount variance")
    unusual_amount_score: Decimal = Field(default=Decimal('0'), description="Unusual amount risk score")
    is_anomalous: bool = Field(default=False, description="Is amount pattern anomalous")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MerchantRiskProfile(BaseModel):
    """Merchant risk profile"""
    merchant_name: str = Field(..., description="Merchant name")
    risk_score: Decimal = Field(default=Decimal('0.5'), description="Merchant risk score")
    transaction_count: int = Field(default=0, description="Transaction count")
    fraud_reports: int = Field(default=0, description="Fraud reports")
    reputation_score: Decimal = Field(default=Decimal('0.5'), description="Reputation score")
    category: str = Field(default="", description="Merchant category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LocationRiskProfile(BaseModel):
    """Location risk profile"""
    location: str = Field(..., description="Location identifier")
    risk_score: Decimal = Field(default=Decimal('0.5'), description="Location risk score")
    transaction_count: int = Field(default=0, description="Transaction count")
    fraud_reports: int = Field(default=0, description="Fraud reports")
    country: str = Field(default="", description="Country")
    region: str = Field(default="", description="Region")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TimeRiskProfile(BaseModel):
    """Time-based risk profile"""
    hour: int = Field(..., description="Hour of day (0-23)")
    day_of_week: int = Field(..., description="Day of week (0-6)")
    risk_score: Decimal = Field(default=Decimal('0.5'), description="Time risk score")
    is_high_risk_time: bool = Field(default=False, description="Is high risk time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudAlert(BaseModel):
    """Fraud alert data structure"""
    id: str = Field(..., description="Alert identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    alert_type: str = Field(..., description="Alert type")
    severity: Severity = Field(..., description="Alert severity")
    risk_score: Decimal = Field(..., description="Risk score")
    description: str = Field(..., description="Alert description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation time")
    status: str = Field(default="Active", description="Alert status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudFeedback(BaseModel):
    """Fraud detection feedback"""
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    feedback_type: str = Field(..., description="Feedback type (true_positive, false_positive, etc.)")
    is_fraud: bool = Field(..., description="Was actually fraud")
    confidence: Decimal = Field(default=Decimal('1.0'), description="Feedback confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feedback timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CounterfactualResult(BaseModel):
    """Counterfactual analysis result"""
    transaction_id: str = Field(..., description="Transaction identifier")
    original_decision: str = Field(..., description="Original decision")
    target_decision: str = Field(..., description="Target decision")
    parameter_changes: Dict[str, Any] = Field(default_factory=dict, description="Parameter changes needed")
    margin_to_safe: Decimal = Field(default=Decimal('0'), description="Margin to safe decision")
    most_effective_change: str = Field(default="", description="Most effective parameter change")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphAnalysisResult(BaseModel):
    """Graph analysis result for fraud ring detection"""
    transaction_id: str = Field(..., description="Transaction identifier")
    fraud_rings: List[Dict[str, Any]] = Field(default_factory=list, description="Detected fraud rings")
    suspicious_nodes: List[str] = Field(default_factory=list, description="Suspicious nodes")
    risk_score: Decimal = Field(default=Decimal('0'), description="Graph risk score")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Detection confidence")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TransferRequest(BaseModel):
    """Transfer request data"""
    from_account: str = Field(..., description="Source account")
    to_account: str = Field(..., description="Destination account")
    amount: Decimal = Field(..., description="Transfer amount")
    currency: str = Field(default="USD", description="Currency")
    description: str = Field(default="", description="Transfer description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PaymentRequest(BaseModel):
    """Payment request data"""
    payee: str = Field(..., description="Payee identifier")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Currency")
    payment_method: str = Field(default="", description="Payment method")
    description: str = Field(default="", description="Payment description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CardOperationRequest(BaseModel):
    """Card operation request data"""
    card_id: str = Field(..., description="Card identifier")
    operation: str = Field(..., description="Operation type (lock/unlock)")
    reason: str = Field(default="", description="Operation reason")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
