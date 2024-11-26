import os
import json
import time
import psutil
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from collections import deque

@dataclass
class MetricPoint:
    """Represents a performance metric point"""
    name: str
    value: float
    timestamp: str
    tags: Dict[str, str]

@dataclass
class ResourceUsage:
    """Represents system resource usage"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    process_count: int
    thread_count: int
    timestamp: str

class PerformanceMonitor:
    """Monitors system performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_dir = os.path.join(
            os.getcwd(),
            '.metrics'
        )
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Recent metrics cache
        self.recent_metrics: Dict[str, deque] = {
            'operation_time': deque(maxlen=1000),
            'resource_usage': deque(maxlen=1000),
            'error_rate': deque(maxlen=1000)
        }
        
        # Resource thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_usage': 80.0,
            'process_count': 100,
            'thread_count': 1000
        }
        
        # Alert handlers
        self.alert_handlers: List[Callable[[str, Any], None]] = []
        
        # Process info
        self.process = psutil.Process()
    
    def track_operation(self, operation: str, duration: float, tags: Dict[str, str] = None):
        """Track operation duration"""
        try:
            metric = MetricPoint(
                name=f"operation.{operation}.duration",
                value=duration,
                timestamp=datetime.now().isoformat(),
                tags=tags or {}
            )
            
            # Add to cache
            self.recent_metrics['operation_time'].append(metric)
            
            # Write to disk
            self._write_metric(metric)
            
            # Check for slow operations
            if duration > 1.0:  # More than 1 second
                self._alert(
                    'slow_operation',
                    f"Slow operation detected: {operation} took {duration:.2f}s"
                )
                
        except Exception as e:
            self.logger.error(f"Error tracking operation: {e}")
    
    def track_error(self, error_type: str, error: str, tags: Dict[str, str] = None):
        """Track error occurrence"""
        try:
            metric = MetricPoint(
                name=f"error.{error_type}",
                value=1.0,
                timestamp=datetime.now().isoformat(),
                tags=tags or {}
            )
            
            # Add to cache
            self.recent_metrics['error_rate'].append(metric)
            
            # Write to disk
            self._write_metric(metric)
            
            # Calculate error rate
            recent_errors = len([
                m for m in self.recent_metrics['error_rate']
                if (datetime.now() - datetime.fromisoformat(m.timestamp)).total_seconds() < 300
            ])
            
            if recent_errors > 10:  # More than 10 errors in 5 minutes
                self._alert(
                    'high_error_rate',
                    f"High error rate detected: {recent_errors} errors in 5 minutes"
                )
                
        except Exception as e:
            self.logger.error(f"Error tracking error: {e}")
    
    async def monitor_resources(self):
        """Monitor system resources"""
        try:
            while True:
                try:
                    # Get resource usage
                    usage = ResourceUsage(
                        cpu_percent=psutil.cpu_percent(),
                        memory_percent=psutil.virtual_memory().percent,
                        disk_usage=psutil.disk_usage('/').percent,
                        process_count=len(psutil.pids()),
                        thread_count=self.process.num_threads(),
                        timestamp=datetime.now().isoformat()
                    )
                    
                    # Add to cache
                    self.recent_metrics['resource_usage'].append(usage)
                    
                    # Write to disk
                    self._write_metric(MetricPoint(
                        name="resource.usage",
                        value=1.0,
                        timestamp=usage.timestamp,
                        tags={
                            'cpu_percent': str(usage.cpu_percent),
                            'memory_percent': str(usage.memory_percent),
                            'disk_usage': str(usage.disk_usage),
                            'process_count': str(usage.process_count),
                            'thread_count': str(usage.thread_count)
                        }
                    ))
                    
                    # Check thresholds
                    self._check_thresholds(usage)
                    
                except Exception as e:
                    self.logger.error(f"Error monitoring resources: {e}")
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except asyncio.CancelledError:
            pass
    
    def add_alert_handler(self, handler: Callable[[str, Any], None]):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    def get_metrics(self, metric_type: str, duration: int = 300) -> List[MetricPoint]:
        """Get recent metrics"""
        try:
            now = datetime.now()
            return [
                m for m in self.recent_metrics[metric_type]
                if (now - datetime.fromisoformat(m.timestamp)).total_seconds() < duration
            ]
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return []
    
    def _write_metric(self, metric: MetricPoint):
        """Write metric to disk"""
        try:
            # Generate filename
            date = datetime.fromisoformat(metric.timestamp).strftime('%Y%m%d')
            filename = f"metrics_{date}.jsonl"
            path = os.path.join(self.metrics_dir, filename)
            
            # Write metric
            with open(path, 'a') as f:
                json.dump({
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp,
                    'tags': metric.tags
                }, f)
                f.write('\n')
                
        except Exception as e:
            self.logger.error(f"Error writing metric: {e}")
    
    def _check_thresholds(self, usage: ResourceUsage):
        """Check resource thresholds"""
        try:
            if usage.cpu_percent > self.thresholds['cpu_percent']:
                self._alert(
                    'high_cpu',
                    f"High CPU usage: {usage.cpu_percent}%"
                )
                
            if usage.memory_percent > self.thresholds['memory_percent']:
                self._alert(
                    'high_memory',
                    f"High memory usage: {usage.memory_percent}%"
                )
                
            if usage.disk_usage > self.thresholds['disk_usage']:
                self._alert(
                    'high_disk',
                    f"High disk usage: {usage.disk_usage}%"
                )
                
            if usage.process_count > self.thresholds['process_count']:
                self._alert(
                    'high_processes',
                    f"High process count: {usage.process_count}"
                )
                
            if usage.thread_count > self.thresholds['thread_count']:
                self._alert(
                    'high_threads',
                    f"High thread count: {usage.thread_count}"
                )
                
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _alert(self, alert_type: str, message: str):
        """Send alert to handlers"""
        try:
            for handler in self.alert_handlers:
                try:
                    handler(alert_type, message)
                except Exception as e:
                    self.logger.error(f"Error in alert handler: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")

class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: PerformanceMonitor, operation: str, tags: Dict[str, str] = None):
        self.monitor = monitor
        self.operation = operation
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.monitor.track_operation(self.operation, duration, self.tags)
            
            if exc_type:
                self.monitor.track_error(
                    'operation_error',
                    str(exc_val),
                    {
                        'operation': self.operation,
                        'error_type': exc_type.__name__,
                        **self.tags
                    }
                )
