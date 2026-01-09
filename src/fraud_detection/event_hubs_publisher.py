"""
Event Hubs Publisher Service
Migrated from C# FraudDetectionAgent.Api.Services.EventHubsPublisher
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from .messaging_models import (
    MessagingResult, BatchMessagingResult, TransactionMessage, 
    MessagingConfiguration, EventHubInfo
)

logger = logging.getLogger(__name__)


class EventHubsPublisher:
    """Event Hubs publisher for transaction events"""
    
    def __init__(self, config: MessagingConfiguration):
        self.config = config
        self.is_connected = False
        self.published_count = 0
        self.failed_count = 0
        self.partition_count = 4  # Default partition count
        
        logger.info("Event Hubs Publisher initialized")
    
    async def connect(self) -> bool:
        """Connect to Event Hubs"""
        try:
            # Simulate connection to Event Hubs
            await asyncio.sleep(0.1)  # Simulate connection delay
            self.is_connected = True
            logger.info(f"Connected to Event Hub: {self.config.event_hubs.event_hub_name}")
            return True
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to connect to Event Hubs: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Event Hubs"""
        self.is_connected = False
        logger.info("Disconnected from Event Hubs")
    
    async def send_transaction_event(self, transaction: Dict[str, Any]) -> MessagingResult:
        """Send a transaction event to Event Hubs"""
        try:
            # Convert transaction dict to TransactionMessage
            message = TransactionMessage(
                amount=transaction.get('amount', 0.0),
                merchant_name=transaction.get('merchant_name', ''),
                location=transaction.get('location', ''),
                timestamp=transaction.get('timestamp', datetime.utcnow()),
                user_id=transaction.get('user_id', ''),
                account_id=transaction.get('account_id', ''),
                device_id=transaction.get('device_id'),
                ip_address=transaction.get('ip_address'),
                properties=transaction.get('properties', {}),
                metadata=transaction.get('metadata', {})
            )
            
            return await self.send_transaction_message(message)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to send transaction event: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def send_transaction_message(self, message: TransactionMessage) -> MessagingResult:
        """Send a transaction message to Event Hubs"""
        try:
            # Check connection
            if not self.is_connected:
                await self.connect()
            
            # Simulate sending to Event Hubs
            await asyncio.sleep(0.05)  # Simulate network delay
            
            # Determine partition based on user_id for consistent partitioning
            partition_key = message.user_id or message.account_id or "default"
            
            result = MessagingResult(
                is_success=True,
                message_id=message.id,
                timestamp=datetime.utcnow(),
                correlation_id=message.correlation_id
            )
            
            self.published_count += 1
            logger.info(f"Sent transaction event {message.id} to Event Hub {self.config.event_hubs.event_hub_name} (partition: {hash(partition_key) % self.partition_count})")
            return result
            
        except (ValueError, TypeError, AttributeError) as e:
            self.failed_count += 1
            logger.error(f"Failed to send transaction message {message.id}: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def send_fraud_event(self, fraud_alert: Dict[str, Any]) -> MessagingResult:
        """Send a fraud event to Event Hubs"""
        try:
            # Convert fraud alert to transaction message format
            message = TransactionMessage(
                amount=fraud_alert.get('amount', 0.0),
                merchant_name=fraud_alert.get('merchant_name', ''),
                location=fraud_alert.get('location', ''),
                timestamp=fraud_alert.get('timestamp', datetime.utcnow()),
                user_id=fraud_alert.get('user_id', ''),
                account_id=fraud_alert.get('account_id', ''),
                properties={
                    'fraud_score': fraud_alert.get('fraud_score', 0.0),
                    'action': fraud_alert.get('action', 'MONITOR'),
                    'risk_level': fraud_alert.get('risk_level', 'Low'),
                    'event_type': 'fraud_alert'
                }
            )
            
            return await self.send_transaction_message(message)
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to send fraud event: {e}")
            return MessagingResult(
                is_success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def send_batch_events(self, events: List[Dict[str, Any]]) -> BatchMessagingResult:
        """Send a batch of events to Event Hubs"""
        results = []
        successful_count = 0
        failed_count = 0
        
        for event in events:
            try:
                result = await self.send_transaction_event(event)
                results.append(result)
                
                if result.is_success:
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Failed to send event: {e}")
                results.append(MessagingResult(
                    is_success=False,
                    error_message=str(e),
                    timestamp=datetime.utcnow()
                ))
                failed_count += 1
        
        return BatchMessagingResult(
            total_messages=len(events),
            successful_messages=successful_count,
            failed_messages=failed_count,
            results=results,
            timestamp=datetime.utcnow()
        )
    
    async def read_transaction_events(self, max_events: int = 100) -> List[Dict[str, Any]]:
        """Read transaction events from Event Hubs (simulation)"""
        try:
            # Simulate reading events
            events = []
            
            # Generate sample events for demonstration
            import random
            for i in range(min(max_events, 10)):  # Limit to 10 for simulation
                event = {
                    'id': f"event_{int(time.time())}_{i}",
                    'amount': random.uniform(10, 1000),
                    'merchant_name': f"Merchant_{random.randint(1, 100)}",
                    'location': f"Location_{random.randint(1, 50)}",
                    'timestamp': datetime.utcnow(),
                    'user_id': f"user_{random.randint(1000, 9999)}",
                    'account_id': f"account_{random.randint(1000, 9999)}",
                    'device_id': f"device_{random.randint(1000, 9999)}",
                    'ip_address': f"192.168.1.{random.randint(1, 254)}",
                    'properties': {
                        'simulated': True,
                        'source': 'event_hubs_publisher'
                    }
                }
                events.append(event)
            
            logger.info(f"Read {len(events)} transaction events from Event Hubs")
            return events
            
        except (ValueError) as e:
            logger.error(f"Failed to read transaction events: {e}")
            return []
    
    async def get_event_hub_info(self) -> EventHubInfo:
        """Get Event Hub information"""
        return EventHubInfo(
            event_hub_name=self.config.event_hubs.event_hub_name,
            consumer_group=self.config.event_hubs.consumer_group,
            partition_count=self.partition_count,
            is_active=self.is_connected,
            last_activity=datetime.utcnow() if self.is_connected else None
        )
    
    async def get_publisher_stats(self) -> Dict[str, Any]:
        """Get publisher statistics"""
        return {
            "is_connected": self.is_connected,
            "published_count": self.published_count,
            "failed_count": self.failed_count,
            "success_rate": self.published_count / (self.published_count + self.failed_count) if (self.published_count + self.failed_count) > 0 else 0.0,
            "event_hub_name": self.config.event_hubs.event_hub_name,
            "consumer_group": self.config.event_hubs.consumer_group,
            "partition_count": self.partition_count
        }
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.is_connected:
                await self.connect()
            
            return self.is_connected
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Event Hubs Publisher health check failed: {e}")
            return False
