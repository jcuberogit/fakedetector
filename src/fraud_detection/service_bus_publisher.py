"""
Service Bus Publisher Service
Migrated from C# FraudDetectionAgent.Api.Services.ServiceBusPublisher
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .messaging_models import (
    MessagingResult, BatchMessagingResult, FraudAlertMessage, 
    MessageEnvelope, MessagingConfiguration
)
from .fraud_tools_models import FraudAlert

logger = logging.getLogger(__name__)


class MessageIdempotencyService:
    """Service for handling message idempotency"""
    
    def __init__(self):
        self.processed_messages: Dict[str, datetime] = {}
        self.ttl_hours = 24
    
    def generate_message_id(self, message: FraudAlertMessage) -> str:
        """Generate a unique message ID based on message content"""
        # Create a deterministic ID based on message content
        content_hash = hash(f"{message.transaction_id}_{message.user_id}_{message.timestamp.isoformat()}")
        return f"msg_{abs(content_hash)}"
    
    async def is_message_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed"""
        if message_id in self.processed_messages:
            processed_time = self.processed_messages[message_id]
            # Check if TTL has expired
            if datetime.utcnow() - processed_time < timedelta(hours=self.ttl_hours):
                return True
            else:
                # Remove expired entry
                del self.processed_messages[message_id]
        return False
    
    async def mark_message_as_processed(self, message_id: str, ttl: timedelta = None) -> None:
        """Mark a message as processed"""
        self.processed_messages[message_id] = datetime.utcnow()
        if ttl:
            self.ttl_hours = ttl.total_seconds() / 3600


class MessageRetryService:
    """Service for handling message retries"""
    
    def __init__(self, config: MessagingConfiguration):
        self.config = config
        self.retry_counts: Dict[str, int] = {}
    
    async def should_retry(self, message_id: str, error: Exception) -> bool:
        """Determine if a message should be retried"""
        retry_count = self.retry_counts.get(message_id, 0)
        return retry_count < self.config.retry.max_retries
    
    async def get_retry_delay(self, message_id: str) -> float:
        """Get the delay for the next retry"""
        retry_count = self.retry_counts.get(message_id, 0)
        
        # Exponential backoff with jitter
        delay = self.config.retry.initial_delay_seconds * (self.config.retry.backoff_multiplier ** retry_count)
        delay = min(delay, self.config.retry.max_delay_minutes * 60)
        
        # Add jitter
        import random
        jitter = random.uniform(0, self.config.retry.jitter_milliseconds / 1000)
        return delay + jitter
    
    async def increment_retry_count(self, message_id: str) -> None:
        """Increment the retry count for a message"""
        self.retry_counts[message_id] = self.retry_counts.get(message_id, 0) + 1
    
    async def reset_retry_count(self, message_id: str) -> None:
        """Reset the retry count for a message"""
        if message_id in self.retry_counts:
            del self.retry_counts[message_id]


class ServiceBusPublisher:
    """Service Bus publisher for fraud alerts"""
    
    def __init__(self, config: MessagingConfiguration):
        self.config = config
        self.idempotency_service = MessageIdempotencyService()
        self.retry_service = MessageRetryService(config)
        self.is_connected = False
        self.published_count = 0
        self.failed_count = 0
        
        logger.info("Service Bus Publisher initialized")
    
    async def connect(self) -> bool:
        """Connect to Service Bus"""
        try:
            # Simulate connection to Service Bus
            await asyncio.sleep(0.1)  # Simulate connection delay
            self.is_connected = True
            logger.info(f"Connected to Service Bus topic: {self.config.service_bus.topic_name}")
            return True
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to connect to Service Bus: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Service Bus"""
        self.is_connected = False
        logger.info("Disconnected from Service Bus")
    
    async def publish_fraud_alert(self, fraud_alert: FraudAlert) -> MessagingResult:
        """Publish a fraud alert to Service Bus"""
        try:
            # Convert FraudAlert to FraudAlertMessage
            message = FraudAlertMessage(
                transaction_id=fraud_alert.transaction_id,
                score=float(fraud_alert.risk_score),
                action="REQUIRES_ACTION" if fraud_alert.requires_action else "MONITOR",
                timestamp=fraud_alert.created_at,
                user_id=fraud_alert.user_id,
                account_id=fraud_alert.user_id,
                metadata={
                    "risk_level": fraud_alert.risk_level.value if hasattr(fraud_alert.risk_level, 'value') else str(fraud_alert.risk_level),
                    "factors": [f.type for f in fraud_alert.risk_factors] if fraud_alert.risk_factors else []
                }
            )
            
            return await self.publish_fraud_alert_message(message)
            
        except (ValueError) as e:
            logger.error(f"Failed to publish fraud alert for transaction {fraud_alert.transaction_id}: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def publish_fraud_alert_message(self, message: FraudAlertMessage) -> MessagingResult:
        """Publish a fraud alert message to Service Bus"""
        try:
            # Check for idempotency
            message_id = self.idempotency_service.generate_message_id(message)
            if await self.idempotency_service.is_message_processed(message_id):
                logger.info(f"Message {message_id} already processed, returning cached result")
                return MessagingResult(
                    is_success=True,
                    message_id=message_id,
                    timestamp=datetime.utcnow()
                )
            
            # Check connection
            if not self.is_connected:
                await self.connect()
            
            # Simulate publishing to Service Bus
            await asyncio.sleep(0.1)  # Simulate network delay
            
            result = MessagingResult(
                is_success=True,
                message_id=message_id,
                timestamp=datetime.utcnow(),
                correlation_id=message.correlation_id
            )
            
            # Mark message as processed for idempotency
            await self.idempotency_service.mark_message_as_processed(message_id, timedelta(hours=24))
            
            self.published_count += 1
            logger.info(f"Published fraud alert {message_id} to topic {self.config.service_bus.topic_name}")
            return result
            
        except (ValueError, TypeError, AttributeError) as e:
            self.failed_count += 1
            logger.error(f"Failed to publish fraud alert message {message.id}: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def publish_fraud_alert_batch(self, fraud_alerts: List[FraudAlert]) -> BatchMessagingResult:
        """Publish a batch of fraud alerts to Service Bus"""
        results = []
        successful_count = 0
        failed_count = 0
        
        for fraud_alert in fraud_alerts:
            try:
                result = await self.publish_fraud_alert(fraud_alert)
                results.append(result)
                
                if result.is_success:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Failed to publish fraud alert {fraud_alert.transaction_id}: {e}")
                results.append(MessagingResult(
                    is_success=False,
                    error_message=str(e),
                    timestamp=datetime.utcnow()
                ))
                failed_count += 1
        
        return BatchMessagingResult(
            total_messages=len(fraud_alerts),
            successful_messages=successful_count,
            failed_messages=failed_count,
            results=results,
            timestamp=datetime.utcnow()
        )
    
    async def publish_transaction_analysis(self, transaction: Dict[str, Any]) -> MessagingResult:
        """Publish transaction analysis to Service Bus"""
        try:
            message = FraudAlertMessage(
                transaction_id=transaction.get('transaction_id', ''),
                score=transaction.get('risk_score', 0.0),
                action=transaction.get('action', 'MONITOR'),
                timestamp=datetime.utcnow(),
                user_id=transaction.get('user_id', ''),
                account_id=transaction.get('account_id', ''),
                metadata=transaction.get('metadata', {})
            )
            
            return await self.publish_fraud_alert_message(message)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to publish transaction analysis: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_publisher_stats(self) -> Dict[str, Any]:
        """Get publisher statistics"""
        return {
            "is_connected": self.is_connected,
            "published_count": self.published_count,
            "failed_count": self.failed_count,
            "success_rate": self.published_count / (self.published_count + self.failed_count) if (self.published_count + self.failed_count) > 0 else 0.0,
            "topic_name": self.config.service_bus.topic_name,
            "subscription_name": self.config.service_bus.subscription_name
        }
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Simulate health check
            if not self.is_connected:
                await self.connect()
            
            return self.is_connected
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Service Bus Publisher health check failed: {e}")
            return False
