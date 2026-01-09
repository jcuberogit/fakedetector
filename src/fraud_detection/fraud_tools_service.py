#!/usr/bin/env python3
"""
Fraud Tools Service for Fraud Detection
Python equivalent of C# FraudTools.cs
"""

import asyncio
import logging
import uuid
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
import statistics

from .fraud_tools_models import (
    FraudRiskScore, FraudAssessment, FraudRiskAssessment, Transaction,
    VelocityAnalysis, FrequencyAnalysis, AmountPatternAnalysis,
    MerchantRiskProfile, LocationRiskProfile, TimeRiskProfile,
    FraudAlert, FraudFeedback, CounterfactualResult, GraphAnalysisResult,
    TransferRequest, PaymentRequest, CardOperationRequest,
    RiskFactor, RiskLevel, Severity, RecommendedAction, TransactionType
)

logger = logging.getLogger(__name__)


class FraudTools:
    """
    Fraud detection tools and algorithms service
    
    Python equivalent of C# FraudTools with comprehensive fraud analysis functions
    including risk assessment, pattern detection, transaction monitoring, and alert management.
    """
    
    def __init__(self):
        self.merchant_risk_cache: Dict[str, MerchantRiskProfile] = {}
        self.location_risk_cache: Dict[str, LocationRiskProfile] = {}
        self.time_risk_cache: Dict[int, TimeRiskProfile] = {}
        self.transaction_history: Dict[str, List[Transaction]] = {}
        
        # Initialize sample data
        self._initialize_sample_data()
        
        logger.info("FraudTools service initialized with risk assessment algorithms")
    
    def _initialize_sample_data(self):
        """Initialize sample merchant and location risk data"""
        
        # Sample merchant risk profiles
        merchants = [
            ("Amazon", Decimal('0.2'), "E-commerce"),
            ("Starbucks", Decimal('0.3'), "Food & Beverage"),
            ("Shell", Decimal('0.4'), "Gas Station"),
            ("Unknown Merchant", Decimal('0.8'), "Unknown"),
            ("High Risk Merchant", Decimal('0.9'), "High Risk")
        ]
        
        for name, risk_score, category in merchants:
            self.merchant_risk_cache[name] = MerchantRiskProfile(
                merchant_name=name,
                risk_score=risk_score,
                transaction_count=random.randint(100, 1000),
                fraud_reports=random.randint(0, 10),
                reputation_score=Decimal('1.0') - risk_score,
                category=category
            )
        
        # Sample location risk profiles
        locations = [
            ("San Francisco, CA", Decimal('0.3'), "US", "California"),
            ("New York, NY", Decimal('0.2'), "US", "New York"),
            ("London, UK", Decimal('0.4'), "UK", "England"),
            ("High Risk Location", Decimal('0.9'), "Unknown", "Unknown")
        ]
        
        for location, risk_score, country, region in locations:
            self.location_risk_cache[location] = LocationRiskProfile(
                location=location,
                risk_score=risk_score,
                transaction_count=random.randint(50, 500),
                fraud_reports=random.randint(0, 5),
                country=country,
                region=region
            )
        
        # Sample time risk profiles
        for hour in range(24):
            # Higher risk during late night/early morning
            if hour in [0, 1, 2, 3, 4, 5]:
                risk_score = Decimal('0.7')
            elif hour in [22, 23]:
                risk_score = Decimal('0.6')
            else:
                risk_score = Decimal('0.3')
            
            self.time_risk_cache[hour] = TimeRiskProfile(
                hour=hour,
                day_of_week=0,  # Will be updated per analysis
                risk_score=risk_score,
                is_high_risk_time=risk_score > Decimal('0.6')
            )
        
        logger.info(f"Initialized sample data: {len(self.merchant_risk_cache)} merchants, "
                   f"{len(self.location_risk_cache)} locations, {len(self.time_risk_cache)} time profiles")
    
    # Risk Assessment Functions
    
    async def calculate_transaction_risk_score(self, transaction_id: str, amount: Decimal, 
                                             merchant_name: str, location: str) -> FraudRiskScore:
        """Calculate comprehensive risk score for a transaction"""
        try:
            logger.info(f"Calculating risk score for transaction {transaction_id}")
            
            risk_factors = []
            total_risk_score = Decimal('0')
            
            # Amount-based risk assessment
            amount_risk = self._calculate_amount_risk(amount)
            if amount_risk.weight > 0:
                risk_factors.append(amount_risk)
                total_risk_score += amount_risk.weight
            
            # Merchant risk assessment
            try:
                merchant_risk = await self._calculate_merchant_risk(merchant_name)
                if merchant_risk.weight > 0:
                    risk_factors.append(merchant_risk)
                    total_risk_score += merchant_risk.weight
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Failed to calculate merchant risk for {merchant_name}: {e}")
                # Continue with default merchant risk
                default_merchant_risk = RiskFactor(
                    type="MERCHANT_RISK",
                    weight=Decimal('0.4'),
                    description="Merchant risk score: 0.40"
                )
                risk_factors.append(default_merchant_risk)
                total_risk_score += default_merchant_risk.weight
            
            # Location risk assessment
            location_risk = self._calculate_location_risk(location)
            if location_risk.weight > 0:
                risk_factors.append(location_risk)
                total_risk_score += location_risk.weight
            
            # Time-based risk assessment
            time_risk = await self._calculate_time_risk(datetime.utcnow())
            risk_factors.append(time_risk)
            total_risk_score += time_risk.weight
            
            # Normalize risk score by taking the highest risk factor
            normalized_score = max([rf.weight for rf in risk_factors]) if risk_factors else Decimal('0')
            
            risk_level = self._determine_risk_level(normalized_score)
            recommended_action = self._get_recommended_action(normalized_score)
            
            return FraudRiskScore(
                transaction_id=transaction_id,
                risk_score=normalized_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence=Decimal('0.85'),
                timestamp=datetime.utcnow(),
                analysis_methods=["AMOUNT_ANALYSIS", "MERCHANT_ANALYSIS", "LOCATION_ANALYSIS", "TIME_ANALYSIS"]
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error calculating transaction risk score: {e}")
            raise
    
    async def analyze_transaction_pattern(self, account_id: str, transaction_id: str) -> FraudAssessment:
        """Analyze transaction patterns for a specific account and transaction"""
        try:
            logger.info(f"Analyzing transaction pattern for account {account_id}")
            
            # Generate sample transaction data for analysis
            recent_transactions = await self._get_recent_transactions(account_id)
            
            risk_factors = []
            
            # Velocity analysis
            velocity_risk = self._analyze_velocity_pattern(recent_transactions)
            risk_factors.extend(velocity_risk)
            
            # Frequency analysis
            frequency_risk = self._analyze_frequency_pattern(recent_transactions)
            risk_factors.extend(frequency_risk)
            
            # Amount pattern analysis
            amount_risk = self._analyze_amount_pattern(recent_transactions)
            risk_factors.extend(amount_risk)
            
            average_risk = statistics.mean([rf.weight for rf in risk_factors]) if risk_factors else Decimal('0')
            risk_level = self._determine_risk_level(average_risk)
            recommended_action = self._get_recommended_action(average_risk)
            
            return FraudAssessment(
                transaction_id=transaction_id,
                account_id=account_id,
                risk_score=average_risk,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence=Decimal('0.80'),
                timestamp=datetime.utcnow(),
                analysis_methods=["VELOCITY_ANALYSIS", "FREQUENCY_ANALYSIS", "AMOUNT_PATTERN"],
                pattern_analysis={
                    "velocity_analysis": self._get_velocity_analysis(recent_transactions).dict(),
                    "frequency_analysis": self._get_frequency_analysis(recent_transactions).dict(),
                    "amount_analysis": self._get_amount_analysis(recent_transactions).dict()
                }
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error analyzing transaction pattern for account {account_id}: {e}")
            raise
    
    async def detect_velocity_anomalies(self, user_id: str, amount: Decimal, 
                                       transaction_time: datetime) -> List[RiskFactor]:
        """Detect velocity-based fraud anomalies"""
        try:
            logger.info(f"Detecting velocity anomalies for user {user_id}")
            
            # Get recent transactions for velocity analysis
            recent_transactions = await self._get_user_recent_transactions(user_id, hours=24)
            
            risk_factors = []
            
            # Check transaction count velocity
            transaction_count = len([t for t in recent_transactions 
                                  if t.timestamp >= transaction_time - timedelta(hours=1)])
            
            if transaction_count > 10:  # More than 10 transactions in 1 hour
                risk_factors.append(RiskFactor(
                    type="HIGH_TRANSACTION_VELOCITY",
                    weight=Decimal('0.8'),
                    description=f"High transaction velocity: {transaction_count} transactions in 1 hour",
                    severity=Severity.HIGH
                ))
            
            # Check amount velocity
            total_amount = sum(t.amount for t in recent_transactions 
                             if t.timestamp >= transaction_time - timedelta(hours=24))
            
            if total_amount > Decimal('10000'):  # More than $10,000 in 24 hours
                risk_factors.append(RiskFactor(
                    type="HIGH_AMOUNT_VELOCITY",
                    weight=Decimal('0.7'),
                    description=f"High amount velocity: ${total_amount} in 24 hours",
                    severity=Severity.HIGH
                ))
            
            # Check rapid successive transactions
            rapid_transactions = self._detect_rapid_transactions(recent_transactions)
            if rapid_transactions:
                risk_factors.append(RiskFactor(
                    type="RAPID_SUCCESSIVE_TRANSACTIONS",
                    weight=Decimal('0.6'),
                    description=f"Rapid successive transactions detected: {len(rapid_transactions)} transactions",
                    severity=Severity.MEDIUM
                ))
            
            return risk_factors
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error detecting velocity anomalies for user {user_id}: {e}")
            raise
    
    async def analyze_transaction_history_risk(self, account_id: str, user_id: str) -> FraudRiskAssessment:
        """Analyze transaction history risk"""
        try:
            logger.info(f"Analyzing transaction history risk for account {account_id}, user {user_id}")
            
            risk_factors = []
            
            # Analyze spending patterns
            spending_pattern_risk = await self._calculate_spending_pattern_risk(account_id)
            risk_factors.append(RiskFactor(
                type="spending_pattern",
                weight=spending_pattern_risk,
                description="Historical spending pattern analysis"
            ))
            
            # Check for velocity anomalies
            velocity_risk = await self._calculate_velocity_risk(account_id)
            risk_factors.append(RiskFactor(
                type="transaction_velocity",
                weight=velocity_risk,
                description="Transaction velocity and frequency analysis"
            ))
            
            # Analyze merchant patterns
            merchant_risk = await self._calculate_merchant_pattern_risk(account_id)
            risk_factors.append(RiskFactor(
                type="merchant_pattern",
                weight=merchant_risk,
                description="Merchant interaction pattern analysis"
            ))
            
            total_risk = sum(rf.weight for rf in risk_factors) / len(risk_factors) if risk_factors else Decimal('0')
            risk_level = self._determine_risk_level(total_risk)
            recommended_action = self._get_recommended_action(total_risk)
            
            return FraudRiskAssessment(
                risk_score=total_risk,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence=Decimal('0.80'),
                timestamp=datetime.utcnow(),
                analysis_methods=["SPENDING_PATTERN", "VELOCITY_ANALYSIS", "MERCHANT_PATTERN"]
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error analyzing transaction history risk for account {account_id}: {e}")
            raise
    
    async def analyze_card_operation_risk(self, card_id: str, action: str, user_id: str) -> FraudRiskAssessment:
        """Analyze card operation risk"""
        try:
            logger.info(f"Analyzing card operation risk for card {card_id}, action {action}, user {user_id}")
            
            risk_factors = []
            
            # Analyze card usage patterns
            usage_pattern_risk = await self._calculate_card_usage_pattern_risk(card_id, action)
            risk_factors.append(RiskFactor(
                type="card_usage_pattern",
                weight=usage_pattern_risk,
                description="Card usage pattern and history analysis"
            ))
            
            # Check location consistency
            location_risk = await self._calculate_card_location_risk(card_id)
            risk_factors.append(RiskFactor(
                type="location_consistency",
                weight=location_risk,
                description="Card usage location consistency analysis"
            ))
            
            # Analyze operation type risk
            operation_risk = await self._calculate_card_operation_type_risk(action)
            risk_factors.append(RiskFactor(
                type="operation_type",
                weight=operation_risk,
                description=f"Risk assessment for {action} operation"
            ))
            
            total_risk = sum(rf.weight for rf in risk_factors) / len(risk_factors) if risk_factors else Decimal('0')
            risk_level = self._determine_risk_level(total_risk)
            recommended_action = self._get_recommended_action(total_risk)
            
            return FraudRiskAssessment(
                risk_score=total_risk,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=recommended_action,
                confidence=Decimal('0.85'),
                timestamp=datetime.utcnow(),
                analysis_methods=["CARD_USAGE_PATTERN", "LOCATION_CONSISTENCY", "OPERATION_TYPE"]
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error analyzing card operation risk for card {card_id}: {e}")
            raise
    
    async def detect_fraud_ring(self, transaction_id: str) -> GraphAnalysisResult:
        """Detect potential fraud rings using graph analysis"""
        try:
            logger.info(f"Detecting fraud ring for transaction {transaction_id}")
            
            # Simulate fraud ring detection
            fraud_rings = []
            suspicious_nodes = []
            
            # Generate sample fraud ring detection
            if random.random() < 0.3:  # 30% chance of detecting a fraud ring
                fraud_rings.append({
                    "ring_id": f"ring_{uuid.uuid4().hex[:8]}",
                    "node_count": random.randint(3, 8),
                    "risk_score": Decimal(str(random.uniform(0.6, 0.9))),
                    "detection_method": "graph_analysis"
                })
                
                suspicious_nodes = [f"node_{i}" for i in range(random.randint(2, 5))]
            
            risk_score = max([ring["risk_score"] for ring in fraud_rings]) if fraud_rings else Decimal('0')
            
            return GraphAnalysisResult(
                transaction_id=transaction_id,
                fraud_rings=fraud_rings,
                suspicious_nodes=suspicious_nodes,
                risk_score=risk_score,
                confidence=Decimal('0.75'),
                analysis_methods=["GRAPH_ANALYSIS", "NODE_CENTRALITY", "COMMUNITY_DETECTION"],
                timestamp=datetime.utcnow()
            )
            
        except (ValueError) as e:
            logger.error(f"Error detecting fraud ring for transaction {transaction_id}: {e}")
            raise
    
    async def record_feedback(self, feedback: FraudFeedback) -> bool:
        """Record fraud detection feedback"""
        try:
            logger.info(f"Recording feedback for transaction {feedback.transaction_id}")
            
            # In a real implementation, this would store feedback in a database
            # and use it to improve fraud detection models
            
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error recording feedback: {e}")
            return False
    
    async def compute_counterfactual(self, transaction: Transaction, account_id: str) -> CounterfactualResult:
        """Compute counterfactual analysis for a transaction"""
        try:
            logger.info(f"Computing counterfactual for transaction {transaction.id}")
            
            # Simulate counterfactual analysis
            original_decision = "BLOCK" if random.random() < 0.5 else "ALLOW"
            target_decision = "ALLOW" if original_decision == "BLOCK" else "BLOCK"
            
            parameter_changes = {
                "amount_reduction": Decimal(str(random.uniform(0.1, 0.5))),
                "merchant_change": "Lower risk merchant",
                "time_change": "Business hours"
            }
            
            margin_to_safe = Decimal(str(random.uniform(0.1, 0.3)))
            most_effective_change = "Reduce transaction amount by 30%"
            
            return CounterfactualResult(
                transaction_id=transaction.id,
                original_decision=original_decision,
                target_decision=target_decision,
                parameter_changes=parameter_changes,
                margin_to_safe=margin_to_safe,
                most_effective_change=most_effective_change,
                confidence=Decimal('0.80'),
                timestamp=datetime.utcnow()
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error computing counterfactual: {e}")
            raise
    
    # Private helper methods
    
    def _calculate_amount_risk(self, amount: Decimal) -> RiskFactor:
        """Calculate amount-based risk"""
        if amount > Decimal('5000'):
            return RiskFactor(
                type="HIGH_AMOUNT",
                weight=Decimal('0.8'),
                description=f"High transaction amount: ${amount}",
                severity=Severity.HIGH
            )
        elif amount > Decimal('1000'):
            return RiskFactor(
                type="MEDIUM_AMOUNT",
                weight=Decimal('0.4'),
                description=f"Medium transaction amount: ${amount}",
                severity=Severity.MEDIUM
            )
        else:
            return RiskFactor(
                type="LOW_AMOUNT",
                weight=Decimal('0.1'),
                description=f"Low transaction amount: ${amount}",
                severity=Severity.LOW
            )
    
    async def _calculate_merchant_risk(self, merchant_name: str) -> RiskFactor:
        """Calculate merchant-based risk"""
        merchant_profile = self.merchant_risk_cache.get(merchant_name)
        
        if merchant_profile:
            return RiskFactor(
                type="MERCHANT_RISK",
                weight=merchant_profile.risk_score,
                description=f"Merchant risk score: {merchant_profile.risk_score}",
                severity=Severity.HIGH if merchant_profile.risk_score > Decimal('0.7') else Severity.MEDIUM
            )
        else:
            # Unknown merchant - higher risk
            return RiskFactor(
                type="UNKNOWN_MERCHANT",
                weight=Decimal('0.6'),
                description="Unknown merchant - higher risk",
                severity=Severity.MEDIUM
            )
    
    def _calculate_location_risk(self, location: str) -> RiskFactor:
        """Calculate location-based risk"""
        location_profile = self.location_risk_cache.get(location)
        
        if location_profile:
            return RiskFactor(
                type="LOCATION_RISK",
                weight=location_profile.risk_score,
                description=f"Location risk score: {location_profile.risk_score}",
                severity=Severity.HIGH if location_profile.risk_score > Decimal('0.7') else Severity.MEDIUM
            )
        else:
            # Unknown location - medium risk
            return RiskFactor(
                type="UNKNOWN_LOCATION",
                weight=Decimal('0.5'),
                description="Unknown location - medium risk",
                severity=Severity.MEDIUM
            )
    
    async def _calculate_time_risk(self, transaction_time: datetime) -> RiskFactor:
        """Calculate time-based risk"""
        hour = transaction_time.hour
        time_profile = self.time_risk_cache.get(hour)
        
        if time_profile:
            return RiskFactor(
                type="TIME_RISK",
                weight=time_profile.risk_score,
                description=f"Time risk score: {time_profile.risk_score}",
                severity=Severity.HIGH if time_profile.is_high_risk_time else Severity.MEDIUM
            )
        else:
            return RiskFactor(
                type="TIME_RISK",
                weight=Decimal('0.3'),
                description="Standard time risk",
                severity=Severity.LOW
            )
    
    def _determine_risk_level(self, risk_score: Decimal) -> RiskLevel:
        """Determine risk level from score"""
        if risk_score >= Decimal('0.8'):
            return RiskLevel.CRITICAL
        elif risk_score >= Decimal('0.6'):
            return RiskLevel.HIGH
        elif risk_score >= Decimal('0.3'):
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_recommended_action(self, risk_score: Decimal) -> RecommendedAction:
        """Get recommended action based on risk score"""
        if risk_score >= Decimal('0.8'):
            return RecommendedAction.BLOCK
        elif risk_score >= Decimal('0.6'):
            return RecommendedAction.REVIEW
        elif risk_score >= Decimal('0.3'):
            return RecommendedAction.MONITOR
        else:
            return RecommendedAction.ALLOW
    
    async def _get_recent_transactions(self, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get recent transactions for an account"""
        # Generate sample transactions
        transactions = []
        base_time = datetime.utcnow()
        
        for i in range(min(limit, 20)):  # Generate up to 20 sample transactions
            transaction = Transaction(
                id=f"txn_{i}",
                account_id=account_id,
                user_id=f"user_{account_id}",
                amount=Decimal(str(random.uniform(10, 1000))),
                merchant_name=random.choice(list(self.merchant_risk_cache.keys())),
                location=random.choice(list(self.location_risk_cache.keys())),
                transaction_type=random.choice(list(TransactionType)),
                timestamp=base_time - timedelta(hours=i),
                device_id=f"device_{random.randint(1, 5)}",
                ip_address=f"192.168.1.{random.randint(1, 255)}"
            )
            transactions.append(transaction)
        
        return transactions
    
    async def _get_user_recent_transactions(self, user_id: str, hours: int = 24) -> List[Transaction]:
        """Get recent transactions for a user"""
        # Generate sample transactions for velocity analysis
        transactions = []
        base_time = datetime.utcnow()
        
        for i in range(random.randint(5, 15)):  # Random number of recent transactions
            transaction = Transaction(
                id=f"txn_{i}",
                account_id=f"account_{user_id}",
                user_id=user_id,
                amount=Decimal(str(random.uniform(10, 500))),
                merchant_name=random.choice(list(self.merchant_risk_cache.keys())),
                location=random.choice(list(self.location_risk_cache.keys())),
                transaction_type=random.choice(list(TransactionType)),
                timestamp=base_time - timedelta(minutes=random.randint(1, hours * 60)),
                device_id=f"device_{random.randint(1, 3)}",
                ip_address=f"192.168.1.{random.randint(1, 255)}"
            )
            transactions.append(transaction)
        
        return transactions
    
    def _analyze_velocity_pattern(self, transactions: List[Transaction]) -> List[RiskFactor]:
        """Analyze velocity patterns in transactions"""
        risk_factors = []
        
        if len(transactions) > 10:  # High transaction count
            risk_factors.append(RiskFactor(
                type="HIGH_VELOCITY",
                weight=Decimal('0.6'),
                description=f"High transaction velocity: {len(transactions)} transactions",
                severity=Severity.MEDIUM
            ))
        
        return risk_factors
    
    def _analyze_frequency_pattern(self, transactions: List[Transaction]) -> List[RiskFactor]:
        """Analyze frequency patterns in transactions"""
        risk_factors = []
        
        # Calculate frequency (transactions per hour)
        if transactions:
            time_span = (max(t.timestamp for t in transactions) - 
                        min(t.timestamp for t in transactions)).total_seconds() / 3600
            frequency = len(transactions) / max(time_span, 1)
            
            if frequency > 5:  # More than 5 transactions per hour
                risk_factors.append(RiskFactor(
                    type="HIGH_FREQUENCY",
                    weight=Decimal('0.5'),
                    description=f"High transaction frequency: {frequency:.2f} per hour",
                    severity=Severity.MEDIUM
                ))
        
        return risk_factors
    
    def _analyze_amount_pattern(self, transactions: List[Transaction]) -> List[RiskFactor]:
        """Analyze amount patterns in transactions"""
        risk_factors = []
        
        if transactions:
            amounts = [t.amount for t in transactions]
            avg_amount = statistics.mean(amounts)
            max_amount = max(amounts)
            
            if max_amount > avg_amount * Decimal('3'):  # Amount significantly higher than average
                risk_factors.append(RiskFactor(
                    type="UNUSUAL_AMOUNT",
                    weight=Decimal('0.4'),
                    description=f"Unusual amount pattern: max ${max_amount} vs avg ${avg_amount:.2f}",
                    severity=Severity.MEDIUM
                ))
        
        return risk_factors
    
    def _get_velocity_analysis(self, transactions: List[Transaction]) -> VelocityAnalysis:
        """Get velocity analysis results"""
        transaction_count = len(transactions)
        total_amount = sum(t.amount for t in transactions) if transactions else Decimal('0')
        
        return VelocityAnalysis(
            transaction_count=transaction_count,
            total_amount=total_amount,
            time_window_hours=24,
            velocity_score=Decimal(str(min(transaction_count / 10, 1.0))),
            is_anomalous=transaction_count > 10
        )
    
    def _get_frequency_analysis(self, transactions: List[Transaction]) -> FrequencyAnalysis:
        """Get frequency analysis results"""
        if not transactions:
            return FrequencyAnalysis()
        
        time_span = (max(t.timestamp for t in transactions) - 
                    min(t.timestamp for t in transactions)).total_seconds() / 3600
        frequency = len(transactions) / max(time_span, 1)
        
        return FrequencyAnalysis(
            transaction_frequency=Decimal(str(frequency)),
            frequency_score=Decimal(str(min(frequency / 5, 1.0))),
            is_anomalous=frequency > 5
        )
    
    def _get_amount_analysis(self, transactions: List[Transaction]) -> AmountPatternAnalysis:
        """Get amount pattern analysis results"""
        if not transactions:
            return AmountPatternAnalysis()
        
        amounts = [t.amount for t in transactions]
        avg_amount = statistics.mean(amounts)
        variance = statistics.variance([float(a) for a in amounts]) if len(amounts) > 1 else 0
        
        return AmountPatternAnalysis(
            average_amount=Decimal(str(avg_amount)),
            amount_variance=Decimal(str(variance)),
            unusual_amount_score=Decimal(str(min(variance / 10000, 1.0))),
            is_anomalous=variance > 10000
        )
    
    def _detect_rapid_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Detect rapid successive transactions"""
        rapid_transactions = []
        
        if len(transactions) < 2:
            return rapid_transactions
        
        # Sort by timestamp
        sorted_transactions = sorted(transactions, key=lambda t: t.timestamp)
        
        for i in range(1, len(sorted_transactions)):
            time_diff = (sorted_transactions[i].timestamp - 
                        sorted_transactions[i-1].timestamp).total_seconds()
            
            if time_diff < 60:  # Less than 1 minute between transactions
                rapid_transactions.append(sorted_transactions[i])
        
        return rapid_transactions
    
    async def _calculate_spending_pattern_risk(self, account_id: str) -> Decimal:
        """Calculate spending pattern risk"""
        # Simulate spending pattern analysis
        return Decimal(str(random.uniform(0.2, 0.8)))
    
    async def _calculate_velocity_risk(self, account_id: str) -> Decimal:
        """Calculate velocity risk"""
        # Simulate velocity risk analysis
        return Decimal(str(random.uniform(0.1, 0.7)))
    
    async def _calculate_merchant_pattern_risk(self, account_id: str) -> Decimal:
        """Calculate merchant pattern risk"""
        # Simulate merchant pattern analysis
        return Decimal(str(random.uniform(0.2, 0.6)))
    
    async def _calculate_card_usage_pattern_risk(self, card_id: str, action: str) -> Decimal:
        """Calculate card usage pattern risk"""
        # Simulate card usage pattern analysis
        return Decimal(str(random.uniform(0.1, 0.5)))
    
    async def _calculate_card_location_risk(self, card_id: str) -> Decimal:
        """Calculate card location risk"""
        # Simulate card location risk analysis
        return Decimal(str(random.uniform(0.2, 0.6)))
    
    async def _calculate_card_operation_type_risk(self, action: str) -> Decimal:
        """Calculate card operation type risk"""
        # Simulate operation type risk analysis
        if action.lower() in ['lock', 'unlock']:
            return Decimal(str(random.uniform(0.1, 0.3)))
        else:
            return Decimal(str(random.uniform(0.3, 0.7)))
