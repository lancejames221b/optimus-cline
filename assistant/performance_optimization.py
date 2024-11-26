import os
import json
import time
import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from collections import deque, defaultdict
from functools import lru_cache

@dataclass
class CacheConfig:
    """Represents cache configuration"""
    max_size: int
    ttl: int  # Time to live in seconds
    refresh_on_access: bool

class PerformanceOptimizer:
    """Optimizes system performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Cache configuration
        self.cache_configs = {
            'tool_results': CacheConfig(1000, 300, True),
            'file_contents': CacheConfig(100, 60, False),
            'browser_screenshots': CacheConfig(50, 600, True)
        }
        
        # Cache storage
        self.caches: Dict[str, Dict[str, Any]] = {
            'tool_results': {},
            'file_contents': {},
            'browser_screenshots': {}
        }
        
        # Cache timestamps
        self.cache_times: Dict[str, Dict[str, float]] = {
            'tool_results': {},
            'file_contents': {},
            'browser_screenshots': {}
        }
        
        # Operation batching
        self.batch_size = 10
        self.batch_timeout = 0.1  # seconds
        self.pending_operations: Dict[str, List[Any]] = defaultdict(list)
        self.batch_timers: Dict[str, asyncio.Task] = {}
        
        # Resource pools
        self.browser_pool = deque(maxlen=5)
        self.connection_pool = deque(maxlen=10)
        
        # Start cache cleanup
        asyncio.create_task(self._cleanup_caches())
    
    def get_cached(self, cache_type: str, key: str) -> Optional[Any]:
        """Get cached value if valid"""
        try:
            # Check cache exists
            if cache_type not in self.caches:
                return None
            
            # Check key exists
            if key not in self.caches[cache_type]:
                return None
            
            # Check TTL
            timestamp = self.cache_times[cache_type].get(key, 0)
            if time.time() - timestamp > self.cache_configs[cache_type].ttl:
                # Expired
                del self.caches[cache_type][key]
                del self.cache_times[cache_type][key]
                return None
            
            # Get value
            value = self.caches[cache_type][key]
            
            # Refresh timestamp if configured
            if self.cache_configs[cache_type].refresh_on_access:
                self.cache_times[cache_type][key] = time.time()
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting cached value: {e}")
            return None
    
    def set_cached(self, cache_type: str, key: str, value: Any):
        """Set cached value"""
        try:
            # Check cache exists
            if cache_type not in self.caches:
                return
            
            # Check cache size
            if len(self.caches[cache_type]) >= self.cache_configs[cache_type].max_size:
                # Remove oldest entry
                oldest_key = min(
                    self.cache_times[cache_type].items(),
                    key=lambda x: x[1]
                )[0]
                del self.caches[cache_type][oldest_key]
                del self.cache_times[cache_type][oldest_key]
            
            # Set value
            self.caches[cache_type][key] = value
            self.cache_times[cache_type][key] = time.time()
            
        except Exception as e:
            self.logger.error(f"Error setting cached value: {e}")
    
    async def batch_operation(self, operation_type: str, operation: Any):
        """Add operation to batch"""
        try:
            # Add to pending
            self.pending_operations[operation_type].append(operation)
            
            # Start timer if needed
            if operation_type not in self.batch_timers:
                self.batch_timers[operation_type] = asyncio.create_task(
                    self._process_batch(operation_type)
                )
            
            # Process immediately if batch full
            if len(self.pending_operations[operation_type]) >= self.batch_size:
                await self._process_batch(operation_type)
                
        except Exception as e:
            self.logger.error(f"Error batching operation: {e}")
    
    async def _process_batch(self, operation_type: str):
        """Process batch of operations"""
        try:
            # Wait for timeout
            await asyncio.sleep(self.batch_timeout)
            
            # Get pending operations
            operations = self.pending_operations[operation_type]
            self.pending_operations[operation_type] = []
            
            # Clear timer
            if operation_type in self.batch_timers:
                del self.batch_timers[operation_type]
            
            # Process batch
            if operation_type == 'file_write':
                await self._batch_file_writes(operations)
            elif operation_type == 'browser_screenshot':
                await self._batch_screenshots(operations)
            elif operation_type == 'metric_write':
                await self._batch_metric_writes(operations)
                
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
    
    async def _batch_file_writes(self, operations: List[Any]):
        """Process batch of file writes"""
        try:
            # Group by directory
            by_dir = defaultdict(list)
            for op in operations:
                if not op.get('path'):
                    continue
                dir_path = os.path.dirname(op['path'])
                by_dir[dir_path].append(op)
            
            # Process each directory
            for dir_path, dir_ops in by_dir.items():
                if not dir_path:
                    continue
                    
                # Create directory
                os.makedirs(dir_path, exist_ok=True)
                
                # Write files
                for op in dir_ops:
                    if not op.get('path') or not op.get('content'):
                        continue
                    with open(op['path'], 'w') as f:
                        f.write(op['content'])
                        
        except Exception as e:
            self.logger.error(f"Error processing file writes: {e}")
    
    async def _batch_screenshots(self, operations: List[Any]):
        """Process batch of screenshots"""
        try:
            # Get browser from pool
            browser = None
            while self.browser_pool and not browser:
                browser = self.browser_pool.popleft()
                if not browser.connected:
                    browser = None
            
            if not browser:
                return
            
            try:
                # Take screenshots
                for op in operations:
                    if not op.get('path'):
                        continue
                    await browser.screenshot(op['path'])
            finally:
                # Return browser to pool
                self.browser_pool.append(browser)
                
        except Exception as e:
            self.logger.error(f"Error processing screenshots: {e}")
    
    async def _batch_metric_writes(self, operations: List[Any]):
        """Process batch of metric writes"""
        try:
            # Group by date
            by_date = defaultdict(list)
            for op in operations:
                if not op.get('timestamp'):
                    continue
                date = datetime.fromisoformat(op['timestamp']).strftime('%Y%m%d')
                by_date[date].append(op)
            
            # Process each date
            metrics_dir = os.path.join(os.getcwd(), '.metrics')
            os.makedirs(metrics_dir, exist_ok=True)
            
            for date, date_ops in by_date.items():
                # Generate filename
                filename = f"metrics_{date}.jsonl"
                path = os.path.join(metrics_dir, filename)
                
                # Write metrics
                with open(path, 'a') as f:
                    for op in date_ops:
                        json.dump(op, f)
                        f.write('\n')
                        
        except Exception as e:
            self.logger.error(f"Error processing metric writes: {e}")
    
    async def _cleanup_caches(self):
        """Clean up expired cache entries"""
        try:
            while True:
                # Check each cache
                for cache_type in self.caches:
                    config = self.cache_configs[cache_type]
                    times = self.cache_times[cache_type]
                    cache = self.caches[cache_type]
                    
                    # Find expired keys
                    now = time.time()
                    expired = [
                        key for key, timestamp in times.items()
                        if now - timestamp > config.ttl
                    ]
                    
                    # Remove expired entries
                    for key in expired:
                        del cache[key]
                        del times[key]
                
                # Wait before next cleanup
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error cleaning caches: {e}")

@lru_cache(maxsize=1000)
def cached_operation(operation_type: str, *args, **kwargs):
    """Cache operation results"""
    # Implementation depends on operation type
    pass
