"""
Service Bus Subscriber Service
Migrated from C# FraudDetectionAgent.Api.Services.ServiceBusSubscriber
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from .messaging_models import (
    FraudAlertMessage, MessagingConfiguration, MessageProcessingResult, 
    MessageStatus, SubscriptionInfo
)
from .fraud_tools_models import FraudAlert

logger = logging.getLogger(__name__)


class ServiceBusSubscriber:
    """Service Bus subscriber for fraud alerts"""
    
    def __init__(self, config: MessagingConfiguration):
        self.config = config
        self.is_running = False
        self.is_connected = False
        self.cancellation_token = None
        self.processing_task = None
        
        # Event handlers
        self.on_fraud_alert_received: Optional[Callable[[FraudAlert], Awaitable[None]]] = None
        self.on_dead_letter_message_received: Optional[Callable[[FraudAlert], Awaitable[None]]] = None
        
        # Statistics
        self.messages_processed = 0
        self.messages_failed = 0
        self.dead_letter_count = 0
        
        logger.info("Service Bus Subscriber initialized")
    
    async def connect(self) -> bool:
        """Connect to Service Bus"""
        try:
            # Simulate connection to Service Bus
            await asyncio.sleep(0.1)  # Simulate connection delay
            self.is_connected = True
            logger.info(f"Connected to Service Bus subscription: {self.config.service_bus.subscription_name}")
            return True
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to connect to Service Bus: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Service Bus"""
        self.is_connected = False
        logger.info("Disconnected from Service Bus")
    
    async def start(self) -> None:
        """Start the subscription"""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not self.is_connected:
                raise Exception("Failed to connect to Service Bus")
            
            self.is_running = True
            self.cancellation_token = asyncio.CancelledError
            
            logger.info(f"Started subscription to topic {self.config.service_bus.topic_name} with subscription {self.config.service_bus.subscription_name}")
            
            # Start message processing task
            self.processing_task = asyncio.create_task(self._process_messages())
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to start Service Bus subscription: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the subscription"""
        try:
            self.is_running = False
            
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            await self.disconnect()
            logger.info("Stopped Service Bus subscription")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error stopping Service Bus subscription: {e}")
            raise
    
    async def _process_messages(self) -> None:
        """Process messages from Service Bus"""
        logger.info("Started message processing loop")
        
        while self.is_running:
            try:
                # Simulate receiving messages
                messages = await self._receive_messages()
                
                for message in messages:
                    if not self.is_running:
                        break
                    
                    await self._process_message(message)
                
                # Wait before next poll
                await asyncio.sleep(1.0)
                
            except asyncio.CancelledError:
                logger.info("Message processing cancelled")
                break
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(5.0)  # Wait before retrying
        
        logger.info("Message processing loop ended")
    
    async def _receive_messages(self) -> List[FraudAlertMessage]:
        """Simulate receiving messages from Service Bus"""
        # In a real implementation, this would connect to Azure Service Bus
        # For now, we'll simulate receiving messages occasionally
        
        import random
        if random.random() < 0.1:  # 10% chance of receiving a message
            # Generate a sample fraud alert message
            message = FraudAlertMessage(
                transaction_id=f"txn_{int(time.time())}",
                score=random.uniform(0.1, 0.9),
                action="MONITOR" if random.random() < 0.7 else "REQUIRES_ACTION",
                user_id=f"user_{random.randint(1000, 9999)}",
                account_id=f"account_{random.randint(1000, 9999)}",
                metadata={"simulated": True, "source": "service_bus_subscriber"}
            )
            return [message]
        
        return []
    
    async def _process_message(self, message: FraudAlertMessage) -> MessageProcessingResult:
        """Process a single message"""
        start_time = time.time()
        
        try:
            # Convert FraudAlertMessage to FraudAlert
            fraud_alert = FraudAlert(
                id=message.id,
                transaction_id=message.transaction_id,
                user_id=message.user_id,
                risk_score=message.score,
                risk_level=self._score_to_risk_level(message.score),
                requires_action=message.action == "REQUIRES_ACTION",
                created_at=message.timestamp,
                risk_factors=[]  # Would be populated from metadata in real implementation
            )
            
            # Call event handler if registered
            if self.on_fraud_alert_received:
                await self.on_fraud_alert_received(fraud_alert)
            
            processing_time = (time.time() - start_time) * 1000
            self.messages_processed += 1
            
            logger.info(f"Processed fraud alert message {message.id} in {processing_time:.2f}ms")
            
            return MessageProcessingResult(
                message_id=message.id,
                status=MessageStatus.COMPLETED,
                processing_time_ms=processing_time,
                processed_at=datetime.utcnow()
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            processing_time = (time.time() - start_time) * 1000
            self.messages_failed += 1
            
            logger.error(f"Failed to process message {message.id}: {e}")
            
            return MessageProcessingResult(
                message_id=message.id,
                status=MessageStatus.FAILED,
                processing_time_ms=processing_time,
                error_message=str(e),
                processed_at=datetime.utcnow()
            )
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.8:
            return "Critical"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"
    
    async def process_dead_letter_queue(self) -> None:
        """Process messages from dead letter queue"""
        try:
            logger.info("Processing dead letter queue")
            
            # Simulate processing dead letter messages
            # In a real implementation, this would connect to the DLQ
            
            await asyncio.sleep(0.1)  # Simulate processing time
            self.dead_letter_count += 1
            
            logger.info("Dead letter queue processing completed")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error processing dead letter queue: {e}")
            raise
    
    async def get_subscription_info(self) -> SubscriptionInfo:
        """Get subscription information"""
        return SubscriptionInfo(
            topic_name=self.config.service_bus.topic_name,
            subscription_name=self.config.service_bus.subscription_name,
            is_active=self.is_running,
            message_count=self.messages_processed,
            dead_letter_count=self.dead_letter_count,
            last_activity=datetime.utcnow() if self.is_running else None
        )
    
    async def get_subscriber_stats(self) -> Dict[str, Any]:
        """Get subscriber statistics"""
        total_messages = self.messages_processed + self.messages_failed
        success_rate = self.messages_processed / total_messages if total_messages > 0 else 0.0
        
        return {
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "messages_processed": self.messages_processed,
            "messages_failed": self.messages_failed,
            "dead_letter_count": self.dead_letter_count,
            "success_rate": success_rate,
            "topic_name": self.config.service_bus.topic_name,
            "subscription_name": self.config.service_bus.subscription_name
        }
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.is_connected:
                await self.connect()
            
            return self.is_connected and self.is_running
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Service Bus Subscriber health check failed: {e}")
            return False
