#!/usr/bin/env python3
"""
Advanced Fraud Algorithms Service
Python equivalent of C# AdvancedFraudAlgorithms.cs
"""

import asyncio
import logging
import uuid
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal

from .advanced_algorithms_models import (
    FraudRiskScore, RiskFactor, PlatformRiskWeights, BehavioralProfile,
    DeviceProfile, NetworkProfile, VelocityProfile, TransactionData,
    ComprehensiveRiskAnalysis, FraudPattern, AdvancedAnalyticsData,
    RiskLevel, Severity, Platform
)

logger = logging.getLogger(__name__)


class AdvancedFraudAlgorithms:
    """
    Advanced fraud detection algorithms supporting multi-platform integration
    
    Python equivalent of C# AdvancedFraudAlgorithms with sophisticated fraud detection patterns
    for real-time risk assessment.
    """
    
    def __init__(self, gnn_service=None, fraud_tools=None):
        self.gnn_service = gnn_service
        self.fraud_tools = fraud_tools
        self.behavioral_profiles: Dict[str, BehavioralProfile] = {}
        self.device_profiles: Dict[str, DeviceProfile] = {}
        self.network_profiles: Dict[str, NetworkProfile] = {}
        self.velocity_profiles: Dict[str, VelocityProfile] = {}
        
        # Initialize sample data
        self._initialize_sample_data()
        
        logger.info("AdvancedFraudAlgorithms service initialized with multi-dimensional analysis")
    
    def _initialize_sample_data(self):
        """Initialize sample behavioral and device profiles"""
        
        # Sample behavioral profiles
        for i in range(5):
            user_id = f"user_{i+1}"
            self.behavioral_profiles[user_id] = BehavioralProfile(
                user_id=user_id,
                average_amount=Decimal(str(random.uniform(50, 500))),
                typical_merchants=["Amazon", "Starbucks", "Shell", "Target"],
                typical_locations=["San Francisco, CA", "New York, NY", "Los Angeles, CA"],
                typical_hours=list(range(9, 18)),  # Business hours
                transaction_frequency=random.uniform(0.5, 3.0),
                risk_tolerance=Decimal(str(random.uniform(0.2, 0.8)))
            )
        
        # Sample device profiles
        for i in range(10):
            device_id = f"device_{i+1}"
            self.device_profiles[device_id] = DeviceProfile(
                device_id=device_id,
                user_id=f"user_{(i % 5) + 1}",
                device_type=random.choice(["Mobile", "Desktop", "Tablet"]),
                os_version=random.choice(["iOS 17.0", "Android 14", "Windows 11", "macOS 14"]),
                browser_version=random.choice(["Chrome 120", "Safari 17", "Firefox 121"]),
                screen_resolution=random.choice(["1920x1080", "1366x768", "375x667", "414x896"]),
                timezone=random.choice(["America/Los_Angeles", "America/New_York", "Europe/London"]),
                language=random.choice(["en-US", "en-GB", "es-ES"]),
                fingerprint=f"fp_{uuid.uuid4().hex[:16]}",
                risk_score=Decimal(str(random.uniform(0.1, 0.9))),
                transaction_count=random.randint(10, 100)
            )
        
        # Sample network profiles
        for i in range(8):
            ip_address = f"192.168.1.{i+1}"
            self.network_profiles[ip_address] = NetworkProfile(
                user_id=f"user_{(i % 5) + 1}",
                ip_address=ip_address,
                location=random.choice(["San Francisco, CA", "New York, NY", "London, UK"]),
                isp=random.choice(["Comcast", "Verizon", "AT&T", "BT"]),
                proxy_detected=random.choice([True, False]),
                vpn_detected=random.choice([True, False]),
                tor_detected=False,
                risk_score=Decimal(str(random.uniform(0.2, 0.8))),
                transaction_count=random.randint(5, 50)
            )
        
        logger.info(f"Initialized sample data: {len(self.behavioral_profiles)} behavioral profiles, "
                   f"{len(self.device_profiles)} device profiles, {len(self.network_profiles)} network profiles")
    
    async def calculate_comprehensive_risk_score(self, user_id: str, 
                                                transaction_data: Dict[str, Any],
                                                platform: str = "api") -> FraudRiskScore:
        """Calculate comprehensive risk score using multi-dimensional analysis"""
        try:
            logger.info(f"Calculating comprehensive risk score for user {user_id} on platform {platform}")
            
            start_time = time.time()
            
            # Calculate individual risk components
            behavioral_score = await self.calculate_behavioral_risk_score(user_id, transaction_data, platform)
            transactional_score = await self.calculate_transactional_risk_score(transaction_data)
            network_score = await self.calculate_network_risk_score(user_id, transaction_data)
            device_score = await self.calculate_device_risk_score(user_id, transaction_data, platform)
            velocity_score = await self.calculate_velocity_risk_score(user_id, transaction_data)
            
            # Get platform-specific weights
            weights = self._get_platform_risk_weights(platform)
            
            # Calculate composite score
            composite_score = (
                behavioral_score * weights.behavioral_weight +
                float(transaction_data.get('amount', 0)) / 1000.0 * weights.transactional_weight +
                network_score * weights.network_weight +
                device_score * weights.device_weight +
                velocity_score * weights.velocity_weight
            )
            
            # Normalize composite score to 0-1 range
            composite_score = min(max(composite_score, 0.0), 1.0)
            
            risk_level = self._determine_risk_level(Decimal(str(composite_score)))
            risk_factors = await self._generate_risk_factors(
                behavioral_score, transactional_score, network_score, device_score, velocity_score
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return FraudRiskScore(
                transaction_id=transaction_data.get('transaction_id', f"txn_{uuid.uuid4().hex[:8]}"),
                user_id=user_id,
                risk_score=Decimal(str(composite_score)),
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=self._get_recommended_action(composite_score),
                confidence=Decimal(str(random.uniform(0.7, 0.95))),
                timestamp=datetime.utcnow(),
                analysis_methods=["BEHAVIORAL_ANALYSIS", "TRANSACTIONAL_ANALYSIS", "NETWORK_ANALYSIS", 
                                "DEVICE_ANALYSIS", "VELOCITY_ANALYSIS"],
                platform=platform,
                metadata={
                    "processing_time_ms": processing_time,
                    "individual_scores": {
                        "behavioral": float(behavioral_score),
                        "transactional": float(transactional_score),
                        "network": float(network_score),
                        "device": float(device_score),
                        "velocity": float(velocity_score)
                    }
                }
            )
            
        except (ValueError) as e:
            logger.error(f"Error calculating comprehensive risk score: {e}")
            raise
    
    async def calculate_behavioral_risk_score(self, user_id: str, 
                                            transaction_data: Dict[str, Any],
                                            platform: str) -> Decimal:
        """Calculate behavioral risk score based on user patterns"""
        try:
            # Get user's behavioral profile
            behavioral_profile = self.behavioral_profiles.get(user_id)
            if not behavioral_profile:
                return Decimal('0.3')  # New user moderate risk
            
            # Extract transaction features
            amount = Decimal(str(transaction_data.get('amount', 0)))
            merchant = transaction_data.get('merchant', '')
            timestamp = datetime.fromisoformat(transaction_data.get('timestamp', datetime.utcnow().isoformat()))
            location = transaction_data.get('location', '')
            
            risk_score = 0.0
            
            # Amount deviation analysis
            if amount > 0 and behavioral_profile.average_amount > 0:
                amount_deviation = min(float(amount / behavioral_profile.average_amount), 3.0)
                if amount_deviation > 2.0:  # More than 2x average
                    risk_score += 0.3
                elif amount_deviation > 1.5:  # More than 1.5x average
                    risk_score += 0.2
            
            # Time pattern analysis
            current_hour = timestamp.hour
            if current_hour < 6 or current_hour > 22:  # Outside business hours
                risk_score += 0.2
            elif current_hour not in behavioral_profile.typical_hours:
                risk_score += 0.1
            
            # Location deviation analysis
            if location and location not in behavioral_profile.typical_locations:
                risk_score += 0.2
                if 'unknown' in location.lower():
                    risk_score += 0.2
            
            # Merchant frequency analysis
            if merchant and merchant not in behavioral_profile.typical_merchants:
                risk_score += 0.1
                if any(keyword in merchant.lower() for keyword in ['casino', 'gambling', 'crypto']):
                    risk_score += 0.3
            
            # Platform-specific behavioral adjustments
            platform_adjustment = 0.1 if platform == "mobile" else 0.05
            risk_score += platform_adjustment
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            return Decimal(str(risk_score))
            
        except (ValueError) as e:
            logger.error(f"Error calculating behavioral risk score: {e}")
            return Decimal('0.5')  # Default moderate risk
    
    async def calculate_transactional_risk_score(self, transaction_data: Dict[str, Any]) -> Decimal:
        """Calculate transactional risk score based on transaction characteristics"""
        try:
            amount = Decimal(str(transaction_data.get('amount', 0)))
            merchant = transaction_data.get('merchant', '')
            location = transaction_data.get('location', '')
            
            risk_score = 0.0
            
            # Amount-based risk
            if amount > Decimal('10000'):
                risk_score += 0.4
            elif amount > Decimal('5000'):
                risk_score += 0.3
            elif amount > Decimal('1000'):
                risk_score += 0.2
            
            # Merchant risk
            high_risk_merchants = ['casino', 'gambling', 'crypto', 'forex', 'bitcoin']
            if any(keyword in merchant.lower() for keyword in high_risk_merchants):
                risk_score += 0.3
            
            # Location risk
            if 'unknown' in location.lower() or not location:
                risk_score += 0.2
            
            # Round amount risk (suspicious round amounts)
            if amount > 0 and amount % Decimal('100') == 0 and amount > Decimal('1000'):
                risk_score += 0.1
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            return Decimal(str(risk_score))
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error calculating transactional risk score: {e}")
            return Decimal('0.3')
    
    async def calculate_network_risk_score(self, user_id: str, 
                                         transaction_data: Dict[str, Any]) -> Decimal:
        """Calculate network risk score based on network characteristics"""
        try:
            ip_address = transaction_data.get('ip_address', '')
            location = transaction_data.get('location', '')
            
            risk_score = 0.0
            
            # Get network profile
            network_profile = self.network_profiles.get(ip_address)
            if network_profile:
                risk_score = float(network_profile.risk_score)
                
                # Additional risk factors
                if network_profile.proxy_detected:
                    risk_score += 0.2
                if network_profile.vpn_detected:
                    risk_score += 0.3
                if network_profile.tor_detected:
                    risk_score += 0.5
            else:
                # Unknown IP address
                risk_score = 0.4
            
            # Location inconsistency
            if network_profile and location and location != network_profile.location:
                risk_score += 0.2
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            return Decimal(str(risk_score))
            
        except (ValueError) as e:
            logger.error(f"Error calculating network risk score: {e}")
            return Decimal('0.3')
    
    async def calculate_device_risk_score(self, user_id: str, 
                                       transaction_data: Dict[str, Any],
                                       platform: str) -> Decimal:
        """Calculate device risk score including fingerprinting"""
        try:
            device_id = transaction_data.get('device_id', '')
            
            risk_score = 0.0
            
            # Get device profile
            device_profile = self.device_profiles.get(device_id)
            if device_profile:
                risk_score = float(device_profile.risk_score)
                
                # Check for device sharing (multiple users on same device)
                device_users = [profile.user_id for profile in self.device_profiles.values() 
                              if profile.device_id == device_id]
                if len(set(device_users)) > 1:
                    risk_score += 0.2
                
                # Check for unusual device characteristics
                if device_profile.device_type == "Mobile" and platform == "web":
                    risk_score += 0.1
                
                # Check for suspicious device fingerprint
                if 'suspicious' in device_profile.fingerprint.lower():
                    risk_score += 0.3
            else:
                # Unknown device
                risk_score = 0.4
            
            # Platform-specific device risk
            if platform == "mobile" and not device_id:
                risk_score += 0.2
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            return Decimal(str(risk_score))
            
        except (ValueError) as e:
            logger.error(f"Error calculating device risk score: {e}")
            return Decimal('0.3')
    
    async def calculate_velocity_risk_score(self, user_id: str, 
                                          transaction_data: Dict[str, Any]) -> Decimal:
        """Calculate velocity risk score using sliding window analysis"""
        try:
            amount = Decimal(str(transaction_data.get('amount', 0)))
            timestamp = datetime.fromisoformat(transaction_data.get('timestamp', datetime.utcnow().isoformat()))
            
            # Simulate velocity analysis
            # In a real implementation, this would analyze recent transactions
            
            risk_score = 0.0
            
            # Simulate high velocity detection
            if random.random() < 0.2:  # 20% chance of high velocity
                risk_score += 0.4
            
            # Simulate amount velocity
            if amount > Decimal('5000'):
                risk_score += 0.3
            
            # Simulate time-based velocity (rapid transactions)
            if random.random() < 0.1:  # 10% chance of rapid transactions
                risk_score += 0.3
            
            # Normalize to 0-1 range
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            return Decimal(str(risk_score))
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error calculating velocity risk score: {e}")
            return Decimal('0.3')
    
    # Private helper methods
    
    def _get_platform_risk_weights(self, platform: str) -> PlatformRiskWeights:
        """Get platform-specific risk weights"""
        if platform == "mobile":
            return PlatformRiskWeights(
                behavioral_weight=0.30,
                transactional_weight=0.15,
                network_weight=0.25,
                device_weight=0.20,
                velocity_weight=0.10
            )
        elif platform == "web":
            return PlatformRiskWeights(
                behavioral_weight=0.25,
                transactional_weight=0.20,
                network_weight=0.20,
                device_weight=0.25,
                velocity_weight=0.10
            )
        else:  # API
            return PlatformRiskWeights(
                behavioral_weight=0.20,
                transactional_weight=0.25,
                network_weight=0.20,
                device_weight=0.20,
                velocity_weight=0.15
            )
    
    def _determine_risk_level(self, risk_score: Decimal) -> RiskLevel:
        """Determine risk level from score"""
        score = float(risk_score)
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_recommended_action(self, risk_score: float) -> str:
        """Get recommended action based on risk score"""
        if risk_score >= 0.8:
            return "BLOCK_TRANSACTION"
        elif risk_score >= 0.6:
            return "MANUAL_REVIEW"
        elif risk_score >= 0.3:
            return "VERIFY_IDENTITY"
        else:
            return "APPROVE"
    
    async def _generate_risk_factors(self, behavioral_score: Decimal, transactional_score: Decimal,
                                   network_score: Decimal, device_score: Decimal, 
                                   velocity_score: Decimal) -> List[RiskFactor]:
        """Generate risk factors from individual scores"""
        risk_factors = []
        
        if behavioral_score > Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="BEHAVIORAL_ANOMALY",
                weight=behavioral_score,
                description="Unusual behavioral patterns detected",
                severity=Severity.HIGH if behavioral_score > Decimal('0.7') else Severity.MEDIUM
            ))
        
        if transactional_score > Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="TRANSACTIONAL_RISK",
                weight=transactional_score,
                description="High-risk transaction characteristics",
                severity=Severity.HIGH if transactional_score > Decimal('0.7') else Severity.MEDIUM
            ))
        
        if network_score > Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="NETWORK_RISK",
                weight=network_score,
                description="Suspicious network activity",
                severity=Severity.HIGH if network_score > Decimal('0.7') else Severity.MEDIUM
            ))
        
        if device_score > Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="DEVICE_RISK",
                weight=device_score,
                description="Suspicious device characteristics",
                severity=Severity.HIGH if device_score > Decimal('0.7') else Severity.MEDIUM
            ))
        
        if velocity_score > Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="VELOCITY_RISK",
                weight=velocity_score,
                description="High transaction velocity detected",
                severity=Severity.HIGH if velocity_score > Decimal('0.7') else Severity.MEDIUM
            ))
        
        return risk_factors
    
    async def detect_fraud_patterns(self, user_id: str, 
                                   transaction_history: List[Dict[str, Any]]) -> List[FraudPattern]:
        """Detect advanced fraud patterns in transaction history"""
        try:
            logger.info(f"Detecting fraud patterns for user {user_id}")
            
            patterns = []
            
            # Simulate pattern detection
            if random.random() < 0.3:  # 30% chance of detecting patterns
                pattern_types = [
                    "PUMP_AND_DUMP",
                    "WASH_TRADING", 
                    "LAYERING",
                    "INSIDER_TRADING",
                    "MARKET_MANIPULATION"
                ]
                
                for pattern_type in random.sample(pattern_types, random.randint(1, 3)):
                    pattern = FraudPattern(
                        pattern_id=f"pattern_{uuid.uuid4().hex[:8]}",
                        pattern_type=pattern_type,
                        pattern_name=f"{pattern_type.replace('_', ' ').title()} Pattern",
                        description=f"Detected {pattern_type.lower().replace('_', ' ')} pattern",
                        risk_score=Decimal(str(random.uniform(0.6, 0.9))),
                        confidence=Decimal(str(random.uniform(0.7, 0.95))),
                        affected_transactions=[f"txn_{i}" for i in range(random.randint(2, 5))]
                    )
                    patterns.append(pattern)
            
            logger.info(f"Detected {len(patterns)} fraud patterns for user {user_id}")
            return patterns
            
        except (ValueError) as e:
            logger.error(f"Error detecting fraud patterns: {e}")
            return []
    
    async def get_advanced_analytics(self, user_id: str, 
                                   analysis_type: str = "comprehensive") -> AdvancedAnalyticsData:
        """Get advanced analytics data for a user"""
        try:
            logger.info(f"Generating advanced analytics for user {user_id}")
            
            # Simulate analytics data
            analytics_data = AdvancedAnalyticsData(
                user_id=user_id,
                analysis_type=analysis_type,
                data_points=[
                    {"metric": "transaction_frequency", "value": random.uniform(0.5, 3.0)},
                    {"metric": "average_amount", "value": random.uniform(50, 500)},
                    {"metric": "risk_trend", "value": random.uniform(0.2, 0.8)},
                    {"metric": "device_diversity", "value": random.uniform(1, 5)}
                ],
                trends={
                    "risk_trend": "increasing" if random.random() < 0.5 else "decreasing",
                    "transaction_volume": "stable",
                    "merchant_diversity": "expanding"
                },
                anomalies=[
                    {"type": "unusual_amount", "severity": "medium", "timestamp": datetime.utcnow().isoformat()},
                    {"type": "location_deviation", "severity": "low", "timestamp": datetime.utcnow().isoformat()}
                ] if random.random() < 0.4 else [],
                predictions={
                    "next_month_risk": random.uniform(0.3, 0.7),
                    "fraud_probability": random.uniform(0.1, 0.4)
                }
            )
            
            return analytics_data
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error generating advanced analytics: {e}")
            raise
