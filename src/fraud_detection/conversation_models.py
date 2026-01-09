#!/usr/bin/env python3
"""
AI Conversation Models for Fraud Detection
Python equivalent of C# FraudConversationService data structures
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
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


class RecommendedAction(str, Enum):
    """Recommended actions"""
    APPROVE = "APPROVE"
    VERIFY_IDENTITY = "VERIFY_IDENTITY"
    BLOCK_TRANSACTION = "BLOCK_TRANSACTION"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    MONITOR = "MONITOR"
    CHALLENGE = "CHALLENGE"


class ChatOption(BaseModel):
    """Chat option for user interaction"""
    id: str = Field(..., description="Option identifier")
    text: str = Field(..., description="Option text")
    action: str = Field(..., description="Action to perform")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VerificationQuestion(BaseModel):
    """Verification question for identity verification"""
    id: str = Field(..., description="Question identifier")
    question: str = Field(..., description="Question text")
    question_type: str = Field(..., description="Question type")
    options: List[str] = Field(default_factory=list, description="Answer options")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TokenUsageStats(BaseModel):
    """Token usage statistics"""
    total_tokens: int = Field(default=0, description="Total tokens used")
    prompt_tokens: int = Field(default=0, description="Prompt tokens")
    completion_tokens: int = Field(default=0, description="Completion tokens")
    cost_usd: Decimal = Field(default=Decimal('0'), description="Cost in USD")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Usage timestamp")


class FraudChatRequest(BaseModel):
    """Chat request to the fraud detection AI agent"""
    message: str = Field(..., description="User's message or query")
    platform: str = Field(default="api", description="Platform (mobile, web, api)")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class FraudChatResponse(BaseModel):
    """Response from the fraud detection AI agent"""
    message: str = Field(default="", description="AI agent's response message")
    fraud_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Fraud alerts")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Alias for fraud_alerts")
    risk_score: Optional[Dict[str, Any]] = Field(default=None, description="Risk score assessment")
    options: List[ChatOption] = Field(default_factory=list, description="Follow-up options")
    verification_questions: List[VerificationQuestion] = Field(default_factory=list, description="Verification questions")
    recommended_action: str = Field(default="", description="Recommended action")
    risk_level: str = Field(default="", description="Risk level")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    token_usage: Optional[TokenUsageStats] = Field(default=None, description="Token usage statistics")
    response: str = Field(default="", description="Alias for message")


class UserContext(BaseModel):
    """User context for fraud detection"""
    user_id: str = Field(..., description="User identifier")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    location: Optional[str] = Field(default=None, description="User location")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationContext(BaseModel):
    """Conversation context for maintaining state"""
    conversation_id: str = Field(..., description="Conversation identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationMessage(BaseModel):
    """Individual conversation message"""
    id: str = Field(..., description="Message identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="Message content")
    message_type: str = Field(default="user", description="Message type (user, assistant)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FraudAnalysisRequest(BaseModel):
    """Request for analyzing a specific transaction"""
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    amount: Decimal = Field(..., description="Transaction amount")
    merchant: Optional[str] = Field(default=None, description="Merchant name")
    location: Optional[str] = Field(default=None, description="Transaction location")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class FraudAnalysisResult(BaseModel):
    """Result of fraud analysis"""
    transaction_id: str = Field(..., description="Transaction identifier")
    risk_score: Decimal = Field(..., description="Risk score (0-100)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Risk factors")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Generated alerts")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Analysis confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class IntelligentFraudResponse(BaseModel):
    """Intelligent fraud response with enhanced analysis"""
    message: str = Field(..., description="Response message")
    tokens_used: int = Field(default=0, description="Tokens used")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Fraud alerts")
    risk_score: Optional[Dict[str, Any]] = Field(default=None, description="Risk score")
    analysis_methods: List[str] = Field(default_factory=list, description="Analysis methods used")
    confidence: Decimal = Field(default=Decimal('0.8'), description="Response confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AISettings(BaseModel):
    """AI service settings"""
    ai_provider: str = Field(default="OpenAI", description="AI provider")
    temperature: float = Field(default=0.7, description="Temperature setting")
    max_tokens: int = Field(default=1000, description="Maximum tokens")
    top_p: float = Field(default=0.9, description="Top-p setting")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(default=2, description="Retry delay in seconds")
    conversation_timeout_minutes: int = Field(default=30, description="Conversation timeout")
    enable_function_calling: bool = Field(default=True, description="Enable function calling")
    max_context_messages: int = Field(default=20, description="Maximum context messages")
    max_conversation_history: int = Field(default=50, description="Maximum conversation history")


class ChatRequestDto(BaseModel):
    """Universal chat request DTO"""
    message: str = Field(..., description="User's message")
    platform: Optional[str] = Field(default="api", description="Platform")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    conversation_id: Optional[str] = Field(default=None, description="Conversation identifier")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class ChatResponseDto(BaseModel):
    """Universal chat response DTO"""
    message: str = Field(..., description="AI agent's response")
    platform: str = Field(default="api", description="Platform")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    conversation_id: Optional[str] = Field(default=None, description="Conversation identifier")
    risk_level: Optional[str] = Field(default=None, description="Risk level")
    recommended_action: Optional[str] = Field(default=None, description="Recommended action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
