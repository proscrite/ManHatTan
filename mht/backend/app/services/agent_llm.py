from langchain_community.chat_models import ChatLiteLLM
from app.services.llm_service import llm_service

# Bridges the existing Router directly into LangChain's BaseChatModel interface
agent_llm = ChatLiteLLM(
    router=llm_service.router,
    model_name="gemini"
)