"""
Computer Use Workflow Manager
---------------------------

Implements a human-like computer use workflow with research-first approach
and cost-effective model usage.
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from .search import ResearchManager
from .openai_manager import OpenAIManager

@dataclass
class ResearchResult:
    """Result from research phase"""
    query: str
    findings: List[str]
    examples: List[str]
    best_practices: List[str]
    timestamp: str

@dataclass
class WorkflowResult:
    """Result from workflow execution"""
    task: str
    research: Optional[ResearchResult]
    solution: Any
    model_used: str
    cost_estimate: float
    timestamp: str

class Solution(BaseModel):
    """Model for solution output"""
    steps: List[str] = Field(..., description="Steps to accomplish the task")
    explanation: str = Field(..., description="Explanation of the solution")
    considerations: List[str] = Field(default_factory=list, description="Important considerations")
    best_practices: List[str] = Field(default_factory=list, description="Best practices to follow")
    code: Optional[str] = Field(None, description="Code implementation if needed")
    commands: Optional[List[str]] = Field(None, description="System commands if needed")

class ComputerWorkflow:
    """Manages human-like computer use workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.research = ResearchManager()
        self.openai = OpenAIManager()
        
        # Default to gpt-4o-mini for cost efficiency
        self.openai.default_model = "gpt-4o-mini"
        
        # Knowledge cache
        self.knowledge_base = {}
        
        # Cost tracking
        self.costs = {
            'research': 0.0,
            'reasoning': 0.0,
            'total': 0.0
        }
    
    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost based on tokens and model"""
        costs = {
            'gpt-4o-mini': {
                'input': 0.000003,  # $3 per 1M tokens
                'output': 0.000012   # $12 per 1M tokens
            },
            'gpt-4o': {
                'input': 0.000015,   # $15 per 1M tokens
                'output': 0.000060   # $60 per 1M tokens
            }
        }
        
        # Assume 50/50 split between input/output tokens
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens
        
        model_costs = costs.get(model, costs['gpt-4o-mini'])
        return (
            input_tokens * model_costs['input'] +
            output_tokens * model_costs['output']
        )
    
    def _update_costs(self, amount: float, category: str):
        """Update cost tracking"""
        self.costs[category] += amount
        self.costs['total'] += amount
    
    async def _research_task(self, task: str) -> ResearchResult:
        """Research task using Perplexity"""
        # Generate research queries
        queries = [
            f"What are the best ways to accomplish: {task}?",
            f"Show examples of how to do: {task}",
            f"What are common mistakes to avoid when doing: {task}?",
            f"What are important considerations for: {task}?"
        ]
        
        findings = []
        examples = []
        best_practices = []
        
        for query in queries:
            try:
                result = await self.research.research(query)
                
                # Extract examples
                if "examples" in query.lower():
                    examples.extend(self._extract_examples(result.response))
                
                # Extract best practices
                if "best ways" in query.lower() or "considerations" in query.lower():
                    practices = self._extract_best_practices(result.response)
                    best_practices.extend(practices)
                
                findings.append(result.response)
                
                # Update costs (Perplexity is generally cheaper than OpenAI)
                cost = self._estimate_cost(result.tokens, 'gpt-4o-mini') * 0.5
                self._update_costs(cost, 'research')
                
            except Exception as e:
                self.logger.error(f"Research error: {e}")
        
        return ResearchResult(
            query=task,
            findings=findings,
            examples=examples,
            best_practices=best_practices,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_examples(self, text: str) -> List[str]:
        """Extract examples from text"""
        examples = []
        in_example = False
        current_example = []
        
        for line in text.split('\n'):
            if line.strip().startswith('```'):
                if in_example:
                    examples.append('\n'.join(current_example))
                    current_example = []
                in_example = not in_example
            elif in_example:
                current_example.append(line)
            elif line.strip().startswith(('Example:', '- Example:', '* Example:')):
                examples.append(line.split(':', 1)[1].strip())
        
        return examples
    
    def _extract_best_practices(self, text: str) -> List[str]:
        """Extract best practices from text"""
        practices = []
        for line in text.split('\n'):
            line = line.strip()
            # Look for bullet points or numbered items
            if line.startswith(('- ', '* ', '• ', '1.', '2.', '3.')):
                practices.append(line)
        return practices
    
    def _should_use_reasoning(self, task: str, research: ResearchResult) -> bool:
        """Determine if reasoning is needed"""
        # Use reasoning if:
        # 1. Task is complex (multiple steps or requirements)
        # 2. Research found conflicting information
        # 3. Task requires combining multiple pieces of information
        # 4. Task involves system changes or critical operations
        
        complexity_indicators = [
            'security',
            'optimize',
            'improve',
            'design',
            'configure',
            'setup',
            'install',
            'manage',
            'organize',
            'automate',
            'critical'
        ]
        
        return (
            any(indicator in task.lower() for indicator in complexity_indicators) or
            len(research.examples) > 2 or  # Multiple approaches found
            any('warning' in f.lower() or 'caution' in f.lower() for f in research.findings)  # Safety concerns
        )
    
    async def execute_task(self, task: str, context: Optional[str] = None) -> WorkflowResult:
        """Execute task using computer workflow"""
        try:
            # Check knowledge base first
            if task in self.knowledge_base:
                self.logger.info("Using cached knowledge")
                research = self.knowledge_base[task]
            else:
                # Research first
                self.logger.info("Researching task")
                research = await self._research_task(task)
                self.knowledge_base[task] = research
            
            # Determine if reasoning is needed
            if self._should_use_reasoning(task, research):
                self.logger.info("Using GPT-4o-mini for reasoning")
                
                # Prepare context from research
                research_context = (
                    f"Based on research:\n"
                    f"Findings: {research.findings}\n"
                    f"Examples: {research.examples}\n"
                    f"Best Practices: {research.best_practices}\n\n"
                    f"Additional Context: {context if context else ''}\n\n"
                    "You must provide a solution with:\n"
                    "1. Clear steps to accomplish the task\n"
                    "2. Explanation of the approach\n"
                    "3. Important considerations\n"
                    "4. Best practices to follow\n"
                    "5. Code or commands if needed\n\n"
                    "Format your response as a JSON object with these fields:\n"
                    "{\n"
                    '  "steps": ["Step 1", "Step 2", ...],\n'
                    '  "explanation": "Detailed explanation here",\n'
                    '  "considerations": ["Consider 1", "Consider 2", ...],\n'
                    '  "best_practices": ["Practice 1", "Practice 2", ...],\n'
                    '  "code": "Code here if needed",\n'
                    '  "commands": ["Command 1", "Command 2", ...]\n'
                    "}"
                )
                
                # Use GPT-4o-mini for reasoning
                result = await self.openai.get_structured_output(
                    query=task,
                    output_model=Solution,
                    research_context=research_context,
                    model="gpt-4o-mini"
                )
                
                # Update costs
                cost = self._estimate_cost(
                    len(str(result.response)) // 4,  # Rough token estimate
                    'gpt-4o-mini'
                )
                self._update_costs(cost, 'reasoning')
                
                solution = result.response
                model_used = 'gpt-4o-mini'
            else:
                self.logger.info("Using research results directly")
                # Create a Solution object from research results
                solution = Solution(
                    steps=research.examples[0].split('\n') if research.examples else ["No specific steps found"],
                    explanation=research.findings[0] if research.findings else "No detailed explanation available",
                    considerations=research.best_practices,
                    best_practices=research.best_practices,
                    code=None,
                    commands=None
                )
                model_used = 'research-only'
            
            return WorkflowResult(
                task=task,
                research=research,
                solution=solution,
                model_used=model_used,
                cost_estimate=self.costs['total'],
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Workflow error: {e}")
            raise
    
    def get_costs(self) -> Dict[str, float]:
        """Get current cost breakdown"""
        return self.costs.copy()
    
    def clear_knowledge_base(self):
        """Clear cached knowledge"""
        self.knowledge_base.clear()
