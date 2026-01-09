"""
Real-time Messaging Models
Migrated from C# FraudDetectionAgent.Api.Models.MessagingModels
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Generic, TypeVar
from enum import Enum
from pydantic import BaseModel, Field
import uuid

T = TypeVar('T')


class MessagingStatus(str, Enum):
    """Messaging service status"""
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    UNHEALTHY = "Unhealthy"
    UNKNOWN = "Unknown"


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    DEAD_LETTERED = "DeadLettered"


class MessagingResult(BaseModel):
    """Result of a messaging operation"""
    is_success: bool = Field(..., description="Whether the operation succeeded")
    message_id: Optional[str] = Field(None, description="Message identifier")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")
    retry_count: int = Field(0, description="Number of retries attempted")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")


class BatchMessagingResult(BaseModel):
    """Result of a batch messaging operation"""
    total_messages: int = Field(..., description="Total number of messages")
    successful_messages: int = Field(..., description="Number of successful messages")
    failed_messages: int = Field(..., description="Number of failed messages")
    results: List[MessagingResult] = Field(default_factory=list, description="Individual message results")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Batch operation timestamp")


class MessagingHealthStatus(BaseModel):
    """Health status of messaging services"""
    overall_status: MessagingStatus = Field(..., description="Overall health status")
    service_bus_status: MessagingStatus = Field(..., description="Service Bus health status")
    event_hubs_status: MessagingStatus = Field(..., description="Event Hubs health status")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional health details")
    errors: List[str] = Field(default_factory=list, description="Health check errors")


class MessagingMetrics(BaseModel):
    """Messaging performance metrics"""
    service_bus_messages_published: int = Field(0, description="Service Bus messages published")
    service_bus_messages_consumed: int = Field(0, description="Service Bus messages consumed")
    event_hubs_events_published: int = Field(0, description="Event Hubs events published")
    event_hubs_events_consumed: int = Field(0, description="Event Hubs events consumed")
    dead_letter_queue_count: int = Field(0, description="Dead letter queue message count")
    average_latency_ms: float = Field(0.0, description="Average message latency in milliseconds")
    success_rate: float = Field(0.0, description="Message processing success rate")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last metrics update")
    partition_metrics: Dict[str, int] = Field(default_factory=dict, description="Per-partition metrics")


class ServiceBusConfiguration(BaseModel):
    """Service Bus configuration"""
    connection_string: str = Field(default="mock_connection_string", description="Service Bus connection string")
    topic_name: str = Field(default="fraud-alerts", description="Topic name")
    subscription_name: str = Field(default="fraud-processor", description="Subscription name")
    max_concurrent_calls: int = Field(default=10, description="Maximum concurrent calls")
    prefetch_count: int = Field(default=100, description="Prefetch count")
    lock_duration_minutes: int = Field(default=5, description="Lock duration in minutes")
    max_auto_renew_duration_minutes: int = Field(default=5, description="Max auto-renew duration in minutes")


class EventHubsConfiguration(BaseModel):
    """Event Hubs configuration"""
    connection_string: str = Field(default="mock_event_hub_connection_string", description="Event Hubs connection string")
    event_hub_name: str = Field(default="fraud-transactions", description="Event Hub name")
    consumer_group: str = Field(default="$Default", description="Consumer group")
    batch_size: int = Field(default=100, description="Batch size")
    batch_timeout_seconds: int = Field(default=10, description="Batch timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retries")


class RetryConfiguration(BaseModel):
    """Retry configuration"""
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    initial_delay_seconds: int = Field(default=1, description="Initial delay in seconds")
    max_delay_minutes: int = Field(default=5, description="Maximum delay in minutes")
    backoff_multiplier: float = Field(default=2.0, description="Backoff multiplier")
    jitter_milliseconds: int = Field(default=100, description="Jitter in milliseconds")


class DeadLetterQueueConfiguration(BaseModel):
    """Dead Letter Queue configuration"""
    enabled: bool = Field(default=True, description="Whether DLQ is enabled")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_interval_minutes: int = Field(default=5, description="Retry interval in minutes")
    message_ttl_days: int = Field(default=7, description="Message TTL in days")
    dlq_topic_name: str = Field(default="fraud-alerts-dlq", description="DLQ topic name")


class MessagingConfiguration(BaseModel):
    """Configuration for messaging services"""
    service_bus: ServiceBusConfiguration = Field(default_factory=ServiceBusConfiguration)
    event_hubs: EventHubsConfiguration = Field(default_factory=EventHubsConfiguration)
    retry: RetryConfiguration = Field(default_factory=RetryConfiguration)
    dead_letter_queue: DeadLetterQueueConfiguration = Field(default_factory=DeadLetterQueueConfiguration)


class FraudAlertMessage(BaseModel):
    """Fraud alert message for Service Bus"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    transaction_id: str = Field(..., description="Transaction identifier")
    score: float = Field(..., description="Risk score")
    action: str = Field(..., description="Recommended action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    user_id: str = Field(..., description="User identifier")
    account_id: str = Field(..., description="Account identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Correlation identifier")


class TransactionMessage(BaseModel):
    """Transaction message for Event Hubs"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    amount: float = Field(..., description="Transaction amount")
    merchant_name: str = Field(..., description="Merchant name")
    location: str = Field(..., description="Transaction location")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")
    user_id: str = Field(..., description="User identifier")
    account_id: str = Field(..., description="Account identifier")
    device_id: Optional[str] = Field(None, description="Device identifier")
    ip_address: Optional[str] = Field(None, description="IP address")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Correlation identifier")


class MessageEnvelope(BaseModel, Generic[T]):
    """Message envelope for tracking and correlation"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message identifier")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Correlation identifier")
    source: str = Field(..., description="Message source")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_type: str = Field(..., description="Message type")
    payload: T = Field(..., description="Message payload")
    headers: Dict[str, str] = Field(default_factory=dict, description="Message headers")
    retry_count: int = Field(0, description="Retry count")
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")


class MessageProcessingResult(BaseModel):
    """Result of message processing"""
    message_id: str = Field(..., description="Message identifier")
    status: MessageStatus = Field(..., description="Processing status")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retries")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")


class SubscriptionInfo(BaseModel):
    """Service Bus subscription information"""
    topic_name: str = Field(..., description="Topic name")
    subscription_name: str = Field(..., description="Subscription name")
    is_active: bool = Field(default=False, description="Whether subscription is active")
    message_count: int = Field(0, description="Current message count")
    dead_letter_count: int = Field(0, description="Dead letter message count")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class EventHubInfo(BaseModel):
    """Event Hub information"""
    event_hub_name: str = Field(..., description="Event Hub name")
    consumer_group: str = Field(..., description="Consumer group")
    partition_count: int = Field(0, description="Number of partitions")
    is_active: bool = Field(default=False, description="Whether Event Hub is active")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class MessagingStats(BaseModel):
    """Messaging statistics"""
    total_messages_sent: int = Field(0, description="Total messages sent")
    total_messages_received: int = Field(0, description="Total messages received")
    successful_messages: int = Field(0, description="Successful messages")
    failed_messages: int = Field(0, description="Failed messages")
    average_processing_time_ms: float = Field(0.0, description="Average processing time")
    peak_throughput_per_second: int = Field(0, description="Peak throughput per second")
    current_throughput_per_second: int = Field(0, description="Current throughput per second")
    uptime_hours: float = Field(0.0, description="Service uptime in hours")
    last_reset: datetime = Field(default_factory=datetime.utcnow, description="Last statistics reset")
