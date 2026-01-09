"""
Database Integration Service
SQLAlchemy ORM equivalent to C# Entity Framework
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
import uuid
import json

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class FraudDetectionEntity(Base):
    """Base entity for fraud detection with audit fields"""
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)

class TransactionEntity(FraudDetectionEntity):
    """Transaction entity"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    merchant_name = Column(String, nullable=True)
    merchant_category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    transaction_type = Column(String, nullable=True)
    status = Column(String, default='pending')
    risk_score = Column(Float, nullable=True)
    fraud_probability = Column(Float, nullable=True)
    is_fraud = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    transaction_timestamp = Column(DateTime, nullable=True)
    
    # Relationships
    alerts = relationship("FraudAlertEntity", back_populates="transaction")
    feedback = relationship("FraudFeedbackEntity", back_populates="transaction")

class FraudAlertEntity(FraudDetectionEntity):
    """Fraud alert entity"""
    __tablename__ = 'fraud_alerts'
    
    alert_id = Column(String, unique=True, nullable=False)
    transaction_id = Column(String, ForeignKey('transactions.transaction_id'))
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    status = Column(String, default='open')
    assigned_to = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    false_positive = Column(Boolean, default=False)
    
    # Relationships
    transaction = relationship("TransactionEntity", back_populates="alerts")

class FraudFeedbackEntity(FraudDetectionEntity):
    """Fraud feedback entity"""
    __tablename__ = 'fraud_feedback'
    
    feedback_id = Column(String, unique=True, nullable=False)
    transaction_id = Column(String, ForeignKey('transactions.transaction_id'))
    user_id = Column(String, nullable=False)
    feedback_type = Column(String, nullable=False)  # 'fraud', 'legitimate', 'unknown'
    confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    analyst_id = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    
    # Relationships
    transaction = relationship("TransactionEntity", back_populates="feedback")

class MLModelEntity(FraudDetectionEntity):
    """ML model entity"""
    __tablename__ = 'ml_models'
    
    model_id = Column(String, unique=True, nullable=False)
    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # 'xgboost', 'neural_network', 'random_forest'
    version = Column(String, nullable=False)
    status = Column(String, default='training')  # 'training', 'active', 'deprecated'
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_data_size = Column(Integer, nullable=True)
    training_duration = Column(Float, nullable=True)
    model_path = Column(String, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    last_trained = Column(DateTime, nullable=True)
    last_evaluated = Column(DateTime, nullable=True)
    
    # Relationships
    predictions = relationship("MLPredictionEntity", back_populates="model")

class MLPredictionEntity(FraudDetectionEntity):
    """ML prediction entity"""
    __tablename__ = 'ml_predictions'
    
    prediction_id = Column(String, unique=True, nullable=False)
    model_id = Column(String, ForeignKey('ml_models.model_id'))
    transaction_id = Column(String, nullable=True)
    input_features = Column(JSON, nullable=False)
    prediction = Column(Float, nullable=False)
    probability = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    prediction_time = Column(DateTime, default=datetime.utcnow)
    actual_outcome = Column(Boolean, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    
    # Relationships
    model = relationship("MLModelEntity", back_populates="predictions")

class UserEntity(FraudDetectionEntity):
    """User entity"""
    __tablename__ = 'users'
    
    user_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    preferences = Column(JSON, nullable=True)
    
    # Relationships
    sessions = relationship("UserSessionEntity", back_populates="user")

class UserSessionEntity(FraudDetectionEntity):
    """User session entity"""
    __tablename__ = 'user_sessions'
    
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey('users.user_id'))
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    logout_time = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserEntity", back_populates="sessions")

class DatabaseService:
    """Database service using SQLAlchemy ORM"""
    
    def __init__(self, database_url: str = "sqlite:///fraud_detection.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
        
        logger.info("Database service initialized")
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database tables created successfully")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> TransactionEntity:
        """Create a new transaction"""
        try:
            with self.get_session() as session:
                transaction = TransactionEntity(**transaction_data)
                session.add(transaction)
                session.commit()
                session.refresh(transaction)
                return transaction
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    async def get_transaction(self, transaction_id: str) -> Optional[TransactionEntity]:
        """Get transaction by ID"""
        try:
            with self.get_session() as session:
                return session.query(TransactionEntity).filter(
                    TransactionEntity.transaction_id == transaction_id,
                    TransactionEntity.is_deleted == False
                ).first()
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get transaction: {e}")
            return None
    
    async def update_transaction(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[TransactionEntity]:
        """Update transaction"""
        try:
            with self.get_session() as session:
                transaction = session.query(TransactionEntity).filter(
                    TransactionEntity.transaction_id == transaction_id,
                    TransactionEntity.is_deleted == False
                ).first()
                
                if transaction:
                    for key, value in update_data.items():
                        if hasattr(transaction, key):
                            setattr(transaction, key, value)
                    transaction.updated_at = datetime.utcnow()
                    session.commit()
                    session.refresh(transaction)
                    return transaction
                return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to update transaction: {e}")
            return None
    
    async def create_fraud_alert(self, alert_data: Dict[str, Any]) -> FraudAlertEntity:
        """Create a new fraud alert"""
        try:
            with self.get_session() as session:
                alert = FraudAlertEntity(**alert_data)
                session.add(alert)
                session.commit()
                session.refresh(alert)
                return alert
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create fraud alert: {e}")
            raise
    
    async def get_fraud_alerts(self, limit: int = 100, status: Optional[str] = None) -> List[FraudAlertEntity]:
        """Get fraud alerts"""
        try:
            with self.get_session() as session:
                query = session.query(FraudAlertEntity).filter(
                    FraudAlertEntity.is_deleted == False
                )
                
                if status:
                    query = query.filter(FraudAlertEntity.status == status)
                
                return query.order_by(FraudAlertEntity.created_at.desc()).limit(limit).all()
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get fraud alerts: {e}")
            return []
    
    async def create_fraud_feedback(self, feedback_data: Dict[str, Any]) -> FraudFeedbackEntity:
        """Create fraud feedback"""
        try:
            with self.get_session() as session:
                feedback = FraudFeedbackEntity(**feedback_data)
                session.add(feedback)
                session.commit()
                session.refresh(feedback)
                return feedback
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create fraud feedback: {e}")
            raise
    
    async def create_ml_model(self, model_data: Dict[str, Any]) -> MLModelEntity:
        """Create ML model record"""
        try:
            with self.get_session() as session:
                model = MLModelEntity(**model_data)
                session.add(model)
                session.commit()
                session.refresh(model)
                return model
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create ML model: {e}")
            raise
    
    async def get_ml_models(self, status: Optional[str] = None) -> List[MLModelEntity]:
        """Get ML models"""
        try:
            with self.get_session() as session:
                query = session.query(MLModelEntity).filter(
                    MLModelEntity.is_deleted == False
                )
                
                if status:
                    query = query.filter(MLModelEntity.status == status)
                
                return query.order_by(MLModelEntity.created_at.desc()).all()
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get ML models: {e}")
            return []
    
    async def create_ml_prediction(self, prediction_data: Dict[str, Any]) -> MLPredictionEntity:
        """Create ML prediction record"""
        try:
            with self.get_session() as session:
                prediction = MLPredictionEntity(**prediction_data)
                session.add(prediction)
                session.commit()
                session.refresh(prediction)
                return prediction
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create ML prediction: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[UserEntity]:
        """Get user by ID"""
        try:
            with self.get_session() as session:
                return session.query(UserEntity).filter(
                    UserEntity.user_id == user_id,
                    UserEntity.is_deleted == False
                ).first()
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserEntity:
        """Create new user"""
        try:
            with self.get_session() as session:
                user = UserEntity(**user_data)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        try:
            with self.get_session() as session:
                total_transactions = session.query(TransactionEntity).filter(
                    TransactionEntity.is_deleted == False
                ).count()
                
                fraud_transactions = session.query(TransactionEntity).filter(
                    TransactionEntity.is_deleted == False,
                    TransactionEntity.is_fraud == True
                ).count()
                
                high_risk_transactions = session.query(TransactionEntity).filter(
                    TransactionEntity.is_deleted == False,
                    TransactionEntity.risk_score > 0.7
                ).count()
                
                return {
                    'total_transactions': total_transactions,
                    'fraud_transactions': fraud_transactions,
                    'high_risk_transactions': high_risk_transactions,
                    'fraud_rate': (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                    'high_risk_rate': (high_risk_transactions / total_transactions * 100) if total_transactions > 0 else 0
                }
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get transaction statistics: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 90):
        """Cleanup old data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with self.get_session() as session:
                # Soft delete old transactions
                session.query(TransactionEntity).filter(
                    TransactionEntity.created_at < cutoff_date,
                    TransactionEntity.is_deleted == False
                ).update({'is_deleted': True, 'updated_at': datetime.utcnow()})
                
                # Soft delete old sessions
                session.query(UserSessionEntity).filter(
                    UserSessionEntity.created_at < cutoff_date,
                    UserSessionEntity.is_deleted == False
                ).update({'is_deleted': True, 'updated_at': datetime.utcnow()})
                
                session.commit()
                logger.info(f"Cleaned up data older than {days} days")
                
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database service instance
database_service = DatabaseService()
