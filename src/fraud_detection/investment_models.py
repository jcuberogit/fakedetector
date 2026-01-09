#!/usr/bin/env python3
"""
Investment Fraud Detection Models
Python equivalent of C# InvestmentModels.cs
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    """Investment transaction types"""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SPLIT = "SPLIT"
    MERGER = "MERGER"


class AssetType(str, Enum):
    """Asset types for investment holdings"""
    STOCK = "STOCK"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUAL_FUND"
    BOND = "BOND"
    OPTION = "OPTION"
    FUTURES = "FUTURES"
    CRYPTO = "CRYPTO"


class RiskLevel(str, Enum):
    """Risk levels for investment assessment"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Severity(str, Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InvestmentHolding(BaseModel):
    """Investment holding model"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    quantity: int = Field(..., ge=0, description="Number of shares")
    current_price: Decimal = Field(..., ge=0, description="Current price per share")
    market_value: Decimal = Field(..., ge=0, description="Total market value")
    cost_basis: Decimal = Field(..., ge=0, description="Original cost basis")
    gain_loss: Decimal = Field(..., description="Gain or loss amount")
    gain_loss_percentage: Decimal = Field(..., description="Gain or loss percentage")
    asset_type: AssetType = Field(default=AssetType.STOCK, description="Type of asset")
    last_trade_date: datetime = Field(default_factory=datetime.utcnow, description="Last trade date")


class InvestmentPortfolio(BaseModel):
    """Investment portfolio model"""
    user_id: str = Field(..., description="User identifier")
    portfolio_id: str = Field(..., description="Portfolio identifier")
    total_value: Decimal = Field(..., ge=0, description="Total portfolio value")
    total_gain_loss: Decimal = Field(..., description="Total gain or loss")
    daily_change: Decimal = Field(..., description="Daily change amount")
    daily_change_percentage: Decimal = Field(..., description="Daily change percentage")
    holdings: List[InvestmentHolding] = Field(default_factory=list, description="Portfolio holdings")
    risk_profile: str = Field(default="MODERATE", description="Risk profile")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class InvestmentTransaction(BaseModel):
    """Investment transaction model"""
    transaction_id: str = Field(..., description="Transaction identifier")
    user_id: str = Field(..., description="User identifier")
    symbol: str = Field(..., description="Stock symbol")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    quantity: int = Field(..., ge=1, description="Number of shares")
    price: Decimal = Field(..., gt=0, description="Price per share")
    amount: Decimal = Field(..., gt=0, description="Total transaction amount")
    transaction_date: datetime = Field(default_factory=datetime.utcnow, description="Transaction date")
    platform: str = Field(default="api", description="Trading platform")
    device_id: str = Field(default="", description="Device identifier")
    description: Optional[str] = Field(None, description="Transaction description")


class InvestmentTransactionRequest(BaseModel):
    """Investment transaction request model"""
    symbol: str = Field(..., description="Stock symbol")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    quantity: int = Field(..., ge=1, description="Number of shares")
    estimated_price: Decimal = Field(..., gt=0, description="Estimated price per share")
    description: Optional[str] = Field(None, description="Transaction description")


class RiskFactor(BaseModel):
    """Risk factor model"""
    type: str = Field(..., description="Type of risk factor")
    weight: Decimal = Field(..., ge=0, le=1, description="Risk weight (0-1)")
    description: str = Field(..., description="Risk description")
    severity: Severity = Field(..., description="Risk severity")


class TradingPattern(BaseModel):
    """Trading pattern model"""
    pattern_type: str = Field(..., description="Type of pattern")
    description: str = Field(..., description="Pattern description")
    confidence: Decimal = Field(..., ge=0, le=1, description="Pattern confidence (0-1)")
    affected_symbols: List[str] = Field(default_factory=list, description="Affected symbols")
    detected_date: datetime = Field(default_factory=datetime.utcnow, description="Detection date")


class InvestmentRiskAssessment(BaseModel):
    """Investment risk assessment model"""
    user_id: str = Field(..., description="User identifier")
    overall_risk_score: Decimal = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors")
    recommendations: List[str] = Field(default_factory=list, description="Risk recommendations")
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")


class InvestmentValidationResult(BaseModel):
    """Investment validation result model"""
    is_valid: bool = Field(..., description="Whether transaction is valid")
    risk_score: Decimal = Field(..., ge=0, le=1, description="Risk score (0-1)")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    validation_message: str = Field(..., description="Validation message")
    requires_approval: bool = Field(default=False, description="Whether approval is required")


class InvestmentFraudAlert(BaseModel):
    """Investment fraud alert model"""
    alert_id: str = Field(..., description="Alert identifier")
    user_id: str = Field(..., description="User identifier")
    alert_type: str = Field(..., description="Type of alert")
    description: str = Field(..., description="Alert description")
    risk_score: Decimal = Field(..., ge=0, le=1, description="Risk score")
    severity: Severity = Field(..., description="Alert severity")
    created_date: datetime = Field(default_factory=datetime.utcnow, description="Creation date")
    is_resolved: bool = Field(default=False, description="Whether alert is resolved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MarketDataPoint(BaseModel):
    """Market data point model"""
    symbol: str = Field(..., description="Stock symbol")
    price: Decimal = Field(..., ge=0, description="Current price")
    change: Decimal = Field(..., description="Price change")
    change_percentage: Decimal = Field(..., description="Price change percentage")
    volume: int = Field(..., ge=0, description="Trading volume")
    high: Decimal = Field(..., ge=0, description="Day high")
    low: Decimal = Field(..., ge=0, description="Day low")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")


class PerformanceData(BaseModel):
    """Performance data model"""
    date: datetime = Field(..., description="Performance date")
    portfolio_value: Decimal = Field(..., ge=0, description="Portfolio value")
    daily_return: Decimal = Field(..., description="Daily return")
    cumulative_return: Decimal = Field(..., description="Cumulative return")
    volatility: Decimal = Field(..., ge=0, description="Volatility measure")


class SectorAllocation(BaseModel):
    """Sector allocation model"""
    sector: str = Field(..., description="Sector name")
    percentage: Decimal = Field(..., ge=0, le=100, description="Allocation percentage")
    value: Decimal = Field(..., ge=0, description="Sector value")
    holdings_count: int = Field(..., ge=0, description="Number of holdings")


class PortfolioAnalysis(BaseModel):
    """Portfolio analysis model"""
    user_id: str = Field(..., description="User identifier")
    diversification: Decimal = Field(..., ge=0, le=1, description="Diversification score")
    beta: Decimal = Field(..., description="Portfolio beta")
    alpha: Decimal = Field(..., description="Portfolio alpha")
    sharpe_ratio: Decimal = Field(..., description="Sharpe ratio")
    max_drawdown: Decimal = Field(..., description="Maximum drawdown")
    sector_allocations: List[SectorAllocation] = Field(default_factory=list, description="Sector allocations")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis date")


class InvestmentSummaryDto(BaseModel):
    """Investment summary DTO"""
    total_portfolio_value: Decimal = Field(..., ge=0, description="Total portfolio value")
    total_gain_loss: Decimal = Field(..., description="Total gain or loss")
    daily_change: Decimal = Field(..., description="Daily change")
    daily_change_percentage: Decimal = Field(..., description="Daily change percentage")
    total_holdings: int = Field(..., ge=0, description="Total number of holdings")
    top_performer: str = Field(default="", description="Top performing symbol")
    worst_performer: str = Field(default="", description="Worst performing symbol")


class InvestmentRecommendationDto(BaseModel):
    """Investment recommendation DTO"""
    symbol: str = Field(..., description="Stock symbol")
    recommendation_type: str = Field(..., description="Recommendation type (BUY/SELL/HOLD)")
    reasoning: str = Field(..., description="Recommendation reasoning")
    target_price: Decimal = Field(..., ge=0, description="Target price")
    confidence: Decimal = Field(..., ge=0, le=1, description="Confidence level")
    recommendation_date: datetime = Field(default_factory=datetime.utcnow, description="Recommendation date")


class MarketNews(BaseModel):
    """Market news model"""
    news_id: str = Field(..., description="News identifier")
    title: str = Field(..., description="News title")
    summary: str = Field(..., description="News summary")
    source: str = Field(..., description="News source")
    published_date: datetime = Field(..., description="Publication date")
    affected_symbols: List[str] = Field(default_factory=list, description="Affected symbols")
    sentiment: str = Field(default="NEUTRAL", description="News sentiment")
    impact_score: Decimal = Field(default=0, ge=0, le=1, description="Impact score")


class ExternalAccountLink(BaseModel):
    """External account link model"""
    account_id: str = Field(..., description="Account identifier")
    user_id: str = Field(..., description="User identifier")
    platform_id: str = Field(..., description="Platform identifier")
    external_account_id: str = Field(..., description="External account identifier")
    account_type: str = Field(..., description="Account type")
    status: str = Field(default="ACTIVE", description="Account status")
    last_sync_date: datetime = Field(default_factory=datetime.utcnow, description="Last sync date")
    access_token: Optional[str] = Field(None, description="Access token")
    token_expiry_date: Optional[datetime] = Field(None, description="Token expiry date")


class InvestmentPlatform(BaseModel):
    """Investment platform model"""
    platform_id: str = Field(..., description="Platform identifier")
    name: str = Field(..., description="Platform name")
    is_supported: bool = Field(default=True, description="Whether platform is supported")
    supported_asset_types: List[AssetType] = Field(default_factory=list, description="Supported asset types")
    api_version: Optional[str] = Field(None, description="API version")
    last_sync_date: datetime = Field(default_factory=datetime.utcnow, description="Last sync date")


class MarketVolatilityData(BaseModel):
    """Market volatility data model"""
    symbols: List[str] = Field(default_factory=list, description="Symbols analyzed")
    average_volatility: Decimal = Field(..., ge=0, description="Average volatility")
    vix_level: Decimal = Field(..., ge=0, description="VIX level")
    market_sentiment: str = Field(default="NEUTRAL", description="Market sentiment")


class MarketDataDto(BaseModel):
    """Market data DTO"""
    quotes: List[MarketDataPoint] = Field(default_factory=list, description="Market quotes")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    data_source: str = Field(default="", description="Data source")
