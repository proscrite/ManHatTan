# app/agent/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional

from app.agent.nodes import (
    retrieve_context_node,
    evaluate_context_node, 
    synthesize_exercise_node, 
    generate_from_scratch_node
)

# --- 1. State Definition ---
class AgentState(TypedDict):
    vocab_id: str
    target_word: str
    target_lang: str
    native_lang: str
    fsrs_difficulty: float
    
    # Fluency Guardrails
    cefr_level: str
    grammar_rules: str
    
    # Execution Context
    retrieved_contexts: List[Dict[str, Any]]
    is_context_valid: bool
    relevance_score: float
    generated_payload: Optional[Dict[str, Any]]

# --- 2. Conditional Routing ---
def route_after_evaluation(state: AgentState) -> str:
    """
    Routes to the synthesizer if Milvus context is excellent,
    otherwise falls back to generating from scratch.
    """
    if state.get("is_context_valid", False):
        return "synthesize"
    return "generate_fallback"

# --- 3. Graph Compilation ---
def build_tier1_agent():
    """
    Compiles the Tier-1 Evaluative RAG State Machine.
    """
    workflow = StateGraph(AgentState)
    
    # Add Execution Nodes
    workflow.add_node("retrieve", retrieve_context_node)
    workflow.add_node("evaluate", evaluate_context_node)
    workflow.add_node("synthesize", synthesize_exercise_node)
    workflow.add_node("generate_fallback", generate_from_scratch_node)
    
    workflow.set_entry_point("retrieve")
    
    # Linear edge: Retrieval ALWAYS flows directly into Evaluation
    workflow.add_edge("retrieve", "evaluate") 
    
    # Conditional Edges
    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "synthesize": "synthesize",
            "generate_fallback": "generate_fallback"
        }
    )
    
    # Terminal Edges
    workflow.add_edge("synthesize", END)
    workflow.add_edge("generate_fallback", END)
    
    return workflow.compile()

# Export the compiled agent singleton
tier1_agent = build_tier1_agent()