import os
import json
import litellm
from litellm import Router
import mlflow
from googletrans import LANGUAGES

from app.schemas import LLMGenerationRequest, LLMGenerationResponse, LLMTaskType

class NoopCache(litellm.InMemoryCache):
    def get_cache(self, key, **kwargs): return None
    def set_cache(self, key, value, **kwargs): pass

litellm.in_memory_llm_clients_cache = NoopCache()

class LLMService:
    def __init__(self):
        model_list = [
            {
                "model_name": "gemini",
                "litellm_params": {
                    "model": "gemini/gemini-3.1-flash-lite",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "timeout": 20,
                },
            },
            {
                "model_name": "groq",
                "litellm_params": {
                    "model": "groq/llama-3.3-70b-versatile",
                    "api_key": os.getenv("GROQ_API_KEY"),
                    "timeout": 15,
                }
            },
            {
                "model_name": "openrouter",
                "litellm_params": {
                    "model": "openrouter/openrouter/free",
                    "api_key": os.getenv("OPENROUTER_API_KEY"),
                    "timeout": 20,
                }
            },
        ]
        
        fallback_routing = [
            {"gemini": ["groq", "openrouter"]}
        ]
        self.router = Router(model_list=model_list, routing_strategy="least-busy", fallbacks=fallback_routing)

    def _build_system_prompt(self, task_type: LLMTaskType) -> str:
        prompts = {
            LLMTaskType.CLOZE: 
            (
                "You are an expert language teacher. Generate a fill-in-the-blank exercise for the provided Target Word. "
                "CRITICAL LINGUISTIC RULES: "
                "1. The 'sentence_target' and all 'options' MUST be written entirely in the Target Language. "
                "2. The 'sentence_translated' MUST be written entirely in the Native Language. "
                "You MUST generate 3 plausible distractors that match the grammatical gender, number, and part-of-speech. "
                "Return raw JSON with keys: 'sentence_target' (with a blank), 'sentence_translated', 'blank_word' (the correct answer), "
                "and 'options' (an array containing the correct answer and the 3 distractors, randomized)."
            ),
            LLMTaskType.GRAMMAR_PILL: (
                "Provide a concise, 2-sentence grammar explanation for the given word or pattern. "
                "Return raw JSON with keys: 'rule_title', 'explanation', 'example'."
            ),
            LLMTaskType.ETYMOLOGY: (
                "Provide the root, historical origin, and root connections for the target word. "
                "Return raw JSON with keys: 'root', 'meaning', 'cognates'."
            ),
            LLMTaskType.WORD_ASSOCIATION: (
                "Find semantic connections between the word and related concepts. "
                "Return raw JSON with keys: 'synonyms', 'antonyms', 'collocations'."
            ),
            LLMTaskType.VOCAB_FACT: (
                "Share an interesting memory hook or mnemonic usage fact for this word. "
                "Return raw JSON with keys: 'mnemonic', 'fun_fact'."
            )
        }
        return prompts.get(task_type, "Return JSON content for the word.")

    @mlflow.trace
    async def generate_content(self, req: LLMGenerationRequest) -> LLMGenerationResponse:
        system_prompt = self._build_system_prompt(req.task_type)

        target_full = LANGUAGES.get(req.target_lang.lower(), req.target_lang).capitalize()
        native_full = LANGUAGES.get(req.native_lang.lower(), req.native_lang).capitalize()
        user_prompt = (
            f"Target Word: {req.target_word}\n"
            f"Target Language: {target_full}\n"
            f"Native Language: {native_full}"
        )

        response = await self.router.acompletion(
            model="gemini/gemini-3.1-flash-lite",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            metadata={"user_id": req.user_id, "task_type": req.task_type.value}
        )

        content_raw = response.choices[0].message.content
        parsed_json = json.loads(content_raw)

        return LLMGenerationResponse(
            task_type=req.task_type,
            content=parsed_json,
            model_used=response.model
        )

llm_service = LLMService()


async def test_cloze():
    req = LLMGenerationRequest(
        target_word="תפוח", # Example Hebrew word
        target_lang="Hebrew",
        native_lang="English",
        task_type=LLMTaskType.CLOZE,
        user_id="test_user_001"
    )
    response = await llm_service.generate_content(req)
    print(f"Model Used: {response.model_used}")
    print(response.content)

if __name__ == "__main__":
    from dotenv import load_dotenv
    import asyncio
    load_dotenv()  # Load environment variables from .env file
    
    asyncio.run(test_cloze())