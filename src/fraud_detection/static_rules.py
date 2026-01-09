"""
Static Fraud Detection Rules
Migrated from C# FraudDetectionAgent.Api.Services.RuleEngine static rules
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .rules_engine_models import RuleResult, RuleActionType, RuleAction
from .fraud_tools_models import RiskFactor, RiskLevel

logger = logging.getLogger(__name__)


class IRule(ABC):
    """Interface for fraud detection rules"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Rule name"""
        pass
    
    @abstractmethod
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate the rule against a transaction"""
        pass


class HighAmountRule(IRule):
    """Rule for detecting high amount transactions"""
    
    @property
    def name(self) -> str:
        return "HIGH_AMOUNT_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate high amount rule"""
        try:
            amount = transaction.get('amount', 0)
            
            if amount >= 10000:
                return RiskFactor(
                    type="HIGH_AMOUNT",
                    weight=0.8,
                    description=f"Amount ${amount:.2f} exceeds threshold",
                    severity=RiskLevel.HIGH
                )
            elif amount >= 5000:
                return RiskFactor(
                    type="ELEVATED_AMOUNT",
                    weight=0.6,
                    description=f"Amount ${amount:.2f} is high",
                    severity=RiskLevel.MEDIUM
                )
            elif amount >= 1000:
                return RiskFactor(
                    type="MODERATE_AMOUNT",
                    weight=0.3,
                    description=f"Amount ${amount:.2f} is moderate",
                    severity=RiskLevel.LOW
                )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in HighAmountRule: {e}")
            return None


class OffHoursLargeTxnRule(IRule):
    """Rule for detecting large transactions during off-hours"""
    
    @property
    def name(self) -> str:
        return "OFF_HOURS_LARGE_TXN_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate off-hours large transaction rule"""
        try:
            amount = transaction.get('amount', 0)
            timestamp_str = transaction.get('timestamp')
            
            if not timestamp_str:
                return None
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            
            hour = timestamp.hour
            off_hours = hour < 6 or hour > 22
            
            if off_hours and amount > 1000:
                return RiskFactor(
                    type="OFF_HOURS_TRANSACTION",
                    weight=0.5,
                    description="Large transaction during off-hours",
                    severity=RiskLevel.MEDIUM
                )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in OffHoursLargeTxnRule: {e}")
            return None


class NewDeviceRule(IRule):
    """Rule for detecting transactions from unknown devices"""
    
    def __init__(self, api_handler=None):
        self.api_handler = api_handler
    
    @property
    def name(self) -> str:
        return "NEW_DEVICE_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate new device rule"""
        try:
            device_id = transaction.get('device_id')
            if not device_id:
                return None
            
            # Mock implementation - in real scenario, would check against known devices
            if self.api_handler:
                known_devices = await self.api_handler.get_known_devices_async(account_id)
                if device_id not in known_devices:
                    return RiskFactor(
                        type="UNKNOWN_DEVICE",
                        weight=0.7,
                        description=f"Transaction from unknown device: {device_id}",
                        severity=RiskLevel.HIGH
                    )
            else:
                # Mock logic for testing
                if device_id.startswith('unknown_'):
                    return RiskFactor(
                        type="UNKNOWN_DEVICE",
                        weight=0.7,
                        description=f"Transaction from unknown device: {device_id}",
                        severity=RiskLevel.HIGH
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in NewDeviceRule: {e}")
            return None


class UnusualLocationRule(IRule):
    """Rule for detecting transactions from unusual locations"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "UNUSUAL_LOCATION_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate unusual location rule"""
        try:
            location = transaction.get('location')
            if not location:
                return None
            
            # Mock implementation - in real scenario, would check against typical locations
            if self.api_handler:
                typical_locations = await self.api_handler.get_typical_locations_async(account_id)
                is_typical = any(location.lower() in loc.lower() for loc in typical_locations)
                
                if not is_typical:
                    high_risk_locations = self.settings.get('high_risk_locations', [])
                    is_high_risk = any(location.lower() in hrl.lower() for hrl in high_risk_locations)
                    
                    if is_high_risk:
                        return RiskFactor(
                            type="HIGH_RISK_LOCATION",
                            weight=0.9,
                            description=f"High-risk location: {location}",
                            severity=RiskLevel.CRITICAL
                        )
                    else:
                        return RiskFactor(
                            type="LOCATION_ANOMALY",
                            weight=0.6,
                            description=f"Unusual location: {location}",
                            severity=RiskLevel.MEDIUM
                        )
            else:
                # Mock logic for testing
                if 'unusual' in location.lower():
                    return RiskFactor(
                        type="LOCATION_ANOMALY",
                        weight=0.6,
                        description=f"Unusual location: {location}",
                        severity=RiskLevel.MEDIUM
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in UnusualLocationRule: {e}")
            return None


class VelocityBurstRule(IRule):
    """Rule for detecting high velocity transactions"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "VELOCITY_BURST_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate velocity burst rule"""
        try:
            max_transactions_per_hour = self.settings.get('max_transactions_per_hour', 50)
            
            if self.api_handler:
                recent_transactions = await self.api_handler.get_recent_transactions_async(account_id)
                if recent_transactions:
                    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                    last_hour_count = sum(1 for t in recent_transactions 
                                        if t.get('timestamp', datetime.min) > one_hour_ago)
                    
                    if last_hour_count > max_transactions_per_hour:
                        return RiskFactor(
                            type="HIGH_VELOCITY",
                            weight=0.7,
                            description=f"{last_hour_count} transactions in last hour",
                            severity=RiskLevel.HIGH
                        )
            else:
                # Mock logic for testing
                if account_id.endswith('_high_velocity'):
                    return RiskFactor(
                        type="HIGH_VELOCITY",
                        weight=0.7,
                        description="High velocity detected (mock)",
                        severity=RiskLevel.HIGH
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in VelocityBurstRule: {e}")
            return None


class AmountVelocityRule(IRule):
    """Rule for detecting high amount velocity"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "AMOUNT_VELOCITY_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate amount velocity rule"""
        try:
            amount_velocity_threshold = self.settings.get('amount_velocity_threshold', 5000)
            
            if self.api_handler:
                recent_transactions = await self.api_handler.get_recent_transactions_async(account_id)
                if recent_transactions:
                    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                    recent_amounts = sum(t.get('amount', 0) for t in recent_transactions 
                                       if t.get('timestamp', datetime.min) > one_hour_ago)
                    
                    if recent_amounts > amount_velocity_threshold:
                        return RiskFactor(
                            type="AMOUNT_VELOCITY",
                            weight=0.6,
                            description=f"High amount velocity: ${recent_amounts:.2f} in last hour",
                            severity=RiskLevel.MEDIUM
                        )
            else:
                # Mock logic for testing
                if account_id.endswith('_high_amount_velocity'):
                    return RiskFactor(
                        type="AMOUNT_VELOCITY",
                        weight=0.6,
                        description="High amount velocity detected (mock)",
                        severity=RiskLevel.MEDIUM
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in AmountVelocityRule: {e}")
            return None


class NewPayeeHighAmountRule(IRule):
    """Rule for detecting high amounts to new payees"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "NEW_PAYEE_HIGH_AMOUNT_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate new payee high amount rule"""
        try:
            amount = transaction.get('amount', 0)
            payee = transaction.get('payee') or transaction.get('merchant_name')
            new_payee_threshold = self.settings.get('new_payee_high_amount_threshold', 1000)
            
            if not payee:
                return None
            
            if self.api_handler:
                # Check if this is a new payee
                is_new_payee = await self.api_handler.is_new_payee_async(account_id, payee)
                
                if is_new_payee and amount > new_payee_threshold:
                    return RiskFactor(
                        type="NEW_PAYEE_HIGH_AMOUNT",
                        weight=0.8,
                        description=f"High amount ${amount:.2f} to new payee: {payee}",
                        severity=RiskLevel.HIGH
                    )
            else:
                # Mock logic for testing
                if payee.startswith('new_') and amount > new_payee_threshold:
                    return RiskFactor(
                        type="NEW_PAYEE_HIGH_AMOUNT",
                        weight=0.8,
                        description=f"High amount ${amount:.2f} to new payee: {payee}",
                        severity=RiskLevel.HIGH
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in NewPayeeHighAmountRule: {e}")
            return None


class ImpossibleTravelRule(IRule):
    """Rule for detecting impossible travel patterns"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "IMPOSSIBLE_TRAVEL_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate impossible travel rule"""
        try:
            location = transaction.get('location')
            timestamp_str = transaction.get('timestamp')
            
            if not location or not timestamp_str:
                return None
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timestamp_str
            
            impossible_travel_threshold_minutes = self.settings.get('impossible_travel_minutes_threshold', 30)
            
            if self.api_handler:
                # Get last transaction location and time
                last_transaction = await self.api_handler.get_last_transaction_async(account_id)
                
                if last_transaction:
                    last_location = last_transaction.get('location')
                    last_timestamp_str = last_transaction.get('timestamp')
                    
                    if last_location and last_timestamp_str:
                        if isinstance(last_timestamp_str, str):
                            last_timestamp = datetime.fromisoformat(last_timestamp_str.replace('Z', '+00:00'))
                        else:
                            last_timestamp = last_timestamp_str
                        
                        time_diff = timestamp - last_timestamp
                        time_diff_minutes = time_diff.total_seconds() / 60
                        
                        # Check if locations are different and time difference is too short
                        if (location.lower() != last_location.lower() and 
                            time_diff_minutes < impossible_travel_threshold_minutes):
                            
                            return RiskFactor(
                                type="IMPOSSIBLE_TRAVEL",
                                weight=0.9,
                                description=f"Impossible travel: {last_location} to {location} in {time_diff_minutes:.1f} minutes",
                                severity=RiskLevel.CRITICAL
                            )
            else:
                # Mock logic for testing
                if 'impossible_travel' in location.lower():
                    return RiskFactor(
                        type="IMPOSSIBLE_TRAVEL",
                        weight=0.9,
                        description="Impossible travel detected (mock)",
                        severity=RiskLevel.CRITICAL
                    )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in ImpossibleTravelRule: {e}")
            return None


class HighRiskMerchantRule(IRule):
    """Rule for detecting transactions with high-risk merchants"""
    
    def __init__(self, api_handler=None, settings=None):
        self.api_handler = api_handler
        self.settings = settings or {}
    
    @property
    def name(self) -> str:
        return "HIGH_RISK_MERCHANT_RULE"
    
    async def evaluate_async(self, transaction: Dict[str, Any], account_id: str) -> Optional[RiskFactor]:
        """Evaluate high-risk merchant rule"""
        try:
            merchant_name = transaction.get('merchant_name') or transaction.get('payee')
            merchant_category = transaction.get('merchant_category')
            
            if not merchant_name:
                return None
            
            high_risk_merchants = self.settings.get('high_risk_merchants', [])
            high_risk_categories = self.settings.get('high_risk_merchant_categories', [])
            
            # Check merchant name
            is_high_risk_merchant = any(merchant_name.lower() in hrm.lower() for hrm in high_risk_merchants)
            
            # Check merchant category
            is_high_risk_category = (merchant_category and 
                                   any(merchant_category.lower() in hrc.lower() for hrc in high_risk_categories))
            
            if is_high_risk_merchant or is_high_risk_category:
                return RiskFactor(
                    type="HIGH_RISK_MERCHANT",
                    weight=0.7,
                    description=f"High-risk merchant: {merchant_name}",
                    severity=RiskLevel.HIGH
                )
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in HighRiskMerchantRule: {e}")
            return None


def get_default_static_rules(api_handler=None, settings=None) -> List[IRule]:
    """Get the default set of static rules"""
    return [
        HighAmountRule(),
        OffHoursLargeTxnRule(),
        NewDeviceRule(api_handler),
        UnusualLocationRule(api_handler, settings),
        VelocityBurstRule(api_handler, settings),
        AmountVelocityRule(api_handler, settings),
        NewPayeeHighAmountRule(api_handler, settings),
        ImpossibleTravelRule(api_handler, settings),
        HighRiskMerchantRule(api_handler, settings)
    ]
