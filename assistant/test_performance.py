import os
import json
import time
import asyncio
import logging
from datetime import datetime
from performance_monitor import PerformanceMonitor, OperationTimer

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_operation_tracking():
    """Test operation tracking"""
    print("\n=== Test 1: Operation Tracking ===")
    
    monitor = PerformanceMonitor()
    
    # Test fast operation
    with OperationTimer(monitor, 'fast_operation', {'type': 'test'}):
        # Simulate fast operation
        await asyncio.sleep(0.1)
    
    # Test slow operation
    with OperationTimer(monitor, 'slow_operation', {'type': 'test'}):
        # Simulate slow operation
        await asyncio.sleep(1.5)
    
    # Get metrics
    metrics = monitor.get_metrics('operation_time')
    
    print("\nOperation metrics:")
    for metric in metrics:
        print(f"- {metric.name}: {metric.value:.3f}s")
        print(f"  Tags: {metric.tags}")

async def test_error_tracking():
    """Test error tracking"""
    print("\n=== Test 2: Error Tracking ===")
    
    monitor = PerformanceMonitor()
    
    # Track some errors
    for i in range(5):
        monitor.track_error(
            'test_error',
            f'Test error {i}',
            {'severity': 'low' if i < 3 else 'high'}
        )
    
    # Get metrics
    metrics = monitor.get_metrics('error_rate')
    
    print("\nError metrics:")
    for metric in metrics:
        print(f"- {metric.name}")
        print(f"  Tags: {metric.tags}")

async def test_resource_monitoring():
    """Test resource monitoring"""
    print("\n=== Test 3: Resource Monitoring ===")
    
    monitor = PerformanceMonitor()
    alerts = []
    
    def alert_handler(alert_type: str, message: str):
        alerts.append((alert_type, message))
        print(f"\nAlert: {alert_type} - {message}")
    
    monitor.add_alert_handler(alert_handler)
    
    # Start resource monitoring
    monitor_task = asyncio.create_task(monitor.monitor_resources())
    
    try:
        # Wait for some metrics
        await asyncio.sleep(10)
        
        # Get metrics
        metrics = monitor.get_metrics('resource_usage')
        
        print("\nResource metrics:")
        for metric in metrics:
            print(f"- {metric.name}")
            print(f"  Tags: {metric.tags}")
        
        print("\nAlerts received:", len(alerts))
        
    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

async def test_metric_storage():
    """Test metric storage"""
    print("\n=== Test 4: Metric Storage ===")
    
    monitor = PerformanceMonitor()
    
    # Generate some metrics
    operations = ['read', 'write', 'process']
    for op in operations:
        with OperationTimer(monitor, op, {'type': 'test'}):
            await asyncio.sleep(0.2)
    
    # Check metric files
    metrics_dir = os.path.join(os.getcwd(), '.metrics')
    metric_files = os.listdir(metrics_dir)
    
    print("\nMetric files:")
    for filename in metric_files:
        path = os.path.join(metrics_dir, filename)
        with open(path) as f:
            metrics = [json.loads(line) for line in f]
            print(f"- {filename}: {len(metrics)} metrics")

async def test_performance_impact():
    """Test monitoring performance impact"""
    print("\n=== Test 5: Performance Impact ===")
    
    monitor = PerformanceMonitor()
    iterations = 1000
    
    # Test without monitoring
    start = time.time()
    for i in range(iterations):
        await asyncio.sleep(0)
    baseline = time.time() - start
    
    # Test with monitoring
    start = time.time()
    for i in range(iterations):
        with OperationTimer(monitor, 'noop', {'iteration': str(i)}):
            await asyncio.sleep(0)
    monitored = time.time() - start
    
    print("\nPerformance comparison:")
    print(f"Baseline: {baseline:.3f}s")
    print(f"Monitored: {monitored:.3f}s")
    print(f"Overhead: {((monitored - baseline) / baseline) * 100:.1f}%")

async def main():
    """Run performance monitoring tests"""
    setup_logging()
    
    print("\nTesting Performance Monitor...\n")
    
    try:
        await test_operation_tracking()
        await test_error_tracking()
        await test_resource_monitoring()
        await test_metric_storage()
        await test_performance_impact()
        
    except KeyboardInterrupt:
        print("\nTests stopped by user")
    except Exception as e:
        print(f"\nError running tests: {e}")

if __name__ == '__main__':
    asyncio.run(main())
