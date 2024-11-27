#!/usr/bin/env python3
"""
Test Model Router
---------------

Test routing tasks to appropriate AI models.
"""

import asyncio
from assistant.model_router import ModelRouter

async def main():
    """Test model router functionality"""
    router = ModelRouter()
    
    # Test cases
    tasks = [
        # App launch tasks (should use OpenAI)
        {
            'task': "Open Chrome and go to gmail.com",
            'context': None,
            'expected_model': 'openai',
            'expected_type': 'app_launch'
        },
        
        # Web search tasks (should use Perplexity)
        {
            'task': "What's the weather like in San Francisco?",
            'context': "Focus on current weather conditions",
            'expected_model': 'perplexity',
            'expected_type': 'web_search'
        },
        {
            'task': "Find information about Python async programming",
            'context': "Focus on technical documentation",
            'expected_model': 'perplexity',
            'expected_type': 'web_search'
        },
        
        # System commands (should use OpenAI)
        {
            'task': "Show me the files in my downloads folder",
            'context': None,
            'expected_model': 'openai',
            'expected_type': 'system_command'
        },
        
        # General queries (should try Perplexity first)
        {
            'task': "What's the capital of France?",
            'context': "Provide factual information",
            'expected_model': 'perplexity',
            'expected_type': 'general_query'
        }
    ]
    
    print("Testing model router with various tasks...\n")
    
    for test in tasks:
        print(f"Task: {test['task']}")
        print(f"Expected model: {test['expected_model']}")
        print(f"Expected type: {test['expected_type']}\n")
        
        try:
            result = await router.execute_task(
                task=test['task'],
                context=test['context']
            )
            
            print(f"Model used: {result.model_used}")
            print(f"Task type: {result.task_type}")
            
            # Verify model selection
            if result.model_used == test['expected_model']:
                print("✓ Correct model selected")
            else:
                print(f"✗ Wrong model selected (expected {test['expected_model']})")
            
            # Verify task type
            if result.task_type == test['expected_type']:
                print("✓ Correct task type detected")
            else:
                print(f"✗ Wrong task type detected (expected {test['expected_type']})")
            
            print("\nResult:")
            print("-" * 80)
            print(result.result)
            print("-" * 80)
            
            if result.error:
                print(f"Error: {result.error}")
            print()
            
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Show performance metrics
    print("Performance Metrics:")
    metrics = router.get_metrics()
    for model, stats in metrics.items():
        print(f"\n{model.upper()}:")
        print(f"Success rate: {stats['success_rate']:.2%}")
        print(f"Total calls: {stats['total_calls']}")
        print(f"Average latency: {stats['average_latency']:.2f}s")

if __name__ == '__main__':
    asyncio.run(main())
