#!/usr/bin/env python3
"""
Test Model Router Implementation
"""

import asyncio
import logging
from assistant.model_router import ModelRouter, TaskType

async def test_model_router():
    """Test routing between Anthropic and OpenRouter APIs"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        router = ModelRouter()
        
        # Test cases
        test_cases = [
            {
                "name": "Vision Task",
                "task_type": TaskType.VISION,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What's in this image?"
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": "..."  # Add test image data
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "name": "System Task",
                "task_type": TaskType.SYSTEM,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant focused on technical documentation."
                    },
                    {
                        "role": "user",
                        "content": "How do I document a Python function?"
                    }
                ]
            },
            {
                "name": "Computer Use Task",
                "task_type": TaskType.COMPUTER_USE,
                "messages": [
                    {
                        "role": "user",
                        "content": "Open the calculator app"
                    }
                ]
            },
            {
                "name": "General Task",
                "task_type": TaskType.GENERAL,
                "messages": [
                    {
                        "role": "user",
                        "content": "What is the capital of France?"
                    }
                ]
            }
        ]
        
        # Run tests
        for test in test_cases:
            logger.info(f"\nTesting: {test['name']}")
            try:
                response = await router.route_request(
                    task_type=test['task_type'],
                    messages=test['messages']
                )
                logger.info(f"Response from model: {response.get('model', 'unknown')}")
                logger.info(f"First choice: {response.get('choices', [{}])[0].get('message', '')}")
                
            except Exception as e:
                logger.error(f"Error in {test['name']}: {e}")
        
        # Get usage stats
        stats = router.get_usage_stats()
        logger.info("\nUsage Statistics:")
        logger.info(f"Total Requests: {stats['total_requests']}")
        logger.info("Requests by Type:")
        for task_type, count in stats['requests_by_type'].items():
            logger.info(f"  {task_type}: {count}")
        logger.info("Requests by Model:")
        for model, count in stats['requests_by_model'].items():
            logger.info(f"  {model}: {count}")
            
    except Exception as e:
        logger.error(f"Test suite error: {e}")

if __name__ == '__main__':
    asyncio.run(test_model_router())
