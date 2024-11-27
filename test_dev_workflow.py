#!/usr/bin/env python3
"""
Test Developer Workflow
---------------------

Test the developer-like workflow with research-first approach.
"""

import asyncio
from assistant.dev_workflow import DevWorkflow

async def main():
    """Test developer workflow"""
    workflow = DevWorkflow()
    
    # Test cases
    tasks = [
        # Simple task (should use research only)
        {
            'task': "How to implement a basic rate limiter in Python",
            'context': "Need a simple rate limiter for API requests"
        },
        
        # Complex task (should use reasoning)
        {
            'task': "Design a secure authentication system with JWT tokens",
            'context': "Need to implement user authentication for a web API"
        },
        
        # Optimization task (should use reasoning)
        {
            'task': "Optimize PostgreSQL queries for large datasets",
            'context': "Database queries are slow with 1M+ records"
        },
        
        # Simple utility task (should use research only)
        {
            'task': "How to parse CSV files in Python",
            'context': "Need to read and process CSV data"
        }
    ]
    
    print("Testing developer workflow...\n")
    
    for test in tasks:
        print(f"Task: {test['task']}")
        print(f"Context: {test['context']}\n")
        
        try:
            result = await workflow.execute_task(
                task=test['task'],
                context=test['context']
            )
            
            print("Research Results:")
            print("-" * 80)
            if result.research:
                print("Best Practices:")
                for practice in result.research.best_practices:
                    print(f"- {practice}")
                
                print("\nCode Examples:")
                for i, code in enumerate(result.research.code_examples, 1):
                    print(f"\nExample {i}:")
                    print(code)
            print("-" * 80)
            
            print("\nSolution:")
            print("-" * 80)
            print(result.solution)
            print("-" * 80)
            
            print(f"\nModel Used: {result.model_used}")
            print(f"Cost Estimate: ${result.cost_estimate:.4f}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Show total costs
    print("Cost Breakdown:")
    costs = workflow.get_costs()
    for category, amount in costs.items():
        print(f"{category.title()}: ${amount:.4f}")

if __name__ == '__main__':
    asyncio.run(main())
