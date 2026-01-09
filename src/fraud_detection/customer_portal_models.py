"""
Customer Portal Models
Migrated from C# FraudDetectionAgent.Api.Models.Entities.FraudCase and customer portal components
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class CaseStatus(str, Enum):
    """Fraud case status"""
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    SUBMITTED = "Submitted"
    INVESTIGATING = "Investigating"


class CasePriority(str, Enum):
    """Fraud case priority"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    URGENT = "Urgent"


class CaseType(str, Enum):
    """Fraud case types"""
    UNAUTHORIZED_TRANSACTION = "UNAUTHORIZED_TRANSACTION"
    IDENTITY_THEFT = "IDENTITY_THEFT"
    PHISHING = "PHISHING"
    CARD_FRAUD = "CARD_FRAUD"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    OTHER = "OTHER"


class ContactPreference(str, Enum):
    """Customer contact preferences"""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SMS = "SMS"


class FraudCase(BaseModel):
    """Fraud case entity"""
    id: Optional[int] = Field(None, description="Database ID")
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique case identifier")
    case_number: str = Field(default_factory=lambda: f"CASE-{uuid.uuid4().hex[:8].upper()}", description="Human-readable case number")
    user_id: str = Field(..., description="User identifier")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst ID")
    priority: CasePriority = Field(default=CasePriority.MEDIUM, description="Case priority")
    status: CaseStatus = Field(default=CaseStatus.OPEN, description="Case status")
    category: str = Field(..., description="Case category")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    amount_involved: Optional[float] = Field(None, description="Amount involved in fraud")
    resolution: Optional[str] = Field(None, description="Case resolution details")
    transaction_id: Optional[str] = Field(None, description="Related transaction ID")
    risk_score: Optional[float] = Field(None, description="Risk score")
    requires_action: bool = Field(default=True, description="Whether case requires action")
    message: str = Field(default="", description="Case message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    notes: List['FraudCaseNote'] = Field(default_factory=list, description="Case notes")


class FraudCaseNote(BaseModel):
    """Fraud case note"""
    id: Optional[int] = Field(None, description="Database ID")
    fraud_case_id: int = Field(..., description="Associated fraud case ID")
    note: str = Field(..., description="Note content")
    created_by: str = Field(..., description="Note author")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class FraudReport(BaseModel):
    """Customer fraud report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Report ID")
    type: CaseType = Field(..., description="Fraud type")
    status: CaseStatus = Field(default=CaseStatus.SUBMITTED, description="Report status")
    description: str = Field(..., description="Report description")
    amount: Optional[float] = Field(None, description="Amount involved")
    incident_date: datetime = Field(..., description="Date of incident")
    submitted_date: datetime = Field(default_factory=datetime.utcnow, description="Submission date")
    priority: CasePriority = Field(default=CasePriority.MEDIUM, description="Report priority")
    evidence: List[str] = Field(default_factory=list, description="Evidence files")
    contact_preference: ContactPreference = Field(default=ContactPreference.EMAIL, description="Contact preference")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is required")
    user_id: str = Field(..., description="Reporting user ID")
    location: Optional[str] = Field(None, description="Incident location")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    device_type: Optional[str] = Field(None, description="Device type")


class FraudAlert(BaseModel):
    """Fraud alert for customer portal"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Alert ID")
    user_id: str = Field(..., description="User ID")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    is_read: bool = Field(default=False, description="Whether alert is read")
    is_resolved: bool = Field(default=False, description="Whether alert is resolved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SuspiciousTransaction(BaseModel):
    """Suspicious transaction for customer review"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    amount: float = Field(..., description="Transaction amount")
    merchant_name: str = Field(..., description="Merchant name")
    location: str = Field(..., description="Transaction location")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    risk_score: float = Field(..., description="Risk score")
    status: str = Field(default="PENDING", description="Review status")
    is_legitimate: Optional[bool] = Field(None, description="Customer confirmation")


class CaseResolution(BaseModel):
    """Case resolution details"""
    case_id: str = Field(..., description="Case ID")
    resolution_type: str = Field(..., description="Type of resolution")
    resolution_details: str = Field(..., description="Resolution details")
    resolved_by: str = Field(..., description="Resolved by user ID")
    resolved_at: datetime = Field(default_factory=datetime.utcnow, description="Resolution timestamp")
    customer_satisfaction: Optional[int] = Field(None, description="Customer satisfaction rating (1-5)")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is required")


class CustomerProfile(BaseModel):
    """Customer profile for portal"""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account status")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    security_settings: Dict[str, Any] = Field(default_factory=dict, description="Security settings")


class CaseStatistics(BaseModel):
    """Case statistics for dashboard"""
    total_cases: int = Field(0, description="Total number of cases")
    open_cases: int = Field(0, description="Number of open cases")
    resolved_cases: int = Field(0, description="Number of resolved cases")
    high_priority_cases: int = Field(0, description="Number of high priority cases")
    average_resolution_time_hours: float = Field(0.0, description="Average resolution time")
    customer_satisfaction_score: float = Field(0.0, description="Average satisfaction score")
    fraud_prevention_rate: float = Field(0.0, description="Fraud prevention rate")


class PortalNotification(BaseModel):
    """Portal notification"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Notification ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    type: str = Field(..., description="Notification type")
    is_read: bool = Field(default=False, description="Whether notification is read")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    action_url: Optional[str] = Field(None, description="Action URL")


class CaseSearchCriteria(BaseModel):
    """Case search criteria"""
    user_id: Optional[str] = Field(None, description="User ID filter")
    status: Optional[CaseStatus] = Field(None, description="Status filter")
    priority: Optional[CasePriority] = Field(None, description="Priority filter")
    case_type: Optional[CaseType] = Field(None, description="Case type filter")
    date_from: Optional[datetime] = Field(None, description="Date range start")
    date_to: Optional[datetime] = Field(None, description="Date range end")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst filter")
    search_text: Optional[str] = Field(None, description="Text search")


class CaseUpdateRequest(BaseModel):
    """Case update request"""
    case_id: str = Field(..., description="Case ID")
    status: Optional[CaseStatus] = Field(None, description="New status")
    priority: Optional[CasePriority] = Field(None, description="New priority")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    resolution: Optional[str] = Field(None, description="Resolution details")
    note: Optional[str] = Field(None, description="Additional note")


class CaseCreationRequest(BaseModel):
    """Case creation request"""
    user_id: str = Field(..., description="User ID")
    case_type: CaseType = Field(..., description="Case type")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    priority: CasePriority = Field(default=CasePriority.MEDIUM, description="Case priority")
    transaction_id: Optional[str] = Field(None, description="Related transaction ID")
    amount_involved: Optional[float] = Field(None, description="Amount involved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Update forward references
FraudCase.model_rebuild()
FraudCaseNote.model_rebuild()
