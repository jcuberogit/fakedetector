#!/usr/bin/env python3
"""
Investment Fraud Detection Service
Python equivalent of C# InvestmentFraudDetectionService.cs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from decimal import Decimal
import statistics
import random

from .investment_models import (
    InvestmentPortfolio, InvestmentTransaction, InvestmentTransactionRequest,
    InvestmentRiskAssessment, InvestmentValidationResult, TradingPattern,
    RiskFactor, RiskLevel, Severity, TransactionType
)

logger = logging.getLogger(__name__)


class InvestmentFraudDetectionService:
    """
    Advanced Investment Fraud Detection Service
    
    Implements sophisticated algorithms for detecting investment-related fraud patterns.
    Python equivalent of C# InvestmentFraudDetectionService.
    """
    
    def __init__(self):
        # Fraud detection thresholds (matching C# constants)
        self.HIGH_RISK_THRESHOLD = Decimal('0.7')
        self.MEDIUM_RISK_THRESHOLD = Decimal('0.4')
        self.MAX_DAILY_TRANSACTIONS = 50
        self.MAX_SINGLE_TRADE_PERCENTAGE = Decimal('0.2')  # 20% of portfolio
        self.PENNY_STOCK_THRESHOLD = Decimal('5.0')
        
        logger.info("InvestmentFraudDetectionService initialized")
    
    async def assess_investment_risk_async(self, user_id: str) -> InvestmentRiskAssessment:
        """
        Comprehensive investment fraud risk assessment
        
        Args:
            user_id: User identifier
            
        Returns:
            InvestmentRiskAssessment: Complete risk assessment
        """
        logger.info(f"Starting comprehensive investment risk assessment for user {user_id}")
        
        try:
            # Get user portfolio and transactions (mock implementation)
            portfolio = await self._get_user_portfolio_async(user_id)
            transactions = await self._get_investment_transactions_async(user_id, 30)
            
            risk_factors = []
            total_risk_score = Decimal('0')
            
            # 1. Trading Velocity Analysis
            velocity_risk = self._analyze_trading_velocity(transactions)
            risk_factors.extend(velocity_risk[0])
            total_risk_score += velocity_risk[1]
            
            # 2. Portfolio Concentration Risk
            concentration_risk = self._analyze_portfolio_concentration(portfolio)
            risk_factors.extend(concentration_risk[0])
            total_risk_score += concentration_risk[1]
            
            # 3. Unusual Trading Patterns
            pattern_risk = await self._analyze_unusual_trading_patterns_async(transactions)
            risk_factors.extend(pattern_risk[0])
            total_risk_score += pattern_risk[1]
            
            # 4. High-Risk Securities Analysis
            securities_risk = self._analyze_high_risk_securities(portfolio, transactions)
            risk_factors.extend(securities_risk[0])
            total_risk_score += securities_risk[1]
            
            # 5. Market Timing Analysis
            timing_risk = self._analyze_market_timing(transactions)
            risk_factors.extend(timing_risk[0])
            total_risk_score += timing_risk[1]
            
            # Normalize risk score (0-1 scale)
            normalized_score = min(total_risk_score / Decimal('5'), Decimal('1'))
            risk_level = self._get_risk_level(normalized_score)
            recommendations = self._generate_recommendations(risk_factors, normalized_score)
            
            logger.info(f"Investment risk assessment completed for user {user_id}. "
                       f"Risk Level: {risk_level}, Score: {normalized_score}")
            
            return InvestmentRiskAssessment(
                user_id=user_id,
                overall_risk_score=normalized_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                assessment_date=datetime.utcnow()
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error during investment risk assessment for user {user_id}: {e}")
            raise
    
    async def validate_transaction_async(
        self, 
        user_id: str, 
        request: InvestmentTransactionRequest
    ) -> InvestmentValidationResult:
        """
        Real-time transaction fraud validation
        
        Args:
            user_id: User identifier
            request: Transaction request
            
        Returns:
            InvestmentValidationResult: Validation result
        """
        logger.info(f"Validating investment transaction for user {user_id}: "
                   f"{request.symbol} {request.transaction_type} "
                   f"{request.quantity}@{request.estimated_price}")
        
        try:
            portfolio = await self._get_user_portfolio_async(user_id)
            recent_transactions = await self._get_investment_transactions_async(user_id, 7)
            
            risk_factors = []
            risk_score = Decimal('0')
            
            # 1. Transaction Size Analysis
            transaction_value = request.quantity * request.estimated_price
            if transaction_value > portfolio.total_value * self.MAX_SINGLE_TRADE_PERCENTAGE:
                risk_factors.append(
                    f"Large transaction (${transaction_value:,.2f}) exceeds "
                    f"{self.MAX_SINGLE_TRADE_PERCENTAGE:.0%} of portfolio value"
                )
                risk_score += Decimal('0.3')
            
            # 2. Penny Stock Detection
            if request.estimated_price < self.PENNY_STOCK_THRESHOLD:
                risk_factors.append(
                    f"Penny stock transaction (${request.estimated_price:.2f} < "
                    f"${self.PENNY_STOCK_THRESHOLD})"
                )
                risk_score += Decimal('0.2')
            
            # 3. Rapid Trading Detection
            today_transactions = len([
                t for t in recent_transactions 
                if t.transaction_date.date() == datetime.today().date()
            ])
            if today_transactions >= self.MAX_DAILY_TRANSACTIONS:
                risk_factors.append(
                    f"Excessive daily trading activity ({today_transactions} transactions today)"
                )
                risk_score += Decimal('0.4')
            
            # 4. Symbol-Specific Velocity Check
            symbol_transactions = len([
                t for t in recent_transactions 
                if t.symbol == request.symbol
            ])
            if symbol_transactions > 10:
                risk_factors.append(
                    f"High frequency trading in {request.symbol} "
                    f"({symbol_transactions} transactions this week)"
                )
                risk_score += Decimal('0.3')
            
            # 5. After-Hours Trading Detection
            current_time = datetime.now().time()
            market_open = datetime.strptime("09:00", "%H:%M").time()
            market_close = datetime.strptime("16:00", "%H:%M").time()
            
            if current_time < market_open or current_time > market_close:
                risk_factors.append("After-hours trading attempt")
                risk_score += Decimal('0.1')
            
            is_valid = risk_score < self.HIGH_RISK_THRESHOLD
            requires_approval = risk_score > self.MEDIUM_RISK_THRESHOLD
            validation_message = (
                "Transaction approved" if is_valid 
                else "Transaction blocked due to high risk"
            )
            
            logger.info(f"Transaction validation completed for user {user_id}. "
                       f"Valid: {is_valid}, Risk Score: {risk_score}")
            
            return InvestmentValidationResult(
                is_valid=is_valid,
                risk_score=min(risk_score, Decimal('1')),
                risk_factors=risk_factors,
                validation_message=validation_message,
                requires_approval=requires_approval
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error validating investment transaction for user {user_id}: {e}")
            raise
    
    async def detect_advanced_fraud_patterns_async(self, user_id: str) -> List[TradingPattern]:
        """
        Detect sophisticated fraud patterns using machine learning techniques
        
        Args:
            user_id: User identifier
            
        Returns:
            List[TradingPattern]: Detected fraud patterns
        """
        logger.info(f"Detecting advanced fraud patterns for user {user_id}")
        
        try:
            transactions = await self._get_investment_transactions_async(user_id, 90)
            patterns = []
            
            # 1. Pump and Dump Detection
            pump_dump_patterns = self._detect_pump_and_dump_patterns(transactions)
            patterns.extend(pump_dump_patterns)
            
            # 2. Wash Trading Detection
            wash_trading_patterns = self._detect_wash_trading_patterns(transactions)
            patterns.extend(wash_trading_patterns)
            
            # 3. Layering/Spoofing Detection
            layering_patterns = self._detect_layering_patterns(transactions)
            patterns.extend(layering_patterns)
            
            # 4. Insider Trading Indicators
            insider_trading_patterns = self._detect_insider_trading_indicators(transactions)
            patterns.extend(insider_trading_patterns)
            
            # 5. Market Manipulation Patterns
            manipulation_patterns = self._detect_market_manipulation_patterns(transactions)
            patterns.extend(manipulation_patterns)
            
            logger.info(f"Advanced fraud pattern detection completed for user {user_id}. "
                       f"Found {len(patterns)} suspicious patterns")
            
            return patterns
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error detecting advanced fraud patterns for user {user_id}: {e}")
            raise
    
    # Risk Analysis Methods
    
    def _analyze_trading_velocity(self, transactions: List[InvestmentTransaction]) -> Tuple[List[RiskFactor], Decimal]:
        """Analyze trading velocity patterns"""
        risk_factors = []
        score = Decimal('0')
        
        if not transactions:
            return risk_factors, score
        
        # Analyze daily trading frequency
        daily_counts = {}
        for transaction in transactions:
            date = transaction.transaction_date.date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        if daily_counts:
            avg_daily_transactions = statistics.mean(daily_counts.values())
            max_daily_transactions = max(daily_counts.values())
            
            if avg_daily_transactions > 20:
                risk_factors.append(RiskFactor(
                    type="High Average Trading Velocity",
                    weight=Decimal('0.3'),
                    description=f"Average {avg_daily_transactions:.1f} transactions per day",
                    severity=Severity.MEDIUM
                ))
                score += Decimal('0.3')
            
            if max_daily_transactions > self.MAX_DAILY_TRANSACTIONS:
                risk_factors.append(RiskFactor(
                    type="Excessive Daily Trading",
                    weight=Decimal('0.4'),
                    description=f"Maximum {max_daily_transactions} transactions in a single day",
                    severity=Severity.HIGH
                ))
                score += Decimal('0.4')
        
        return risk_factors, score
    
    def _analyze_portfolio_concentration(self, portfolio: InvestmentPortfolio) -> Tuple[List[RiskFactor], Decimal]:
        """Analyze portfolio concentration risk"""
        risk_factors = []
        score = Decimal('0')
        
        if not portfolio.holdings:
            return risk_factors, score
        
        # Analyze concentration risk
        top_holding = max(portfolio.holdings, key=lambda h: h.market_value)
        top_holding_percentage = top_holding.market_value / portfolio.total_value
        
        if top_holding_percentage > Decimal('0.3'):
            risk_factors.append(RiskFactor(
                type="High Portfolio Concentration",
                weight=Decimal('0.2'),
                description=f"{top_holding.symbol} represents {top_holding_percentage:.1%} of portfolio",
                severity=Severity.MEDIUM
            ))
            score += Decimal('0.2')
        
        # Analyze sector concentration
        sector_allocation = {}
        for holding in portfolio.holdings:
            sector = self._get_sector_from_symbol(holding.symbol)
            sector_allocation[sector] = sector_allocation.get(sector, Decimal('0')) + holding.market_value
        
        if sector_allocation:
            max_sector_percentage = max(sector_allocation.values()) / portfolio.total_value
            if max_sector_percentage > Decimal('0.5'):
                max_sector = max(sector_allocation, key=sector_allocation.get)
                risk_factors.append(RiskFactor(
                    type="High Sector Concentration",
                    weight=Decimal('0.15'),
                    description=f"{max_sector} sector represents {max_sector_percentage:.1%} of portfolio",
                    severity=Severity.LOW
                ))
                score += Decimal('0.15')
        
        return risk_factors, score
    
    async def _analyze_unusual_trading_patterns_async(self, transactions: List[InvestmentTransaction]) -> Tuple[List[RiskFactor], Decimal]:
        """Analyze unusual trading patterns"""
        risk_factors = []
        score = Decimal('0')
        
        if not transactions:
            return risk_factors, score
        
        # After-hours trading analysis
        after_hours_count = len([
            t for t in transactions 
            if t.transaction_date.hour < 9 or t.transaction_date.hour > 16
        ])
        
        if after_hours_count > len(transactions) * Decimal('0.2'):
            risk_factors.append(RiskFactor(
                type="Excessive After-Hours Trading",
                weight=Decimal('0.2'),
                description=f"{after_hours_count} transactions "
                           f"({after_hours_count * 100 / len(transactions):.1f}%) outside market hours",
                severity=Severity.MEDIUM
            ))
            score += Decimal('0.2')
        
        # Weekend trading analysis
        weekend_count = len([
            t for t in transactions 
            if t.transaction_date.weekday() >= 5  # Saturday = 5, Sunday = 6
        ])
        
        if weekend_count > 5:
            risk_factors.append(RiskFactor(
                type="Weekend Trading Activity",
                weight=Decimal('0.15'),
                description=f"{weekend_count} transactions attempted on weekends",
                severity=Severity.LOW
            ))
            score += Decimal('0.15')
        
        return risk_factors, score
    
    def _analyze_high_risk_securities(
        self, 
        portfolio: InvestmentPortfolio, 
        transactions: List[InvestmentTransaction]
    ) -> Tuple[List[RiskFactor], Decimal]:
        """Analyze high-risk securities"""
        risk_factors = []
        score = Decimal('0')
        
        if not portfolio.holdings:
            return risk_factors, score
        
        # Penny stock analysis
        penny_stock_holdings = [
            h for h in portfolio.holdings 
            if h.current_price < self.PENNY_STOCK_THRESHOLD
        ]
        penny_stock_value = sum(h.market_value for h in penny_stock_holdings)
        penny_stock_percentage = penny_stock_value / portfolio.total_value
        
        if penny_stock_percentage > Decimal('0.1'):
            risk_factors.append(RiskFactor(
                type="High Penny Stock Exposure",
                weight=Decimal('0.25'),
                description=f"Penny stocks represent {penny_stock_percentage:.1%} of portfolio value",
                severity=Severity.MEDIUM
            ))
            score += Decimal('0.25')
        
        # Recent penny stock transactions
        recent_penny_stock_trades = len([
            t for t in transactions 
            if t.price < self.PENNY_STOCK_THRESHOLD
        ])
        if recent_penny_stock_trades > len(transactions) * Decimal('0.3'):
            risk_factors.append(RiskFactor(
                type="Frequent Penny Stock Trading",
                weight=Decimal('0.2'),
                description=f"{recent_penny_stock_trades} recent penny stock transactions",
                severity=Severity.MEDIUM
            ))
            score += Decimal('0.2')
        
        return risk_factors, score
    
    def _analyze_market_timing(self, transactions: List[InvestmentTransaction]) -> Tuple[List[RiskFactor], Decimal]:
        """Analyze market timing patterns"""
        risk_factors = []
        score = Decimal('0')
        
        if not transactions:
            return risk_factors, score
        
        # Analyze transaction timing patterns
        hourly_distribution = {}
        for transaction in transactions:
            hour = transaction.transaction_date.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        # Check for suspicious timing patterns (e.g., all trades at market open/close)
        market_open_trades = hourly_distribution.get(9, 0)
        market_close_trades = hourly_distribution.get(15, 0) + hourly_distribution.get(16, 0)
        total_trades = len(transactions)
        
        if total_trades > 10 and (market_open_trades + market_close_trades) > total_trades * Decimal('0.5'):
            risk_factors.append(RiskFactor(
                type="Suspicious Market Timing",
                weight=Decimal('0.15'),
                description="High concentration of trades at market open/close",
                severity=Severity.LOW
            ))
            score += Decimal('0.15')
        
        return risk_factors, score
    
    # Advanced Pattern Detection Methods
    
    def _detect_pump_and_dump_patterns(self, transactions: List[InvestmentTransaction]) -> List[TradingPattern]:
        """Detect pump and dump patterns"""
        patterns = []
        
        # Group transactions by symbol
        symbol_groups = {}
        for transaction in transactions:
            if transaction.symbol not in symbol_groups:
                symbol_groups[transaction.symbol] = []
            symbol_groups[transaction.symbol].append(transaction)
        
        for symbol, symbol_transactions in symbol_groups.items():
            if len(symbol_transactions) < 5:
                continue
            
            # Sort by date
            symbol_transactions.sort(key=lambda t: t.transaction_date)
            
            # Look for pattern: rapid buying followed by rapid selling
            buy_transactions = [t for t in symbol_transactions if t.transaction_type == TransactionType.BUY]
            sell_transactions = [t for t in symbol_transactions if t.transaction_type == TransactionType.SELL]
            
            if len(buy_transactions) > 3 and len(sell_transactions) > 2:
                first_buy = buy_transactions[0].transaction_date
                last_buy = buy_transactions[-1].transaction_date
                first_sell = sell_transactions[0].transaction_date
                
                # Rapid accumulation followed by rapid disposal
                if (last_buy - first_buy).days < 7 and first_sell > last_buy and (first_sell - last_buy).days < 3:
                    patterns.append(TradingPattern(
                        pattern_type="Potential Pump and Dump",
                        description=f"Rapid accumulation and disposal of {symbol}",
                        confidence=Decimal('0.75'),
                        affected_symbols=[symbol]
                    ))
        
        return patterns
    
    def _detect_wash_trading_patterns(self, transactions: List[InvestmentTransaction]) -> List[TradingPattern]:
        """Detect wash trading patterns"""
        patterns = []
        
        # Group transactions by symbol
        symbol_groups = {}
        for transaction in transactions:
            if transaction.symbol not in symbol_groups:
                symbol_groups[transaction.symbol] = []
            symbol_groups[transaction.symbol].append(transaction)
        
        for symbol, symbol_transactions in symbol_groups.items():
            symbol_transactions.sort(key=lambda t: t.transaction_date)
            wash_trading_count = 0
            
            for i in range(len(symbol_transactions) - 2):
                t1 = symbol_transactions[i]
                t2 = symbol_transactions[i + 1]
                t3 = symbol_transactions[i + 2]
                
                # Pattern: BUY -> SELL -> BUY within short timeframe with similar quantities
                if (t1.transaction_type == TransactionType.BUY and 
                    t2.transaction_type == TransactionType.SELL and 
                    t3.transaction_type == TransactionType.BUY):
                    
                    time_span = t3.transaction_date - t1.transaction_date
                    quantity_similarity = abs(t1.quantity - t3.quantity) / max(t1.quantity, t3.quantity)
                    
                    if time_span.total_seconds() < 24 * 3600 and quantity_similarity < Decimal('0.1'):
                        wash_trading_count += 1
            
            if wash_trading_count > 2:
                patterns.append(TradingPattern(
                    pattern_type="Potential Wash Trading",
                    description=f"Detected {wash_trading_count} wash trading sequences in {symbol}",
                    confidence=Decimal('0.8'),
                    affected_symbols=[symbol]
                ))
        
        return patterns
    
    def _detect_layering_patterns(self, transactions: List[InvestmentTransaction]) -> List[TradingPattern]:
        """Detect layering/spoofing patterns"""
        patterns = []
        
        # Group transactions by symbol
        symbol_groups = {}
        for transaction in transactions:
            if transaction.symbol not in symbol_groups:
                symbol_groups[transaction.symbol] = []
            symbol_groups[transaction.symbol].append(transaction)
        
        for symbol, symbol_transactions in symbol_groups.items():
            if len(symbol_transactions) <= 10:
                continue
            
            recent_transactions = [
                t for t in symbol_transactions 
                if t.transaction_date > datetime.utcnow() - timedelta(days=7)
            ]
            rapid_transaction_count = 0
            
            # Look for clusters of transactions within short time periods
            for i in range(len(recent_transactions) - 3):
                time_window = recent_transactions[i:i+4]
                time_span = time_window[-1].transaction_date - time_window[0].transaction_date
                
                if time_span.total_seconds() < 30 * 60:  # 30 minutes
                    rapid_transaction_count += 1
            
            if rapid_transaction_count > 3:
                patterns.append(TradingPattern(
                    pattern_type="Potential Layering/Spoofing",
                    description=f"Rapid order activity detected in {symbol}",
                    confidence=Decimal('0.65'),
                    affected_symbols=[symbol]
                ))
        
        return patterns
    
    def _detect_insider_trading_indicators(self, transactions: List[InvestmentTransaction]) -> List[TradingPattern]:
        """Detect insider trading indicators"""
        patterns = []
        
        # Look for unusual trading activity before typical announcement periods
        suspicious_transactions = [
            t for t in transactions
            if (t.transaction_date.weekday() == 4 and t.transaction_date.hour >= 15) or  # Friday after 3 PM
               (t.transaction_date.weekday() == 0 and t.transaction_date.hour <= 10)   # Monday before 10 AM
        ]
        
        if len(suspicious_transactions) > len(transactions) * Decimal('0.15'):
            affected_symbols = list(set(t.symbol for t in suspicious_transactions))
            patterns.append(TradingPattern(
                pattern_type="Potential Insider Trading",
                description="Unusual trading activity during typical announcement periods",
                confidence=Decimal('0.55'),
                affected_symbols=affected_symbols
            ))
        
        return patterns
    
    def _detect_market_manipulation_patterns(self, transactions: List[InvestmentTransaction]) -> List[TradingPattern]:
        """Detect market manipulation patterns"""
        patterns = []
        
        # Detect coordinated trading patterns across multiple symbols
        daily_transactions = {}
        for transaction in transactions:
            date = transaction.transaction_date.date()
            if date not in daily_transactions:
                daily_transactions[date] = []
            daily_transactions[date].append(transaction)
        
        for date, day_transactions in daily_transactions.items():
            if len(day_transactions) > 20:
                symbols_traded = len(set(t.symbol for t in day_transactions))
                total_value = sum(t.amount for t in day_transactions)
                
                # High volume across many symbols in single day
                if symbols_traded > 15 and total_value > Decimal('100000'):
                    patterns.append(TradingPattern(
                        pattern_type="Potential Market Manipulation",
                        description=f"High volume coordinated trading across {symbols_traded} symbols",
                        confidence=Decimal('0.6'),
                        affected_symbols=list(set(t.symbol for t in day_transactions))
                    ))
        
        return patterns
    
    # Helper Methods
    
    def _get_risk_level(self, risk_score: Decimal) -> RiskLevel:
        """Get risk level from score"""
        if risk_score >= Decimal('0.8'):
            return RiskLevel.CRITICAL
        elif risk_score >= Decimal('0.6'):
            return RiskLevel.HIGH
        elif risk_score >= Decimal('0.3'):
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(self, risk_factors: List[RiskFactor], risk_score: Decimal) -> List[str]:
        """Generate recommendations based on risk factors"""
        recommendations = []
        
        if risk_score >= self.HIGH_RISK_THRESHOLD:
            recommendations.extend([
                "Immediate review of trading activity required",
                "Consider implementing trading limits",
                "Enhanced monitoring for suspicious patterns"
            ])
        elif risk_score >= self.MEDIUM_RISK_THRESHOLD:
            recommendations.extend([
                "Monitor trading activity closely",
                "Review portfolio concentration",
                "Consider diversification strategies"
            ])
        else:
            recommendations.extend([
                "Current risk level acceptable",
                "Continue regular monitoring"
            ])
        
        # Specific recommendations based on risk factors
        if any(rf.type.find("Concentration") != -1 for rf in risk_factors):
            recommendations.append("Diversify portfolio holdings across sectors and asset types")
        
        if any(rf.type.find("Velocity") != -1 or rf.type.find("Trading") != -1 for rf in risk_factors):
            recommendations.append("Implement cooling-off periods between trades")
        
        if any(rf.type.find("Penny Stock") != -1 for rf in risk_factors):
            recommendations.append("Limit exposure to high-risk securities")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_sector_from_symbol(self, symbol: str) -> str:
        """Get sector from symbol (simplified mapping)"""
        sector_mapping = {
            "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", "NVDA": "Technology",
            "JPM": "Financial", "BAC": "Financial", "WFC": "Financial",
            "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare",
            "XOM": "Energy", "CVX": "Energy",
            "SPY": "ETF", "QQQ": "ETF", "VTI": "ETF"
        }
        return sector_mapping.get(symbol, "Other")
    
    # Mock Data Methods (replace with real API calls)
    
    async def _get_user_portfolio_async(self, user_id: str) -> InvestmentPortfolio:
        """Mock method to get user portfolio"""
        # In real implementation, this would call the investment API
        return InvestmentPortfolio(
            user_id=user_id,
            portfolio_id=f"portfolio_{user_id}",
            total_value=Decimal('100000'),
            total_gain_loss=Decimal('5000'),
            daily_change=Decimal('1000'),
            daily_change_percentage=Decimal('0.01'),
            holdings=[
                InvestmentHolding(
                    symbol="AAPL",
                    name="Apple Inc.",
                    quantity=100,
                    current_price=Decimal('150.00'),
                    market_value=Decimal('15000'),
                    cost_basis=Decimal('14000'),
                    gain_loss=Decimal('1000'),
                    gain_loss_percentage=Decimal('0.071'),
                    asset_type="STOCK"
                )
            ]
        )
    
    async def _get_investment_transactions_async(self, user_id: str, days: int) -> List[InvestmentTransaction]:
        """Mock method to get investment transactions"""
        # In real implementation, this would call the investment API
        transactions = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(min(days, 20)):  # Generate up to 20 transactions
            transactions.append(InvestmentTransaction(
                transaction_id=f"txn_{user_id}_{i}",
                user_id=user_id,
                symbol="AAPL",
                transaction_type=TransactionType.BUY if i % 2 == 0 else TransactionType.SELL,
                quantity=10 + i,
                price=Decimal('150.00') + Decimal(str(i)),
                amount=Decimal('1500.00') + Decimal(str(i * 10)),
                transaction_date=base_date + timedelta(days=i),
                platform="api"
            ))
        
        return transactions
