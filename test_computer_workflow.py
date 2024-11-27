#!/usr/bin/env python3
"""
Test Computer Workflow
--------------------

Test the human-like computer use workflow with various tasks.
"""

import asyncio
from assistant.computer_workflow import ComputerWorkflow

async def main():
    """Test computer workflow"""
    workflow = ComputerWorkflow()
    
    # Test cases
    tasks = [
        # Development task
        {
            'task': "How to implement a basic rate limiter in Python",
            'context': "Need a simple rate limiter for API requests"
        },
        
        # System task
        {
            'task': "How to organize files by date and type",
            'context': "Need to clean up Downloads folder"
        },
        
        # Communication task
        {
            'task': "How to set up email filters in Gmail",
            'context': "Want to automatically organize incoming emails"
        },
        
        # Research task
        {
            'task': "Find information about M2 Mac performance",
            'context': "Considering upgrade from Intel Mac"
        },
        
        # Routine task
        {
            'task': "How to schedule automatic backups",
            'context': "Need daily backups of important files"
        },
        
        # Complex task
        {
            'task': "Set up a development environment for Python",
            'context': "Need VSCode, Python, Git, and virtual environments"
        }
    ]
    
    print("Testing computer workflow with various tasks...\n")
    
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
                
                print("\nExamples:")
                for i, example in enumerate(result.research.examples, 1):
                    print(f"\nExample {i}:")
                    print(example)
            print("-" * 80)
            
            print("\nSolution:")
            print("-" * 80)
            if isinstance(result.solution, dict):
                if result.solution.get('steps'):
                    print("\nSteps:")
                    for step in result.solution['steps']:
                        print(f"- {step}")
                
                if result.solution.get('explanation'):
                    print("\nExplanation:")
                    print(result.solution['explanation'])
                
                if result.solution.get('considerations'):
                    print("\nConsiderations:")
                    for consideration in result.solution['considerations']:
                        print(f"- {consideration}")
                
                if result.solution.get('code'):
                    print("\nCode:")
                    print(result.solution['code'])
                
                if result.solution.get('commands'):
                    print("\nCommands:")
                    for cmd in result.solution['commands']:
                        print(f"$ {cmd}")
            else:
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
