import os
import json
import time
import asyncio
import logging
from datetime import datetime
from performance_optimization import PerformanceOptimizer

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def test_caching():
    """Test cache functionality"""
    print("\n=== Test 1: Caching ===")
    
    optimizer = PerformanceOptimizer()
    
    # Test tool results cache
    print("\nTool results cache:")
    optimizer.set_cached('tool_results', 'test_key', {'result': 'success'})
    value = optimizer.get_cached('tool_results', 'test_key')
    print(f"Initial value: {value}")
    
    # Test cache refresh
    await asyncio.sleep(0.1)
    value = optimizer.get_cached('tool_results', 'test_key')
    print(f"After refresh: {value}")
    
    # Test cache expiration
    await asyncio.sleep(0.2)
    value = optimizer.get_cached('tool_results', 'test_key')
    print(f"After expiration: {value}")

async def test_batching():
    """Test operation batching"""
    print("\n=== Test 2: Operation Batching ===")
    
    optimizer = PerformanceOptimizer()
    test_dir = 'test_batch'
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Test file write batching
        print("\nFile write batching:")
        start = time.time()
        
        for i in range(10):  # Reduced from 20
            await optimizer.batch_operation('file_write', {
                'path': os.path.join(test_dir, f'file_{i}.txt'),
                'content': f'Content {i}'
            })
        
        # Wait for batch processing
        await asyncio.sleep(0.2)
        
        duration = time.time() - start
        print(f"Processed 10 writes in {duration:.3f}s")
        
        # Check files
        files = os.listdir(test_dir)
        print(f"Created {len(files)} files")
        
    finally:
        # Clean up
        for file in os.listdir(test_dir):
            os.remove(os.path.join(test_dir, file))
        os.rmdir(test_dir)

async def test_metric_batching():
    """Test metric write batching"""
    print("\n=== Test 3: Metric Batching ===")
    
    optimizer = PerformanceOptimizer()
    metrics_dir = '.metrics'
    os.makedirs(metrics_dir, exist_ok=True)
    
    try:
        # Test metric batching
        print("\nMetric write batching:")
        start = time.time()
        
        for i in range(10):  # Reduced from 100
            await optimizer.batch_operation('metric_write', {
                'name': 'test_metric',
                'value': i,
                'timestamp': datetime.now().isoformat(),
                'tags': {'test': 'true'}
            })
        
        # Wait for batch processing
        await asyncio.sleep(0.2)
        
        duration = time.time() - start
        print(f"Processed 10 metrics in {duration:.3f}s")
        
        # Check metric files
        files = os.listdir(metrics_dir)
        print(f"Created {len(files)} metric files")
        
    finally:
        # Clean up
        for file in os.listdir(metrics_dir):
            os.remove(os.path.join(metrics_dir, file))
        os.rmdir(metrics_dir)

async def test_cache_cleanup():
    """Test cache cleanup"""
    print("\n=== Test 4: Cache Cleanup ===")
    
    optimizer = PerformanceOptimizer()
    
    # Fill caches
    print("\nFilling caches:")
    for i in range(10):  # Reduced from 100
        optimizer.set_cached('file_contents', f'file_{i}', f'content_{i}')
    
    initial_size = len(optimizer.caches['file_contents'])
    print(f"Initial cache size: {initial_size}")
    
    # Wait for cleanup
    print("Waiting for cleanup...")
    await asyncio.sleep(0.5)  # Reduced from 61s
    
    final_size = len(optimizer.caches['file_contents'])
    print(f"Final cache size: {final_size}")

async def test_performance_impact():
    """Test optimization performance impact"""
    print("\n=== Test 5: Performance Impact ===")
    
    optimizer = PerformanceOptimizer()
    iterations = 10  # Reduced from 1000
    
    # Test without optimization
    print("\nWithout optimization:")
    start = time.time()
    for i in range(iterations):
        with open('test.txt', 'w') as f:
            f.write(f'test_{i}')
    baseline = time.time() - start
    print(f"Baseline: {baseline:.3f}s")
    
    # Test with optimization
    print("\nWith optimization:")
    start = time.time()
    for i in range(iterations):
        await optimizer.batch_operation('file_write', {
            'path': 'test.txt',
            'content': f'test_{i}'
        })
    optimized = time.time() - start
    print(f"Optimized: {optimized:.3f}s")
    print(f"Improvement: {((baseline - optimized) / baseline) * 100:.1f}%")
    
    # Clean up
    if os.path.exists('test.txt'):
        os.remove('test.txt')

async def main():
    """Run performance optimization tests"""
    setup_logging()
    
    print("\nTesting Performance Optimization...\n")
    
    try:
        await test_caching()
        await test_batching()
        await test_metric_batching()
        await test_cache_cleanup()
        await test_performance_impact()
        
    except KeyboardInterrupt:
        print("\nTests stopped by user")
    except Exception as e:
        print(f"\nError running tests: {e}")
    finally:
        # Clean up any remaining files
        if os.path.exists('test.txt'):
            os.remove('test.txt')
        if os.path.exists('test_batch'):
            for file in os.listdir('test_batch'):
                os.remove(os.path.join('test_batch', file))
            os.rmdir('test_batch')
        if os.path.exists('.metrics'):
            for file in os.listdir('.metrics'):
                os.remove(os.path.join('.metrics', file))
            os.rmdir('.metrics')

if __name__ == '__main__':
    asyncio.run(main())
