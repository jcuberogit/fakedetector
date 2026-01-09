"""
Performance Models for Fraud Detection Agent
Pydantic models for performance monitoring and optimization
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Performance metrics for monitoring."""
    endpoint: str = Field(description="API endpoint name")
    method: str = Field(description="HTTP method")
    request_count: int = Field(default=0, description="Total number of requests")
    total_time_ms: float = Field(default=0.0, description="Total processing time in milliseconds")
    min_time_ms: float = Field(default=0.0, description="Minimum response time in milliseconds")
    max_time_ms: float = Field(default=0.0, description="Maximum response time in milliseconds")
    avg_time_ms: float = Field(default=0.0, description="Average response time in milliseconds")
    p50_time_ms: float = Field(default=0.0, description="50th percentile response time")
    p95_time_ms: float = Field(default=0.0, description="95th percentile response time")
    p99_time_ms: float = Field(default=0.0, description="99th percentile response time")
    error_count: int = Field(default=0, description="Number of failed requests")
    success_rate: float = Field(default=100.0, description="Success rate percentage")
    last_request: Optional[datetime] = Field(default=None, description="Timestamp of last request")


class SystemMetrics(BaseModel):
    """System performance metrics."""
    cpu_percent: float = Field(default=0.0, description="CPU usage percentage")
    memory_percent: float = Field(default=0.0, description="Memory usage percentage")
    memory_used_mb: float = Field(default=0.0, description="Memory used in MB")
    memory_available_mb: float = Field(default=0.0, description="Available memory in MB")
    disk_usage_percent: float = Field(default=0.0, description="Disk usage percentage")
    network_bytes_sent: int = Field(default=0, description="Network bytes sent")
    network_bytes_recv: int = Field(default=0, description="Network bytes received")
    active_threads: int = Field(default=0, description="Number of active threads")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")


class PerformanceSummary(BaseModel):
    """Performance summary for the system."""
    total_requests: int = Field(description="Total number of requests processed")
    total_errors: int = Field(description="Total number of errors")
    overall_success_rate: float = Field(description="Overall success rate percentage")
    average_response_time_ms: float = Field(description="Average response time in milliseconds")
    target_latency_ms: int = Field(default=600, description="Target latency in milliseconds")
    meeting_target: bool = Field(description="Whether the system is meeting performance targets")
    slowest_endpoints: List[tuple] = Field(default_factory=list, description="Slowest endpoints")
    exceeding_target: List[tuple] = Field(default_factory=list, description="Endpoints exceeding target")
    system_metrics: Dict[str, Any] = Field(default_factory=dict, description="Current system metrics")
    monitoring_enabled: bool = Field(default=True, description="Whether monitoring is enabled")


class PerformanceOptimizationRequest(BaseModel):
    """Request for performance optimization."""
    enable_caching: bool = Field(default=True, description="Enable response caching")
    enable_compression: bool = Field(default=True, description="Enable response compression")
    enable_connection_pooling: bool = Field(default=True, description="Enable connection pooling")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    max_cache_size: int = Field(default=1000, description="Maximum cache size")
    compression_level: int = Field(default=6, description="Compression level")
    max_connections: int = Field(default=100, description="Maximum connections")
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")


class PerformanceOptimizationResponse(BaseModel):
    """Response for performance optimization."""
    success: bool = Field(description="Whether optimization was successful")
    message: str = Field(description="Optimization result message")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    applied_optimizations: List[str] = Field(default_factory=list, description="Applied optimizations")
    performance_impact: Dict[str, Any] = Field(default_factory=dict, description="Performance impact metrics")


class PerformanceTestRequest(BaseModel):
    """Request for performance testing."""
    endpoint: str = Field(description="Endpoint to test")
    method: str = Field(default="GET", description="HTTP method")
    iterations: int = Field(default=100, description="Number of test iterations")
    concurrent_requests: int = Field(default=10, description="Number of concurrent requests")
    test_data: Optional[Dict[str, Any]] = Field(default=None, description="Test data for POST/PUT requests")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")


class PerformanceTestResponse(BaseModel):
    """Response for performance testing."""
    success: bool = Field(description="Whether the test was successful")
    endpoint: str = Field(description="Tested endpoint")
    method: str = Field(description="HTTP method used")
    iterations: int = Field(description="Number of test iterations")
    concurrent_requests: int = Field(description="Number of concurrent requests")
    total_time_ms: float = Field(description="Total test time in milliseconds")
    average_response_time_ms: float = Field(description="Average response time in milliseconds")
    min_response_time_ms: float = Field(description="Minimum response time in milliseconds")
    max_response_time_ms: float = Field(description="Maximum response time in milliseconds")
    p50_response_time_ms: float = Field(description="50th percentile response time")
    p95_response_time_ms: float = Field(description="95th percentile response time")
    p99_response_time_ms: float = Field(description="99th percentile response time")
    success_rate: float = Field(description="Success rate percentage")
    error_count: int = Field(description="Number of errors")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    meets_target: bool = Field(description="Whether the endpoint meets performance targets")
    recommendations: List[str] = Field(default_factory=list, description="Performance recommendations")


class PerformanceAlert(BaseModel):
    """Performance alert model."""
    alert_id: str = Field(description="Unique alert identifier")
    alert_type: str = Field(description="Type of alert (warning, critical, info)")
    endpoint: str = Field(description="Endpoint that triggered the alert")
    message: str = Field(description="Alert message")
    threshold_value: float = Field(description="Threshold value that was exceeded")
    actual_value: float = Field(description="Actual value that triggered the alert")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    resolved: bool = Field(default=False, description="Whether the alert has been resolved")
    resolution_timestamp: Optional[datetime] = Field(default=None, description="Alert resolution timestamp")


class PerformanceReport(BaseModel):
    """Performance report model."""
    report_id: str = Field(description="Unique report identifier")
    report_type: str = Field(description="Type of report (daily, weekly, monthly)")
    start_time: datetime = Field(description="Report start time")
    end_time: datetime = Field(description="Report end time")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation time")
    summary: PerformanceSummary = Field(description="Performance summary")
    endpoint_metrics: Dict[str, PerformanceMetrics] = Field(default_factory=dict, description="Endpoint-specific metrics")
    system_metrics_history: List[SystemMetrics] = Field(default_factory=list, description="System metrics history")
    alerts: List[PerformanceAlert] = Field(default_factory=list, description="Performance alerts")
    recommendations: List[str] = Field(default_factory=list, description="Performance recommendations")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Optimization suggestions")


class PerformanceConfiguration(BaseModel):
    """Performance configuration model."""
    target_latency_ms: int = Field(default=600, description="Target latency in milliseconds")
    warning_threshold_ms: int = Field(default=500, description="Warning threshold in milliseconds")
    critical_threshold_ms: int = Field(default=800, description="Critical threshold in milliseconds")
    monitoring_enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    alerting_enabled: bool = Field(default=True, description="Whether alerting is enabled")
    auto_optimization_enabled: bool = Field(default=False, description="Whether auto-optimization is enabled")
    cache_enabled: bool = Field(default=True, description="Whether caching is enabled")
    compression_enabled: bool = Field(default=True, description="Whether compression is enabled")
    connection_pooling_enabled: bool = Field(default=True, description="Whether connection pooling is enabled")
    max_cache_size: int = Field(default=1000, description="Maximum cache size")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")
    compression_level: int = Field(default=6, description="Compression level")
    max_connections: int = Field(default=100, description="Maximum connections")
    connection_timeout: int = Field(default=30, description="Connection timeout in seconds")
    monitoring_interval_seconds: int = Field(default=5, description="System monitoring interval")
    report_generation_enabled: bool = Field(default=True, description="Whether report generation is enabled")
    report_retention_days: int = Field(default=30, description="Report retention period in days")
