"""
Developer Workflow Manager
------------------------

Implements a human-like developer workflow with research-first approach
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
    code_examples: List[str]
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
    code: Optional[str] = Field(None, description="Code implementation")
    explanation: str = Field(..., description="Explanation of the solution")
    considerations: List[str] = Field(default_factory=list, description="Important considerations")
    best_practices: List[str] = Field(default_factory=list, description="Best practices to follow")

class DevWorkflow:
    """Manages developer-like workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.research = ResearchManager()
        self.openai = OpenAIManager()
        
        # Default to mini model for cost efficiency
        self.openai.default_model = "gpt-o1-mini"
        
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
            'gpt-o1-preview': {
                'input': 0.000015,  # $15 per 1M tokens
                'output': 0.000060   # $60 per 1M tokens
            },
            'gpt-o1-mini': {
                'input': 0.000003,   # $3 per 1M tokens
                'output': 0.000012   # $12 per 1M tokens
            }
        }
        
        # Assume 50/50 split between input/output tokens
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens
        
        model_costs = costs.get(model, costs['gpt-o1-mini'])
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
            f"What are the latest best practices for implementing {task}?",
            f"Show code examples for {task} in Python",
            f"What are common pitfalls when implementing {task}?",
            f"What are the security considerations for {task}?"
        ]
        
        findings = []
        code_examples = []
        best_practices = []
        
        for query in queries:
            try:
                result = await self.research.research(query)
                
                # Extract code examples
                if "code examples" in query.lower():
                    code_blocks = self._extract_code_blocks(result.response)
                    code_examples.extend(code_blocks)
                
                # Extract best practices
                if "best practices" in query.lower():
                    practices = self._extract_best_practices(result.response)
                    best_practices.extend(practices)
                
                findings.append(result.response)
                
                # Update costs (Perplexity is generally cheaper than OpenAI)
                cost = self._estimate_cost(result.tokens, 'gpt-o1-mini') * 0.5
                self._update_costs(cost, 'research')
                
            except Exception as e:
                self.logger.error(f"Research error: {e}")
        
        return ResearchResult(
            query=task,
            findings=findings,
            code_examples=code_examples,
            best_practices=best_practices,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text"""
        code_blocks = []
        in_block = False
        current_block = []
        
        for line in text.split('\n'):
            if line.strip().startswith('```'):
                if in_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                in_block = not in_block
            elif in_block:
                current_block.append(line)
        
        return code_blocks
    
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
        # 4. Task involves security or critical functionality
        
        complexity_indicators = [
            'security',
            'optimize',
            'improve',
            'design',
            'architecture',
            'critical'
        ]
        
        return any(indicator in task.lower() for indicator in complexity_indicators)
    
    async def execute_task(self, task: str, context: Optional[str] = None) -> WorkflowResult:
        """Execute task using developer workflow"""
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
                self.logger.info("Using GPT-o1-mini for reasoning")
                
                # Prepare context from research
                research_context = (
                    f"Based on research:\n"
                    f"Findings: {research.findings}\n"
                    f"Best Practices: {research.best_practices}\n"
                    f"Code Examples: {research.code_examples}\n\n"
                    f"Additional Context: {context if context else ''}"
                )
                
                # Use GPT-o1-mini for reasoning
                result = await self.openai.get_structured_output(
                    query=task,
                    output_model=Solution,
                    research_context=research_context,
                    model="gpt-o1-mini"
                )
                
                # Update costs
                cost = self._estimate_cost(
                    len(str(result.response)) // 4,  # Rough token estimate
                    'gpt-o1-mini'
                )
                self._update_costs(cost, 'reasoning')
                
                solution = result.response
                model_used = 'gpt-o1-mini'
            else:
                self.logger.info("Using research results directly")
                solution = {
                    'code': research.code_examples[0] if research.code_examples else None,
                    'best_practices': research.best_practices,
                    'implementation_notes': research.findings
                }
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
