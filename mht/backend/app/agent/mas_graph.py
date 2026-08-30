from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agent.mas_state import MASState
from app.agent.mas_nodes import (
    tutor_evaluation_node,
    conversationalist_node
)

# --- 2. Graph Compilation ---
def build_mas_agent():
    """
    Compiles the Tier-Pro Actor-Critic Conversational Agent.
    """
    workflow = StateGraph(MASState)
    
    # Add Nodes
    workflow.add_node("tutor_eval", tutor_evaluation_node)
    workflow.add_node("conversationalist", conversationalist_node)
    
    # Entry Point: Critic analyzes the user's latest utterance first
    workflow.set_entry_point("tutor_eval")
    
    # Edges: Sequential Supervisor -> Actor Hand-off
    workflow.add_edge("tutor_eval", "conversationalist")
    workflow.add_edge("conversationalist", END)
    
    return workflow.compile()

# Export compiled MAS singleton
mas_agent = build_mas_agent()