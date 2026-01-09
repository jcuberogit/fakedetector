"""
Messaging Service
Migrated from C# FraudDetectionAgent.Api.Services.MessagingService
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from .messaging_models import (
    MessagingHealthStatus, MessagingMetrics, MessagingConfiguration,
    MessagingStatus, MessagingStats
)
from .service_bus_publisher import ServiceBusPublisher
from .service_bus_subscriber import ServiceBusSubscriber
from .event_hubs_publisher import EventHubsPublisher
from .fraud_tools_models import FraudAlert

logger = logging.getLogger(__name__)


class MessagingHealthCheck:
    """Health check service for messaging components"""
    
    def __init__(self, service_bus_publisher: ServiceBusPublisher, 
                 service_bus_subscriber: ServiceBusSubscriber,
                 event_hubs_publisher: EventHubsPublisher):
        self.service_bus_publisher = service_bus_publisher
        self.service_bus_subscriber = service_bus_subscriber
        self.event_hubs_publisher = event_hubs_publisher
    
    async def check_health(self) -> MessagingHealthStatus:
        """Perform comprehensive health check"""
        errors = []
        details = {}
        
        # Check Service Bus Publisher
        try:
            publisher_healthy = await self.service_bus_publisher.health_check()
            details['service_bus_publisher'] = {
                'status': 'Healthy' if publisher_healthy else 'Unhealthy',
                'connected': publisher_healthy
            }
        except (ValueError, TypeError, AttributeError) as e:
            errors.append(f"Service Bus Publisher health check failed: {e}")
            details['service_bus_publisher'] = {'status': 'Unhealthy', 'error': str(e)}
        
        # Check Service Bus Subscriber
        try:
            subscriber_healthy = await self.service_bus_subscriber.health_check()
            details['service_bus_subscriber'] = {
                'status': 'Healthy' if subscriber_healthy else 'Unhealthy',
                'connected': subscriber_healthy
            }
        except (ValueError, TypeError, AttributeError) as e:
            errors.append(f"Service Bus Subscriber health check failed: {e}")
            details['service_bus_subscriber'] = {'status': 'Unhealthy', 'error': str(e)}
        
        # Check Event Hubs Publisher
        try:
            event_hubs_healthy = await self.event_hubs_publisher.health_check()
            details['event_hubs_publisher'] = {
                'status': 'Healthy' if event_hubs_healthy else 'Unhealthy',
                'connected': event_hubs_healthy
            }
        except (ValueError, TypeError, AttributeError) as e:
            errors.append(f"Event Hubs Publisher health check failed: {e}")
            details['event_hubs_publisher'] = {'status': 'Unhealthy', 'error': str(e)}
        
        # Determine overall status
        all_healthy = all([
            details.get('service_bus_publisher', {}).get('status') == 'Healthy',
            details.get('service_bus_subscriber', {}).get('status') == 'Healthy',
            details.get('event_hubs_publisher', {}).get('status') == 'Healthy'
        ])
        
        if all_healthy:
            overall_status = MessagingStatus.HEALTHY
        elif len(errors) == 0:
            overall_status = MessagingStatus.DEGRADED
        else:
            overall_status = MessagingStatus.UNHEALTHY
        
        return MessagingHealthStatus(
            overall_status=overall_status,
            service_bus_status=MessagingStatus.HEALTHY if details.get('service_bus_publisher', {}).get('status') == 'Healthy' else MessagingStatus.UNHEALTHY,
            event_hubs_status=MessagingStatus.HEALTHY if details.get('event_hubs_publisher', {}).get('status') == 'Healthy' else MessagingStatus.UNHEALTHY,
            details=details,
            errors=errors
        )


class MessagingService:
    """Main messaging service that orchestrates all messaging operations"""
    
    def __init__(self, config: MessagingConfiguration):
        self.config = config
        self.is_running = False
        self.start_time = None
        
        # Initialize components
        self.service_bus_publisher = ServiceBusPublisher(config)
        self.service_bus_subscriber = ServiceBusSubscriber(config)
        self.event_hubs_publisher = EventHubsPublisher(config)
        self.health_check = MessagingHealthCheck(
            self.service_bus_publisher,
            self.service_bus_subscriber,
            self.event_hubs_publisher
        )
        
        # Statistics
        self.stats = MessagingStats()
        
        logger.info("Messaging Service initialized")
    
    async def start(self) -> None:
        """Start all messaging services"""
        try:
            logger.info("Starting messaging services...")
            
            # Start Service Bus Publisher
            await self.service_bus_publisher.connect()
            
            # Start Service Bus Subscriber
            await self.service_bus_subscriber.start()
            
            # Start Event Hubs Publisher
            await self.event_hubs_publisher.connect()
            
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            logger.info("All messaging services started successfully")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to start messaging services: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop all messaging services"""
        try:
            logger.info("Stopping messaging services...")
            
            # Stop Service Bus Subscriber
            await self.service_bus_subscriber.stop()
            
            # Disconnect publishers
            await self.service_bus_publisher.disconnect()
            await self.event_hubs_publisher.disconnect()
            
            self.is_running = False
            
            logger.info("All messaging services stopped")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error stopping messaging services: {e}")
            raise
    
    async def get_health_status(self) -> MessagingHealthStatus:
        """Get the health status of messaging services"""
        return await self.health_check.check_health()
    
    async def get_metrics(self) -> MessagingMetrics:
        """Get messaging metrics and statistics"""
        try:
            # Get component statistics
            publisher_stats = await self.service_bus_publisher.get_publisher_stats()
            subscriber_stats = await self.service_bus_subscriber.get_subscriber_stats()
            event_hubs_stats = await self.event_hubs_publisher.get_publisher_stats()
            
            # Calculate overall metrics
            total_published = publisher_stats['published_count'] + event_hubs_stats['published_count']
            total_consumed = subscriber_stats['messages_processed']
            total_failed = publisher_stats['failed_count'] + subscriber_stats['messages_failed'] + event_hubs_stats['failed_count']
            
            success_rate = 0.0
            if total_published + total_consumed > 0:
                success_rate = (total_published + total_consumed - total_failed) / (total_published + total_consumed)
            
            return MessagingMetrics(
                service_bus_messages_published=publisher_stats['published_count'],
                service_bus_messages_consumed=subscriber_stats['messages_processed'],
                event_hubs_events_published=event_hubs_stats['published_count'],
                event_hubs_events_consumed=0,  # Event Hubs consumer not implemented
                dead_letter_queue_count=subscriber_stats['dead_letter_count'],
                average_latency_ms=50.0,  # Simulated average latency
                success_rate=success_rate,
                partition_metrics={
                    'partition_0': event_hubs_stats['published_count'] // 4,
                    'partition_1': event_hubs_stats['published_count'] // 4,
                    'partition_2': event_hubs_stats['published_count'] // 4,
                    'partition_3': event_hubs_stats['published_count'] // 4
                }
            )
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to get messaging metrics: {e}")
            return MessagingMetrics()
    
    async def send_fraud_alert(self, fraud_alert: FraudAlert) -> bool:
        """Send a fraud alert through messaging services"""
        try:
            # Send to Service Bus
            result = await self.service_bus_publisher.publish_fraud_alert(fraud_alert)
            
            if result.is_success:
                logger.info(f"Fraud alert {fraud_alert.transaction_id} sent successfully")
                return True
            else:
                logger.error(f"Failed to send fraud alert {fraud_alert.transaction_id}: {result.error_message}")
                return False
                
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error sending fraud alert: {e}")
            return False
    
    async def send_transaction_analysis(self, transaction: Dict[str, Any]) -> bool:
        """Send transaction analysis through messaging services"""
        try:
            # Send to Service Bus
            result = await self.service_bus_publisher.publish_transaction_analysis(transaction)
            
            # Send to Event Hubs
            event_result = await self.event_hubs_publisher.send_transaction_event(transaction)
            
            success = result.is_success and event_result.is_success
            
            if success:
                logger.info(f"Transaction analysis {transaction.get('transaction_id', 'unknown')} sent successfully")
            else:
                logger.error(f"Failed to send transaction analysis: Service Bus: {result.error_message}, Event Hubs: {event_result.error_message}")
            
            return success
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error sending transaction analysis: {e}")
            return False
    
    async def get_service_stats(self) -> MessagingStats:
        """Get comprehensive service statistics"""
        try:
            metrics = await self.get_metrics()
            
            # Calculate uptime
            uptime_hours = 0.0
            if self.start_time:
                uptime_hours = (datetime.utcnow() - self.start_time).total_seconds() / 3600
            
            # Calculate throughput
            total_messages = metrics.service_bus_messages_published + metrics.event_hubs_events_published
            current_throughput = int(total_messages / max(uptime_hours, 0.001)) if uptime_hours > 0 else 0
            
            self.stats.total_messages_sent = metrics.service_bus_messages_published + metrics.event_hubs_events_published
            self.stats.total_messages_received = metrics.service_bus_messages_consumed
            self.stats.successful_messages = int((metrics.service_bus_messages_published + metrics.event_hubs_events_published) * metrics.success_rate)
            self.stats.failed_messages = int((metrics.service_bus_messages_published + metrics.event_hubs_events_published) * (1 - metrics.success_rate))
            self.stats.average_processing_time_ms = metrics.average_latency_ms
            self.stats.current_throughput_per_second = current_throughput
            self.stats.uptime_hours = uptime_hours
            
            return self.stats
            
        except (ValueError) as e:
            logger.error(f"Failed to get service stats: {e}")
            return self.stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            health_status = await self.get_health_status()
            return health_status.overall_status == MessagingStatus.HEALTHY
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Messaging service health check failed: {e}")
            return False


# Global messaging service instance
messaging_service: Optional[MessagingService] = None


async def get_messaging_service(config: MessagingConfiguration) -> MessagingService:
    """Get or create the global messaging service instance"""
    global messaging_service
    
    if messaging_service is None:
        messaging_service = MessagingService(config)
        await messaging_service.start()
    
    return messaging_service
