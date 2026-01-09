"""
Feature Engineering Service
Automated feature extraction and selection
Python equivalent of C# FeatureEngineeringService
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import statistics

logger = logging.getLogger(__name__)

class FeatureType(Enum):
    """Feature types"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    TIME_SERIES = "time_series"
    TEXT = "text"
    DERIVED = "derived"

class FeatureImportance(Enum):
    """Feature importance levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IRRELEVANT = "irrelevant"

@dataclass
class FeatureDefinition:
    """Feature definition"""
    name: str
    feature_type: FeatureType
    importance: FeatureImportance
    description: str
    source_columns: List[str]
    transformation: str
    validation_rules: List[str]
    created_at: datetime

@dataclass
class FeatureEngineeringResult:
    """Feature engineering result"""
    original_features: int
    engineered_features: int
    total_features: int
    feature_definitions: List[FeatureDefinition]
    feature_importance_scores: Dict[str, float]
    feature_correlation_matrix: Dict[str, Dict[str, float]]
    processing_time: float
    created_at: datetime

@dataclass
class FeatureSelectionResult:
    """Feature selection result"""
    selected_features: List[str]
    feature_scores: Dict[str, float]
    selection_method: str
    k_best: int
    total_features_before: int
    total_features_after: int
    processing_time: float

class FeatureEngineeringService:
    """
    Feature Engineering Service
    
    Automated feature extraction, transformation, and selection for fraud detection.
    Includes statistical features, time-based features, behavioral patterns, and
    advanced feature selection techniques.
    """
    
    def __init__(self):
        self.feature_definitions: Dict[str, FeatureDefinition] = {}
        self.feature_scalers: Dict[str, Any] = {}
        self.feature_encoders: Dict[str, Any] = {}
        self.feature_history: List[FeatureEngineeringResult] = []
        
        # Initialize default feature definitions
        self._initialize_default_features()
        
        logger.info("Feature Engineering Service initialized")
    
    def _initialize_default_features(self):
        """Initialize default feature definitions"""
        default_features = [
            FeatureDefinition(
                name="amount_log",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Logarithmic transformation of transaction amount",
                source_columns=["amount"],
                transformation="log(amount + 1)",
                validation_rules=["amount >= 0"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="amount_zscore",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Z-score normalized transaction amount",
                source_columns=["amount"],
                transformation="(amount - mean(amount)) / std(amount)",
                validation_rules=["amount is numeric"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="hour_of_day",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Hour of day extracted from timestamp",
                source_columns=["timestamp"],
                transformation="extract_hour(timestamp)",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="day_of_week",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Day of week extracted from timestamp",
                source_columns=["timestamp"],
                transformation="extract_dow(timestamp)",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="is_weekend",
                feature_type=FeatureType.BINARY,
                importance=FeatureImportance.MEDIUM,
                description="Binary indicator for weekend transactions",
                source_columns=["timestamp"],
                transformation="is_weekend(timestamp)",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="is_night_time",
                feature_type=FeatureType.BINARY,
                importance=FeatureImportance.MEDIUM,
                description="Binary indicator for night time transactions (10 PM - 6 AM)",
                source_columns=["timestamp"],
                transformation="is_night_time(timestamp)",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="merchant_frequency",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Frequency of transactions with same merchant",
                source_columns=["merchant_name", "user_id"],
                transformation="count(merchant_name) per user_id",
                validation_rules=["merchant_name is not null"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="location_frequency",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Frequency of transactions from same location",
                source_columns=["location", "user_id"],
                transformation="count(location) per user_id",
                validation_rules=["location is not null"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="velocity_1h",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Transaction velocity in last 1 hour",
                source_columns=["timestamp", "user_id"],
                transformation="count(transactions) in last 1 hour per user_id",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="velocity_24h",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Transaction velocity in last 24 hours",
                source_columns=["timestamp", "user_id"],
                transformation="count(transactions) in last 24 hours per user_id",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="amount_velocity_1h",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Amount velocity in last 1 hour",
                source_columns=["amount", "timestamp", "user_id"],
                transformation="sum(amount) in last 1 hour per user_id",
                validation_rules=["amount is numeric", "timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="amount_velocity_24h",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Amount velocity in last 24 hours",
                source_columns=["amount", "timestamp", "user_id"],
                transformation="sum(amount) in last 24 hours per user_id",
                validation_rules=["amount is numeric", "timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="avg_amount_7d",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Average transaction amount in last 7 days",
                source_columns=["amount", "timestamp", "user_id"],
                transformation="mean(amount) in last 7 days per user_id",
                validation_rules=["amount is numeric", "timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="max_amount_30d",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Maximum transaction amount in last 30 days",
                source_columns=["amount", "timestamp", "user_id"],
                transformation="max(amount) in last 30 days per user_id",
                validation_rules=["amount is numeric", "timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="transaction_gap",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Time gap since last transaction",
                source_columns=["timestamp", "user_id"],
                transformation="time_since_last_transaction per user_id",
                validation_rules=["timestamp is datetime"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="merchant_category_risk",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="Risk score based on merchant category",
                source_columns=["merchant_category"],
                transformation="merchant_category_risk_score(merchant_category)",
                validation_rules=["merchant_category is not null"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="location_risk",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Risk score based on transaction location",
                source_columns=["location"],
                transformation="location_risk_score(location)",
                validation_rules=["location is not null"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="device_trust_score",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="Trust score based on device history",
                source_columns=["device_id", "user_id"],
                transformation="device_trust_score(device_id, user_id)",
                validation_rules=["device_id is not null"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="ip_reputation_score",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.MEDIUM,
                description="IP reputation score",
                source_columns=["ip_address"],
                transformation="ip_reputation_score(ip_address)",
                validation_rules=["ip_address is valid IP"],
                created_at=datetime.utcnow()
            ),
            FeatureDefinition(
                name="user_behavior_score",
                feature_type=FeatureType.DERIVED,
                importance=FeatureImportance.HIGH,
                description="User behavior anomaly score",
                source_columns=["amount", "merchant_name", "location", "timestamp", "user_id"],
                transformation="user_behavior_anomaly_score(user_id)",
                validation_rules=["all required fields present"],
                created_at=datetime.utcnow()
            )
        ]
        
        for feature in default_features:
            self.feature_definitions[feature.name] = feature
    
    async def engineer_features(self, data: List[Dict[str, Any]], 
                              target_column: str = "is_fraud") -> FeatureEngineeringResult:
        """Engineer features from raw data"""
        try:
            start_time = time.time()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            original_features = len(df.columns)
            
            logger.info(f"Starting feature engineering for {len(df)} records")
            
            # Apply feature transformations
            engineered_df = await self._apply_feature_transformations(df)
            
            # Calculate feature importance
            feature_importance_scores = await self._calculate_feature_importance(
                engineered_df, target_column
            )
            
            # Calculate feature correlations
            feature_correlation_matrix = await self._calculate_feature_correlations(engineered_df)
            
            # Create feature definitions for new features
            new_feature_definitions = await self._create_feature_definitions(
                engineered_df, original_features
            )
            
            processing_time = time.time() - start_time
            
            result = FeatureEngineeringResult(
                original_features=original_features,
                engineered_features=len(engineered_df.columns) - original_features,
                total_features=len(engineered_df.columns),
                feature_definitions=new_feature_definitions,
                feature_importance_scores=feature_importance_scores,
                feature_correlation_matrix=feature_correlation_matrix,
                processing_time=processing_time,
                created_at=datetime.utcnow()
            )
            
            # Store result
            self.feature_history.append(result)
            
            logger.info(f"Feature engineering completed: {len(engineered_df.columns)} total features")
            return result
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to engineer features: {e}")
            raise
    
    async def _apply_feature_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply feature transformations"""
        try:
            engineered_df = df.copy()
            
            # Convert timestamp to datetime if it's a string
            if 'timestamp' in engineered_df.columns:
                if engineered_df['timestamp'].dtype == 'object':
                    engineered_df['timestamp'] = pd.to_datetime(engineered_df['timestamp'])
            
            # Apply each feature transformation
            for feature_name, feature_def in self.feature_definitions.items():
                try:
                    if feature_name == "amount_log" and "amount" in engineered_df.columns:
                        engineered_df[feature_name] = np.log1p(engineered_df["amount"])
                    
                    elif feature_name == "amount_zscore" and "amount" in engineered_df.columns:
                        mean_amount = engineered_df["amount"].mean()
                        std_amount = engineered_df["amount"].std()
                        engineered_df[feature_name] = (engineered_df["amount"] - mean_amount) / std_amount
                    
                    elif feature_name == "hour_of_day" and "timestamp" in engineered_df.columns:
                        engineered_df[feature_name] = engineered_df["timestamp"].dt.hour
                    
                    elif feature_name == "day_of_week" and "timestamp" in engineered_df.columns:
                        engineered_df[feature_name] = engineered_df["timestamp"].dt.dayofweek
                    
                    elif feature_name == "is_weekend" and "timestamp" in engineered_df.columns:
                        engineered_df[feature_name] = engineered_df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
                    
                    elif feature_name == "is_night_time" and "timestamp" in engineered_df.columns:
                        hour = engineered_df["timestamp"].dt.hour
                        engineered_df[feature_name] = ((hour >= 22) | (hour <= 6)).astype(int)
                    
                    elif feature_name == "merchant_frequency" and "merchant_name" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = engineered_df.groupby("user_id")["merchant_name"].transform("count")
                    
                    elif feature_name == "location_frequency" and "location" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = engineered_df.groupby("user_id")["location"].transform("count")
                    
                    elif feature_name == "velocity_1h" and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_velocity(
                            engineered_df, "user_id", "timestamp", hours=1
                        )
                    
                    elif feature_name == "velocity_24h" and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_velocity(
                            engineered_df, "user_id", "timestamp", hours=24
                        )
                    
                    elif feature_name == "amount_velocity_1h" and "amount" in engineered_df.columns and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_amount_velocity(
                            engineered_df, "user_id", "amount", "timestamp", hours=1
                        )
                    
                    elif feature_name == "amount_velocity_24h" and "amount" in engineered_df.columns and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_amount_velocity(
                            engineered_df, "user_id", "amount", "timestamp", hours=24
                        )
                    
                    elif feature_name == "avg_amount_7d" and "amount" in engineered_df.columns and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_rolling_statistic(
                            engineered_df, "user_id", "amount", "timestamp", days=7, stat="mean"
                        )
                    
                    elif feature_name == "max_amount_30d" and "amount" in engineered_df.columns and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_rolling_statistic(
                            engineered_df, "user_id", "amount", "timestamp", days=30, stat="max"
                        )
                    
                    elif feature_name == "transaction_gap" and "timestamp" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_transaction_gap(
                            engineered_df, "user_id", "timestamp"
                        )
                    
                    elif feature_name == "merchant_category_risk" and "merchant_category" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_merchant_category_risk(
                            engineered_df["merchant_category"]
                        )
                    
                    elif feature_name == "location_risk" and "location" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_location_risk(
                            engineered_df["location"]
                        )
                    
                    elif feature_name == "device_trust_score" and "device_id" in engineered_df.columns and "user_id" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_device_trust_score(
                            engineered_df, "device_id", "user_id"
                        )
                    
                    elif feature_name == "ip_reputation_score" and "ip_address" in engineered_df.columns:
                        engineered_df[feature_name] = await self._calculate_ip_reputation_score(
                            engineered_df["ip_address"]
                        )
                    
                    elif feature_name == "user_behavior_score" and all(col in engineered_df.columns for col in ["amount", "merchant_name", "location", "timestamp", "user_id"]):
                        engineered_df[feature_name] = await self._calculate_user_behavior_score(
                            engineered_df
                        )
                
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Failed to create feature {feature_name}: {e}")
                    continue
            
            # Fill NaN values
            engineered_df = engineered_df.fillna(0)
            
            return engineered_df
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to apply feature transformations: {e}")
            raise
    
    async def _calculate_velocity(self, df: pd.DataFrame, group_col: str, 
                                time_col: str, hours: int) -> pd.Series:
        """Calculate transaction velocity"""
        try:
            velocity = pd.Series(0, index=df.index)
            
            for user_id in df[group_col].unique():
                user_mask = df[group_col] == user_id
                user_data = df[user_mask].copy()
                user_data = user_data.sort_values(time_col)
                
                for i, row in user_data.iterrows():
                    time_window = row[time_col] - pd.Timedelta(hours=hours)
                    count = len(user_data[user_data[time_col] > time_window])
                    velocity.loc[i] = count
            
            return velocity
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate velocity: {e}")
            return pd.Series(0, index=df.index)
    
    async def _calculate_amount_velocity(self, df: pd.DataFrame, group_col: str, 
                                       amount_col: str, time_col: str, hours: int) -> pd.Series:
        """Calculate amount velocity"""
        try:
            amount_velocity = pd.Series(0, index=df.index)
            
            for user_id in df[group_col].unique():
                user_mask = df[group_col] == user_id
                user_data = df[user_mask].copy()
                user_data = user_data.sort_values(time_col)
                
                for i, row in user_data.iterrows():
                    time_window = row[time_col] - pd.Timedelta(hours=hours)
                    amount_sum = user_data[user_data[time_col] > time_window][amount_col].sum()
                    amount_velocity.loc[i] = amount_sum
            
            return amount_velocity
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate amount velocity: {e}")
            return pd.Series(0, index=df.index)
    
    async def _calculate_rolling_statistic(self, df: pd.DataFrame, group_col: str, 
                                         value_col: str, time_col: str, 
                                         days: int, stat: str) -> pd.Series:
        """Calculate rolling statistics"""
        try:
            rolling_stat = pd.Series(0, index=df.index)
            
            for user_id in df[group_col].unique():
                user_mask = df[group_col] == user_id
                user_data = df[user_mask].copy()
                user_data = user_data.sort_values(time_col)
                
                for i, row in user_data.iterrows():
                    time_window = row[time_col] - pd.Timedelta(days=days)
                    window_data = user_data[user_data[time_col] > time_window][value_col]
                    
                    if stat == "mean":
                        rolling_stat.loc[i] = window_data.mean() if len(window_data) > 0 else 0
                    elif stat == "max":
                        rolling_stat.loc[i] = window_data.max() if len(window_data) > 0 else 0
                    elif stat == "min":
                        rolling_stat.loc[i] = window_data.min() if len(window_data) > 0 else 0
                    elif stat == "std":
                        rolling_stat.loc[i] = window_data.std() if len(window_data) > 0 else 0
            
            return rolling_stat
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate rolling statistic: {e}")
            return pd.Series(0, index=df.index)
    
    async def _calculate_transaction_gap(self, df: pd.DataFrame, group_col: str, 
                                       time_col: str) -> pd.Series:
        """Calculate time gap since last transaction"""
        try:
            gap = pd.Series(0, index=df.index)
            
            for user_id in df[group_col].unique():
                user_mask = df[group_col] == user_id
                user_data = df[user_mask].copy()
                user_data = user_data.sort_values(time_col)
                
                for i, row in user_data.iterrows():
                    prev_transactions = user_data[user_data[time_col] < row[time_col]]
                    if len(prev_transactions) > 0:
                        last_time = prev_transactions[time_col].iloc[-1]
                        gap.loc[i] = (row[time_col] - last_time).total_seconds() / 3600  # hours
                    else:
                        gap.loc[i] = 0
            
            return gap
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate transaction gap: {e}")
            return pd.Series(0, index=df.index)
    
    async def _calculate_merchant_category_risk(self, merchant_categories: pd.Series) -> pd.Series:
        """Calculate merchant category risk scores"""
        try:
            # Risk scores for different merchant categories
            risk_scores = {
                'gas_station': 0.3,
                'grocery': 0.2,
                'restaurant': 0.4,
                'retail': 0.5,
                'online': 0.7,
                'atm': 0.6,
                'pharmacy': 0.3,
                'entertainment': 0.8,
                'travel': 0.9,
                'jewelry': 0.9,
                'electronics': 0.7,
                'cash_advance': 1.0
            }
            
            return merchant_categories.map(risk_scores).fillna(0.5)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate merchant category risk: {e}")
            return pd.Series(0.5, index=merchant_categories.index)
    
    async def _calculate_location_risk(self, locations: pd.Series) -> pd.Series:
        """Calculate location risk scores"""
        try:
            # Simple location risk based on location patterns
            # In production, this would use geolocation data
            risk_scores = pd.Series(0.5, index=locations.index)
            
            # Higher risk for international locations
            international_mask = locations.str.contains('international|foreign|overseas', case=False, na=False)
            risk_scores[international_mask] = 0.8
            
            # Lower risk for home country
            domestic_mask = locations.str.contains('domestic|local|home', case=False, na=False)
            risk_scores[domestic_mask] = 0.3
            
            return risk_scores
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate location risk: {e}")
            return pd.Series(0.5, index=locations.index)
    
    async def _calculate_device_trust_score(self, df: pd.DataFrame, device_col: str, 
                                          user_col: str) -> pd.Series:
        """Calculate device trust scores"""
        try:
            trust_scores = pd.Series(0.5, index=df.index)
            
            # Calculate device usage frequency per user
            device_freq = df.groupby([user_col, device_col]).size().reset_index(name='frequency')
            
            for i, row in df.iterrows():
                user_id = row[user_col]
                device_id = row[device_col]
                
                if pd.notna(device_id):
                    user_devices = device_freq[device_freq[user_col] == user_id]
                    if len(user_devices) > 0:
                        device_frequency = user_devices[user_devices[device_col] == device_id]['frequency'].iloc[0] if len(user_devices[user_devices[device_col] == device_id]) > 0 else 0
                        total_user_transactions = user_devices['frequency'].sum()
                        
                        if total_user_transactions > 0:
                            trust_scores.loc[i] = device_frequency / total_user_transactions
            
            return trust_scores
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate device trust score: {e}")
            return pd.Series(0.5, index=df.index)
    
    async def _calculate_ip_reputation_score(self, ip_addresses: pd.Series) -> pd.Series:
        """Calculate IP reputation scores"""
        try:
            # Simple IP reputation scoring
            # In production, this would integrate with IP reputation services
            reputation_scores = pd.Series(0.5, index=ip_addresses.index)
            
            # Lower reputation for suspicious IP patterns
            suspicious_patterns = ['192.168.', '10.', '172.', '127.', '0.0.0.0']
            for pattern in suspicious_patterns:
                mask = ip_addresses.str.startswith(pattern, na=False)
                reputation_scores[mask] = 0.3
            
            return reputation_scores
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate IP reputation score: {e}")
            return pd.Series(0.5, index=ip_addresses.index)
    
    async def _calculate_user_behavior_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate user behavior anomaly scores"""
        try:
            behavior_scores = pd.Series(0.5, index=df.index)
            
            for user_id in df['user_id'].unique():
                user_mask = df['user_id'] == user_id
                user_data = df[user_mask]
                
                if len(user_data) > 1:
                    # Calculate behavioral patterns
                    amount_mean = user_data['amount'].mean()
                    amount_std = user_data['amount'].std()
                    
                    # Calculate anomaly score based on amount deviation
                    for i, row in user_data.iterrows():
                        if amount_std > 0:
                            z_score = abs((row['amount'] - amount_mean) / amount_std)
                            behavior_scores.loc[i] = min(1.0, z_score / 3.0)  # Normalize to 0-1
            
            return behavior_scores
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to calculate user behavior score: {e}")
            return pd.Series(0.5, index=df.index)
    
    async def _calculate_feature_importance(self, df: pd.DataFrame, 
                                          target_column: str) -> Dict[str, float]:
        """Calculate feature importance scores"""
        try:
            if target_column not in df.columns:
                return {}
            
            # Separate features and target
            feature_columns = [col for col in df.columns if col != target_column]
            X = df[feature_columns].select_dtypes(include=[np.number])
            y = df[target_column]
            
            if len(X.columns) == 0 or len(y.unique()) < 2:
                return {}
            
            # Use mutual information for feature importance
            importance_scores = mutual_info_classif(X, y, random_state=42)
            
            # Create importance dictionary
            importance_dict = {}
            for i, feature in enumerate(X.columns):
                importance_dict[feature] = float(importance_scores[i])
            
            return importance_dict
            
        except (ValueError) as e:
            logger.error(f"Failed to calculate feature importance: {e}")
            return {}
    
    async def _calculate_feature_correlations(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate feature correlation matrix"""
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            correlation_matrix = numeric_df.corr()
            
            # Convert to dictionary format
            correlation_dict = {}
            for col1 in correlation_matrix.columns:
                correlation_dict[col1] = {}
                for col2 in correlation_matrix.columns:
                    correlation_dict[col1][col2] = float(correlation_matrix.loc[col1, col2])
            
            return correlation_dict
            
        except (ValueError) as e:
            logger.error(f"Failed to calculate feature correlations: {e}")
            return {}
    
    async def _create_feature_definitions(self, df: pd.DataFrame, 
                                        original_features: int) -> List[FeatureDefinition]:
        """Create feature definitions for engineered features"""
        try:
            new_definitions = []
            
            # Get engineered feature columns
            engineered_columns = df.columns[original_features:]
            
            for col in engineered_columns:
                if col in self.feature_definitions:
                    new_definitions.append(self.feature_definitions[col])
            
            return new_definitions
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create feature definitions: {e}")
            return []
    
    async def select_features(self, df: pd.DataFrame, target_column: str, 
                            k_best: int = 20, method: str = "mutual_info") -> FeatureSelectionResult:
        """Select best features using various methods"""
        try:
            start_time = time.time()
            
            # Separate features and target
            feature_columns = [col for col in df.columns if col != target_column]
            X = df[feature_columns].select_dtypes(include=[np.number])
            y = df[target_column]
            
            if len(X.columns) == 0 or len(y.unique()) < 2:
                return FeatureSelectionResult(
                    selected_features=[],
                    feature_scores={},
                    selection_method=method,
                    k_best=k_best,
                    total_features_before=len(feature_columns),
                    total_features_after=0,
                    processing_time=time.time() - start_time
                )
            
            # Apply feature selection
            if method == "mutual_info":
                selector = SelectKBest(score_func=mutual_info_classif, k=min(k_best, len(X.columns)))
            elif method == "f_classif":
                selector = SelectKBest(score_func=f_classif, k=min(k_best, len(X.columns)))
            else:
                raise ValueError(f"Unsupported selection method: {method}")
            
            X_selected = selector.fit_transform(X, y)
            selected_features = X.columns[selector.get_support()].tolist()
            
            # Get feature scores
            feature_scores = {}
            for i, feature in enumerate(X.columns):
                feature_scores[feature] = float(selector.scores_[i])
            
            processing_time = time.time() - start_time
            
            return FeatureSelectionResult(
                selected_features=selected_features,
                feature_scores=feature_scores,
                selection_method=method,
                k_best=k_best,
                total_features_before=len(feature_columns),
                total_features_after=len(selected_features),
                processing_time=processing_time
            )
            
        except (ValueError) as e:
            logger.error(f"Failed to select features: {e}")
            raise
    
    async def get_feature_engineering_summary(self) -> Dict[str, Any]:
        """Get feature engineering summary"""
        try:
            if not self.feature_history:
                return {'message': 'No feature engineering history available'}
            
            latest_result = self.feature_history[-1]
            
            return {
                'total_engineering_runs': len(self.feature_history),
                'latest_run': {
                    'original_features': latest_result.original_features,
                    'engineered_features': latest_result.engineered_features,
                    'total_features': latest_result.total_features,
                    'processing_time': latest_result.processing_time,
                    'created_at': latest_result.created_at.isoformat()
                },
                'feature_definitions_count': len(self.feature_definitions),
                'top_features': sorted(
                    latest_result.feature_importance_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get feature engineering summary: {e}")
            return {}


# Global feature engineering service instance
feature_engineering_service = FeatureEngineeringService()
