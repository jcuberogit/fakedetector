"""
Data Quality Service
ML-ready data validation and monitoring
Python equivalent of C# DataQualityService
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataQualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class ValidationRule(Enum):
    """Validation rules"""
    REQUIRED = "required"
    UNIQUE = "unique"
    RANGE = "range"
    FORMAT = "format"
    PATTERN = "pattern"
    REFERENCE = "reference"

@dataclass
class FieldValidationResult:
    """Field validation result"""
    field_name: str
    rule: ValidationRule
    passed: bool
    value: Any
    expected: Any
    message: str
    severity: str = "info"

@dataclass
class DataQualityMetrics:
    """Data quality metrics"""
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    validity_score: float
    uniqueness_score: float
    overall_score: float
    quality_level: DataQualityLevel
    total_records: int
    valid_records: int
    invalid_records: int
    missing_fields: int
    duplicate_records: int
    validation_errors: List[FieldValidationResult]
    timestamp: datetime

@dataclass
class DataQualityTrend:
    """Data quality trend over time"""
    date: datetime
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    validity_score: float
    overall_score: float
    record_count: int

@dataclass
class DataQualityAlert:
    """Data quality alert"""
    alert_id: str
    field_name: str
    alert_type: str
    severity: str
    message: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False

class DataQualityService:
    """
    Data Quality Service for ML-ready data validation and monitoring
    
    Python equivalent of C# DataQualityService with comprehensive data validation,
    quality scoring, trend analysis, and alerting capabilities.
    """
    
    def __init__(self):
        self.validation_rules: Dict[str, List[Dict[str, Any]]] = {}
        self.quality_thresholds = {
            'completeness': 0.85,  # 85% threshold
            'accuracy': 0.90,      # 90% threshold
            'consistency': 0.80,
            'validity': 0.85,
            'uniqueness': 0.95
        }
        self.quality_history: List[DataQualityTrend] = []
        self.active_alerts: List[DataQualityAlert] = []
        
        # Initialize default validation rules
        self._initialize_default_rules()
        
        logger.info("Data Quality Service initialized")
    
    def _initialize_default_rules(self):
        """Initialize default validation rules"""
        self.validation_rules = {
            'transaction_id': [
                {'rule': ValidationRule.REQUIRED, 'message': 'Transaction ID is required'},
                {'rule': ValidationRule.UNIQUE, 'message': 'Transaction ID must be unique'},
                {'rule': ValidationRule.FORMAT, 'pattern': r'^[A-Za-z0-9_-]+$', 'message': 'Invalid transaction ID format'}
            ],
            'user_id': [
                {'rule': ValidationRule.REQUIRED, 'message': 'User ID is required'},
                {'rule': ValidationRule.FORMAT, 'pattern': r'^[A-Za-z0-9_-]+$', 'message': 'Invalid user ID format'}
            ],
            'amount': [
                {'rule': ValidationRule.REQUIRED, 'message': 'Amount is required'},
                {'rule': ValidationRule.RANGE, 'min': 0.01, 'max': 1000000, 'message': 'Amount must be between 0.01 and 1,000,000'},
                {'rule': ValidationRule.FORMAT, 'type': 'numeric', 'message': 'Amount must be numeric'}
            ],
            'merchant_name': [
                {'rule': ValidationRule.REQUIRED, 'message': 'Merchant name is required'},
                {'rule': ValidationRule.FORMAT, 'min_length': 2, 'max_length': 100, 'message': 'Merchant name must be 2-100 characters'}
            ],
            'location': [
                {'rule': ValidationRule.FORMAT, 'pattern': r'^[A-Za-z\s,.-]+$', 'message': 'Invalid location format'}
            ],
            'ip_address': [
                {'rule': ValidationRule.FORMAT, 'pattern': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', 'message': 'Invalid IP address format'}
            ],
            'email': [
                {'rule': ValidationRule.FORMAT, 'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', 'message': 'Invalid email format'}
            ],
            'phone': [
                {'rule': ValidationRule.FORMAT, 'pattern': r'^\+?[\d\s\-\(\)]+$', 'message': 'Invalid phone format'}
            ]
        }
    
    async def validate_data(self, data: List[Dict[str, Any]], 
                          schema: Optional[Dict[str, Any]] = None) -> DataQualityMetrics:
        """Validate data and return quality metrics"""
        try:
            if not data:
                return self._create_empty_metrics()
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(data)
            
            # Calculate individual quality scores
            completeness_score = await self._calculate_completeness_score(df)
            accuracy_score = await self._calculate_accuracy_score(df)
            consistency_score = await self._calculate_consistency_score(df)
            validity_score = await self._calculate_validity_score(df, schema)
            uniqueness_score = await self._calculate_uniqueness_score(df)
            
            # Calculate overall score
            overall_score = (
                completeness_score * 0.25 +
                accuracy_score * 0.25 +
                consistency_score * 0.20 +
                validity_score * 0.20 +
                uniqueness_score * 0.10
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Count records
            total_records = len(df)
            valid_records = int(total_records * validity_score)
            invalid_records = total_records - valid_records
            
            # Count missing fields
            missing_fields = df.isnull().sum().sum()
            
            # Count duplicates
            duplicate_records = df.duplicated().sum()
            
            # Generate validation errors
            validation_errors = await self._generate_validation_errors(df, schema)
            
            metrics = DataQualityMetrics(
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                validity_score=validity_score,
                uniqueness_score=uniqueness_score,
                overall_score=overall_score,
                quality_level=quality_level,
                total_records=total_records,
                valid_records=valid_records,
                invalid_records=invalid_records,
                missing_fields=missing_fields,
                duplicate_records=duplicate_records,
                validation_errors=validation_errors,
                timestamp=datetime.utcnow()
            )
            
            # Store trend data
            await self._store_quality_trend(metrics)
            
            # Check for alerts
            await self._check_quality_alerts(metrics)
            
            logger.info(f"Data quality analysis completed: {overall_score:.2%} overall score")
            return metrics
            
        except (ValueError) as e:
            logger.error(f"Failed to validate data: {e}")
            return self._create_empty_metrics()
    
    async def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """Calculate completeness score"""
        try:
            total_cells = df.size
            missing_cells = df.isnull().sum().sum()
            completeness = (total_cells - missing_cells) / total_cells
            return max(0.0, min(1.0, completeness))
        except Exception:
            return 0.0
    
    async def _calculate_accuracy_score(self, df: pd.DataFrame) -> float:
        """Calculate accuracy score based on data format validation"""
        try:
            accuracy_checks = 0
            passed_checks = 0
            
            for column in df.columns:
                if column in self.validation_rules:
                    rules = self.validation_rules[column]
                    for rule_config in rules:
                        rule = rule_config['rule']
                        accuracy_checks += 1
                        
                        if rule == ValidationRule.FORMAT:
                            if 'type' in rule_config and rule_config['type'] == 'numeric':
                                # Check if column is numeric
                                if pd.api.types.is_numeric_dtype(df[column]):
                                    passed_checks += 1
                            elif 'pattern' in rule_config:
                                # Check pattern matching
                                pattern = rule_config['pattern']
                                valid_count = df[column].astype(str).str.match(pattern, na=False).sum()
                                if valid_count > 0:
                                    passed_checks += 1
            
            return passed_checks / accuracy_checks if accuracy_checks > 0 else 1.0
        except Exception:
            return 0.0
    
    async def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate consistency score"""
        try:
            consistency_checks = 0
            passed_checks = 0
            
            # Check data type consistency
            for column in df.columns:
                if df[column].dtype == 'object':
                    # Check if all values follow same format
                    sample_values = df[column].dropna().head(10)
                    if len(sample_values) > 0:
                        consistency_checks += 1
                        # Simple consistency check - all values have similar length
                        lengths = sample_values.astype(str).str.len()
                        if lengths.std() < lengths.mean() * 0.5:  # Low variance in length
                            passed_checks += 1
            
            return passed_checks / consistency_checks if consistency_checks > 0 else 1.0
        except Exception:
            return 0.0
    
    async def _calculate_validity_score(self, df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> float:
        """Calculate validity score based on validation rules"""
        try:
            total_validations = 0
            passed_validations = 0
            
            for column in df.columns:
                if column in self.validation_rules:
                    rules = self.validation_rules[column]
                    for rule_config in rules:
                        rule = rule_config['rule']
                        total_validations += len(df)
                        
                        if rule == ValidationRule.REQUIRED:
                            passed_validations += df[column].notna().sum()
                        elif rule == ValidationRule.UNIQUE:
                            passed_validations += len(df) - df[column].duplicated().sum()
                        elif rule == ValidationRule.RANGE:
                            if 'min' in rule_config and 'max' in rule_config:
                                min_val = rule_config['min']
                                max_val = rule_config['max']
                                passed_validations += df[column].between(min_val, max_val, inclusive='both').sum()
                        elif rule == ValidationRule.FORMAT:
                            if 'pattern' in rule_config:
                                pattern = rule_config['pattern']
                                passed_validations += df[column].astype(str).str.match(pattern, na=False).sum()
            
            return passed_validations / total_validations if total_validations > 0 else 1.0
        except Exception:
            return 0.0
    
    async def _calculate_uniqueness_score(self, df: pd.DataFrame) -> float:
        """Calculate uniqueness score"""
        try:
            total_records = len(df)
            if total_records == 0:
                return 1.0
            
            # Check for duplicate rows
            duplicate_count = df.duplicated().sum()
            uniqueness = (total_records - duplicate_count) / total_records
            
            return max(0.0, min(1.0, uniqueness))
        except Exception:
            return 0.0
    
    def _determine_quality_level(self, score: float) -> DataQualityLevel:
        """Determine quality level based on score"""
        if score >= 0.95:
            return DataQualityLevel.EXCELLENT
        elif score >= 0.85:
            return DataQualityLevel.GOOD
        elif score >= 0.70:
            return DataQualityLevel.FAIR
        elif score >= 0.50:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
    
    async def _generate_validation_errors(self, df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> List[FieldValidationResult]:
        """Generate detailed validation errors"""
        errors = []
        
        try:
            for column in df.columns:
                if column in self.validation_rules:
                    rules = self.validation_rules[column]
                    for rule_config in rules:
                        rule = rule_config['rule']
                        
                        if rule == ValidationRule.REQUIRED:
                            missing_count = df[column].isnull().sum()
                            if missing_count > 0:
                                errors.append(FieldValidationResult(
                                    field_name=column,
                                    rule=rule,
                                    passed=False,
                                    value=None,
                                    expected="Non-null value",
                                    message=f"{missing_count} missing values in {column}",
                                    severity="error"
                                ))
                        
                        elif rule == ValidationRule.UNIQUE:
                            duplicate_count = df[column].duplicated().sum()
                            if duplicate_count > 0:
                                errors.append(FieldValidationResult(
                                    field_name=column,
                                    rule=rule,
                                    passed=False,
                                    value=f"{duplicate_count} duplicates",
                                    expected="Unique values",
                                    message=f"{duplicate_count} duplicate values in {column}",
                                    severity="warning"
                                ))
                        
                        elif rule == ValidationRule.RANGE:
                            if 'min' in rule_config and 'max' in rule_config:
                                min_val = rule_config['min']
                                max_val = rule_config['max']
                                invalid_count = (~df[column].between(min_val, max_val, inclusive='both')).sum()
                                if invalid_count > 0:
                                    errors.append(FieldValidationResult(
                                        field_name=column,
                                        rule=rule,
                                        passed=False,
                                        value=f"{invalid_count} out of range",
                                        expected=f"Between {min_val} and {max_val}",
                                        message=f"{invalid_count} values out of range in {column}",
                                        severity="error"
                                    ))
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to generate validation errors: {e}")
        
        return errors
    
    async def _store_quality_trend(self, metrics: DataQualityMetrics):
        """Store quality trend data"""
        try:
            trend = DataQualityTrend(
                date=metrics.timestamp,
                completeness_score=metrics.completeness_score,
                accuracy_score=metrics.accuracy_score,
                consistency_score=metrics.consistency_score,
                validity_score=metrics.validity_score,
                overall_score=metrics.overall_score,
                record_count=metrics.total_records
            )
            
            self.quality_history.append(trend)
            
            # Keep only last 30 days of history
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            self.quality_history = [t for t in self.quality_history if t.date >= cutoff_date]
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to store quality trend: {e}")
    
    async def _check_quality_alerts(self, metrics: DataQualityMetrics):
        """Check for quality alerts"""
        try:
            # Check completeness threshold
            if metrics.completeness_score < self.quality_thresholds['completeness']:
                await self._create_alert(
                    field_name="completeness",
                    alert_type="threshold_breach",
                    severity="warning",
                    message=f"Completeness score {metrics.completeness_score:.2%} below threshold {self.quality_thresholds['completeness']:.2%}",
                    threshold=self.quality_thresholds['completeness'],
                    current_value=metrics.completeness_score
                )
            
            # Check accuracy threshold
            if metrics.accuracy_score < self.quality_thresholds['accuracy']:
                await self._create_alert(
                    field_name="accuracy",
                    alert_type="threshold_breach",
                    severity="error",
                    message=f"Accuracy score {metrics.accuracy_score:.2%} below threshold {self.quality_thresholds['accuracy']:.2%}",
                    threshold=self.quality_thresholds['accuracy'],
                    current_value=metrics.accuracy_score
                )
            
            # Check overall score
            if metrics.overall_score < 0.70:
                await self._create_alert(
                    field_name="overall",
                    alert_type="critical_quality",
                    severity="critical",
                    message=f"Overall quality score {metrics.overall_score:.2%} is critically low",
                    threshold=0.70,
                    current_value=metrics.overall_score
                )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to check quality alerts: {e}")
    
    async def _create_alert(self, field_name: str, alert_type: str, severity: str, 
                          message: str, threshold: float, current_value: float):
        """Create a quality alert"""
        try:
            alert = DataQualityAlert(
                alert_id=f"dq_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{field_name}",
                field_name=field_name,
                alert_type=alert_type,
                severity=severity,
                message=message,
                threshold=threshold,
                current_value=current_value,
                timestamp=datetime.utcnow()
            )
            
            self.active_alerts.append(alert)
            logger.warning(f"Data quality alert: {message}")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def get_quality_trends(self, days: int = 7) -> List[DataQualityTrend]:
        """Get quality trends for specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return [t for t in self.quality_history if t.date >= cutoff_date]
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get quality trends: {e}")
            return []
    
    async def get_active_alerts(self) -> List[DataQualityAlert]:
        """Get active quality alerts"""
        try:
            return [a for a in self.active_alerts if not a.resolved]
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a quality alert"""
        try:
            for alert in self.active_alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    logger.info(f"Alert {alert_id} resolved")
                    return True
            return False
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False
    
    async def batch_quality_analysis(self, data_batches: List[List[Dict[str, Any]]]) -> List[DataQualityMetrics]:
        """Perform batch quality analysis"""
        try:
            results = []
            for batch in data_batches:
                metrics = await self.validate_data(batch)
                results.append(metrics)
            
            logger.info(f"Batch quality analysis completed for {len(data_batches)} batches")
            return results
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to perform batch quality analysis: {e}")
            return []
    
    def _create_empty_metrics(self) -> DataQualityMetrics:
        """Create empty metrics for error cases"""
        return DataQualityMetrics(
            completeness_score=0.0,
            accuracy_score=0.0,
            consistency_score=0.0,
            validity_score=0.0,
            uniqueness_score=0.0,
            overall_score=0.0,
            quality_level=DataQualityLevel.CRITICAL,
            total_records=0,
            valid_records=0,
            invalid_records=0,
            missing_fields=0,
            duplicate_records=0,
            validation_errors=[],
            timestamp=datetime.utcnow()
        )
    
    async def get_quality_summary(self) -> Dict[str, Any]:
        """Get overall quality summary"""
        try:
            recent_trends = await self.get_quality_trends(days=7)
            active_alerts = await self.get_active_alerts()
            
            if recent_trends:
                latest_trend = recent_trends[-1]
                avg_score = sum(t.overall_score for t in recent_trends) / len(recent_trends)
            else:
                latest_trend = None
                avg_score = 0.0
            
            return {
                'current_score': latest_trend.overall_score if latest_trend else 0.0,
                'average_score_7d': avg_score,
                'quality_level': latest_trend.quality_level.value if latest_trend else 'unknown',
                'active_alerts': len(active_alerts),
                'critical_alerts': len([a for a in active_alerts if a.severity == 'critical']),
                'trend_direction': self._calculate_trend_direction(recent_trends),
                'last_analysis': latest_trend.date.isoformat() if latest_trend else None
            }
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get quality summary: {e}")
            return {}
    
    def _calculate_trend_direction(self, trends: List[DataQualityTrend]) -> str:
        """Calculate trend direction"""
        try:
            if len(trends) < 2:
                return "insufficient_data"
            
            recent_scores = [t.overall_score for t in trends[-5:]]  # Last 5 data points
            if len(recent_scores) < 2:
                return "insufficient_data"
            
            # Simple trend calculation
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 0.05:
                return "improving"
            elif second_avg < first_avg - 0.05:
                return "declining"
            else:
                return "stable"
                
        except Exception:
            return "unknown"


# Global data quality service instance
data_quality_service = DataQualityService()
