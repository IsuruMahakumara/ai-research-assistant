from typing import List, Dict, Any, Tuple
import logging

from app.llm import HFInferenceClient
from app.retriever import RAGRetriever
from app.agents.planner import ResearchPlanner

logger = logging.getLogger(__name__)


REASONING_PROMPT = """You are a research assistant. Answer the following question using the provided context. Be thorough and cite your sources.

Context:
{context}

Question: {question}

Provide a well-reasoned answer based on the context. If the context doesn't contain enough information, say so clearly.

Answer:"""


SYNTHESIS_PROMPT = """You are a research assistant synthesizing information to answer a complex question.

Original Question: {original_query}

Sub-questions and their answers:
{sub_answers}

Synthesize these answers into a comprehensive, coherent response to the original question. Make sure to:
1. Address all aspects of the original question
2. Highlight key findings
3. Note any gaps or uncertainties

Final Answer:"""


class ReasoningAgent:
    """Agent for multi-step reasoning and answer synthesis."""
    
    def __init__(self, retriever: RAGRetriever):
        self.llm_client = HFInferenceClient()
        self.retriever = retriever
        self.planner = ResearchPlanner()
    
    async def answer_single_question(
        self, 
        question: str, 
        max_sources: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Answer a single question using RAG."""
        # Retrieve relevant context
        context, results = await self.retriever.query_with_context(question, max_sources)
        
        if not context:
            return "I couldn't find relevant information to answer this question.", []
        
        # Generate answer
        prompt = REASONING_PROMPT.format(context=context, question=question)
        
        try:
            answer = await self.llm_client.generate(
                prompt,
                max_new_tokens=1024,
                temperature=0.5,
            )
            
            sources = [
                {
                    "content": doc.content,
                    "source": doc.source,
                    "relevance_score": score,
                    "metadata": doc.metadata,
                }
                for doc, score in results
            ]
            
            return answer.strip(), sources
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise
    
    async def reason_and_answer(
        self,
        query: str,
        max_sources: int = 5,
        use_decomposition: bool = True,
    ) -> Dict[str, Any]:
        """Perform multi-step reasoning to answer a complex query."""
        reasoning_steps = []
        all_sources = []
        
        if use_decomposition:
            # Step 1: Decompose the query
            reasoning_steps.append(f"Analyzing query: {query}")
            plan = await self.planner.create_research_plan(query)
            sub_questions = plan["sub_questions"]
            reasoning_steps.append(f"Decomposed into {len(sub_questions)} sub-questions")
            
            # Step 2: Answer each sub-question
            sub_answers = []
            for i, sub_q in enumerate(sub_questions, 1):
                reasoning_steps.append(f"Researching: {sub_q}")
                answer, sources = await self.answer_single_question(sub_q, max_sources)
                sub_answers.append({"question": sub_q, "answer": answer})
                all_sources.extend(sources)
                reasoning_steps.append(f"Found answer for sub-question {i}")
            
            # Step 3: Synthesize final answer
            reasoning_steps.append("Synthesizing final answer")
            
            sub_answers_text = "\n\n".join([
                f"Q: {sa['question']}\nA: {sa['answer']}"
                for sa in sub_answers
            ])
            
            synthesis_prompt = SYNTHESIS_PROMPT.format(
                original_query=query,
                sub_answers=sub_answers_text
            )
            
            final_answer = await self.llm_client.generate(
                synthesis_prompt,
                max_new_tokens=1024,
                temperature=0.5,
            )
            
        else:
            # Direct answering without decomposition
            reasoning_steps.append(f"Directly answering: {query}")
            final_answer, all_sources = await self.answer_single_question(query, max_sources)
        
        # Deduplicate sources by content
        seen_contents = set()
        unique_sources = []
        for source in all_sources:
            if source["content"] not in seen_contents:
                seen_contents.add(source["content"])
                unique_sources.append(source)
        
        # Calculate confidence based on source relevance
        if unique_sources:
            avg_relevance = sum(s["relevance_score"] for s in unique_sources) / len(unique_sources)
            confidence = min(avg_relevance, 1.0)
        else:
            confidence = 0.0
        
        return {
            "answer": final_answer.strip(),
            "reasoning_steps": reasoning_steps,
            "sources": unique_sources,
            "confidence": confidence,
        }

