from typing import List, Dict, Any
import logging

from app.llm import HFInferenceClient

logger = logging.getLogger(__name__)


PLANNING_PROMPT = """You are a research planning assistant. Given a research question, break it down into smaller, actionable sub-questions that can be answered independently.

Research Question: {query}

Provide a list of 2-5 sub-questions that would help answer the main question comprehensively. Format your response as a numbered list.

Sub-questions:"""


class ResearchPlanner:
    """Agent for planning research queries by decomposing them into sub-questions."""
    
    def __init__(self):
        self.llm_client = HFInferenceClient()
    
    async def decompose_query(self, query: str) -> List[str]:
        """Decompose a complex research query into sub-questions."""
        prompt = PLANNING_PROMPT.format(query=query)
        
        try:
            response = await self.llm_client.generate(
                prompt,
                max_new_tokens=512,
                temperature=0.3,
            )
            
            # Parse numbered list from response
            sub_questions = self._parse_numbered_list(response)
            
            if not sub_questions:
                # Fallback: return original query
                return [query]
            
            logger.info(f"Decomposed query into {len(sub_questions)} sub-questions")
            return sub_questions
            
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            return [query]
    
    def _parse_numbered_list(self, text: str) -> List[str]:
        """Parse a numbered list from LLM output."""
        lines = text.strip().split("\n")
        questions = []
        
        for line in lines:
            line = line.strip()
            # Match patterns like "1.", "1)", "1:", etc.
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove numbering/bullets
                for sep in [".", ")", ":", "-"]:
                    if sep in line[:3]:
                        line = line.split(sep, 1)[-1].strip()
                        break
                if line:
                    questions.append(line)
        
        return questions
    
    async def create_research_plan(self, query: str) -> Dict[str, Any]:
        """Create a full research plan with sub-questions and strategy."""
        sub_questions = await self.decompose_query(query)
        
        return {
            "original_query": query,
            "sub_questions": sub_questions,
            "strategy": "sequential",  # Could be enhanced with parallel/iterative strategies
            "estimated_steps": len(sub_questions) + 1,  # +1 for synthesis
        }

