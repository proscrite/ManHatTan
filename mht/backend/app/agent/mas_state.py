# app/agent/mas_state.py
from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class MASState(TypedDict):
    # --- 1. Core Dialogue ---
    # add_messages reducer ensures we append to the chat history, not overwrite it
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # --- 2. User Context & Guardrails ---
    fluency_index: float
    cefr_level: str
    target_lang: str
    native_lang: str
    
    # --- 3. Critic State & Orchestration ---
    due_vocab_id: Optional[str]
    
    # Determines the routing path after the Tutor evaluates the turn
    intervention_type: Optional[Literal["correction", "cloze_exercise", "none"]]
    
    # Stores the Tutor's morphological breakdown/correction instructions
    tutor_critique_ll: Optional[str]
    tutor_critique_ul: Optional[str]
    
    # Actor Dual-Language Outputs
    conversationalist_message_ll: Optional[str]
    conversationalist_message_ul: Optional[str]
    
    # Stores the payload returned if the Tier-1 Subgraph is triggered
    # generated_exercise: Optional[dict]