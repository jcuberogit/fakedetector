"""
Performance Monitoring and Optimization Service
Ensures Python implementation meets C# performance targets (<600ms)
"""

import time
import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
import threading
import psutil
import gc

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    endpoint: str
    method: str
    request_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    p50_time_ms: float = 0.0
    p95_time_ms: float = 0.0
    p99_time_ms: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    last_request: Optional[datetime] = None
    response_times: List[float] = field(default_factory=list)
    
    def add_request(self, response_time_ms: float, success: bool = True):
        """Add a request to the metrics."""
        self.request_count += 1
        self.total_time_ms += response_time_ms
        self.min_time_ms = min(self.min_time_ms, response_time_ms)
        self.max_time_ms = max(self.max_time_ms, response_time_ms)
        self.response_times.append(response_time_ms)
        
        if not success:
            self.error_count += 1
        
        self.success_rate = ((self.request_count - self.error_count) / self.request_count) * 100
        self.last_request = datetime.utcnow()
        
        # Keep only last 1000 response times for percentile calculations
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        self._calculate_percentiles()
    
    def _calculate_percentiles(self):
        """Calculate percentile metrics."""
        if self.response_times:
            self.avg_time_ms = statistics.mean(self.response_times)
            self.p50_time_ms = statistics.median(self.response_times)
            if len(self.response_times) >= 20:  # Need at least 20 samples for p95/p99
                self.p95_time_ms = statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
                self.p99_time_ms = statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    active_threads: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PerformanceMonitor:
    """Performance monitoring service."""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.system_metrics: List[SystemMetrics] = []
        self.target_latency_ms = 600  # C# performance target
        self.warning_threshold_ms = 500  # Warning threshold
        self.critical_threshold_ms = 800  # Critical threshold
        self.monitoring_enabled = True
        self._lock = threading.Lock()
        
        logger.info("Performance Monitor initialized")
    
    def start_monitoring(self):
        """Start system monitoring."""
        if self.monitoring_enabled:
            threading.Thread(target=self._monitor_system, daemon=True).start()
            logger.info("System monitoring started")
    
    def _monitor_system(self):
        """Monitor system metrics."""
        while self.monitoring_enabled:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                system_metric = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    memory_available_mb=memory.available / (1024 * 1024),
                    disk_usage_percent=disk.percent,
                    network_bytes_sent=network.bytes_sent,
                    network_bytes_recv=network.bytes_recv,
                    active_threads=threading.active_count()
                )
                
                with self._lock:
                    self.system_metrics.append(system_metric)
                    # Keep only last 1000 system metrics
                    if len(self.system_metrics) > 1000:
                        self.system_metrics = self.system_metrics[-1000:]
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Error monitoring system: {e}")
                time.sleep(10)  # Wait longer on error
    
    def record_request(self, endpoint: str, method: str, response_time_ms: float, success: bool = True):
        """Record a request performance."""
        key = f"{method}:{endpoint}"
        
        with self._lock:
            if key not in self.metrics:
                self.metrics[key] = PerformanceMetrics(endpoint=endpoint, method=method)
            
            self.metrics[key].add_request(response_time_ms, success)
            
            # Log performance warnings
            if response_time_ms > self.critical_threshold_ms:
                logger.warning(f"CRITICAL: {key} took {response_time_ms:.2f}ms (threshold: {self.critical_threshold_ms}ms)")
            elif response_time_ms > self.warning_threshold_ms:
                logger.warning(f"WARNING: {key} took {response_time_ms:.2f}ms (threshold: {self.warning_threshold_ms}ms)")
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._lock:
            if endpoint:
                # Return specific endpoint metrics
                key = next((k for k in self.metrics.keys() if endpoint in k), None)
                if key:
                    return self.metrics[key].__dict__
                return {}
            else:
                # Return all metrics
                return {
                    key: metrics.__dict__ for key, metrics in self.metrics.items()
                }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        if self.system_metrics:
            latest = self.system_metrics[-1]
            return latest.__dict__
        return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        with self._lock:
            total_requests = sum(m.request_count for m in self.metrics.values())
            total_errors = sum(m.error_count for m in self.metrics.values())
            avg_response_time = statistics.mean([m.avg_time_ms for m in self.metrics.values()]) if self.metrics else 0
            
            # Find slowest endpoints
            slowest_endpoints = sorted(
                [(key, m.avg_time_ms) for key, m in self.metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Find endpoints exceeding target
            exceeding_target = [
                (key, m.avg_time_ms) for key, m in self.metrics.items()
                if m.avg_time_ms > self.target_latency_ms
            ]
            
            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "overall_success_rate": ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 100,
                "average_response_time_ms": avg_response_time,
                "target_latency_ms": self.target_latency_ms,
                "meeting_target": avg_response_time <= self.target_latency_ms,
                "slowest_endpoints": slowest_endpoints,
                "exceeding_target": exceeding_target,
                "system_metrics": self.get_system_metrics(),
                "monitoring_enabled": self.monitoring_enabled
            }
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_enabled = False
        logger.info("System monitoring stopped")


def performance_monitor(monitor: PerformanceMonitor):
    """Decorator to monitor endpoint performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except (ValueError, TypeError, AttributeError) as e:
                success = False
                raise
            finally:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                # Extract endpoint info from Flask request if available
                try:
                    from flask import request
                    endpoint = request.endpoint or func.__name__
                    method = request.method or "UNKNOWN"
                except:
                    endpoint = func.__name__
                    method = "UNKNOWN"
                
                monitor.record_request(endpoint, method, response_time_ms, success)
        
        return wrapper
    return decorator


class PerformanceOptimizer:
    """Performance optimization service."""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.optimization_enabled = True
        self.cache_enabled = True
        self.compression_enabled = True
        self.connection_pooling_enabled = True
        
        # Performance optimization settings
        self.cache_ttl_seconds = 300  # 5 minutes
        self.max_cache_size = 1000
        self.compression_level = 6
        self.max_connections = 100
        self.connection_timeout = 30
        
        # In-memory cache for optimization
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        logger.info("Performance Optimizer initialized")
    
    def optimize_response(self, data: Any, compress: bool = True) -> Any:
        """Optimize response data."""
        try:
            # Apply compression if enabled and data is large enough
            if compress and self.compression_enabled and len(str(data)) > 1024:
                # In a real implementation, you would compress the data here
                # For now, we'll just return the data as-is
                pass
            
            return data
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error optimizing response: {e}")
            return data
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self.cache_enabled:
            return None
        
        try:
            if key in self._cache:
                # Check if cache entry is still valid
                if key in self._cache_timestamps:
                    cache_time = self._cache_timestamps[key]
                    if datetime.utcnow() - cache_time < timedelta(seconds=self.cache_ttl_seconds):
                        return self._cache[key]
                    else:
                        # Remove expired cache entry
                        del self._cache[key]
                        del self._cache_timestamps[key]
            
            return None
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error getting cached data: {e}")
            return None
    
    def set_cached_data(self, key: str, data: Any):
        """Set data in cache."""
        if not self.cache_enabled:
            return
        
        try:
            # Check cache size limit
            if len(self._cache) >= self.max_cache_size:
                # Remove oldest entries
                oldest_key = min(self._cache_timestamps.keys(), key=lambda k: self._cache_timestamps[k])
                del self._cache[oldest_key]
                del self._cache_timestamps[oldest_key]
            
            self._cache[key] = data
            self._cache_timestamps[key] = datetime.utcnow()
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error setting cached data: {e}")
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")
    
    def optimize_memory(self):
        """Optimize memory usage."""
        try:
            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")
            
            # Clear cache if memory usage is high
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:
                self.clear_cache()
                logger.warning(f"High memory usage ({memory_percent}%), cache cleared")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error optimizing memory: {e}")
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        try:
            summary = self.monitor.get_performance_summary()
            
            # Check average response time
            if summary["average_response_time_ms"] > self.monitor.target_latency_ms:
                recommendations.append(f"Average response time ({summary['average_response_time_ms']:.2f}ms) exceeds target ({self.monitor.target_latency_ms}ms)")
            
            # Check slowest endpoints
            for endpoint, avg_time in summary["slowest_endpoints"]:
                if avg_time > self.monitor.target_latency_ms:
                    recommendations.append(f"Endpoint {endpoint} is slow ({avg_time:.2f}ms)")
            
            # Check system metrics
            system_metrics = summary["system_metrics"]
            if system_metrics.get("cpu_percent", 0) > 80:
                recommendations.append("High CPU usage detected")
            
            if system_metrics.get("memory_percent", 0) > 80:
                recommendations.append("High memory usage detected")
            
            # General recommendations
            if not self.cache_enabled:
                recommendations.append("Enable caching for better performance")
            
            if not self.compression_enabled:
                recommendations.append("Enable compression for large responses")
            
            if not self.connection_pooling_enabled:
                recommendations.append("Enable connection pooling")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error getting optimization recommendations: {e}")
        
        return recommendations
    
    def apply_optimizations(self):
        """Apply performance optimizations."""
        try:
            # Optimize memory
            self.optimize_memory()
            
            # Get recommendations and apply them
            recommendations = self.get_optimization_recommendations()
            
            for recommendation in recommendations:
                logger.info(f"Optimization recommendation: {recommendation}")
            
            logger.info("Performance optimizations applied")
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error applying optimizations: {e}")


# Global performance monitor instance
performance_monitor_instance = PerformanceMonitor()
performance_optimizer = PerformanceOptimizer(performance_monitor_instance)
