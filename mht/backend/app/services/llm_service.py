import os
import json
import litellm
from litellm import Router
import mlflow
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
                    "model": "gemini/gemini-flash-latest",
                    "api_key": os.getenv("GEMINI_API_KEY"),
                    "timeout": 20,
                }
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
            }
        ]
        self.router = Router(model_list=model_list, routing_strategy="least-busy")

    def _build_system_prompt(self, task_type: LLMTaskType) -> str:
        prompts = {
            LLMTaskType.CLOZE: (
                "You are an expert language teacher. Generate a fill-in-the-blank exercise. "
                "Return raw JSON with keys: 'sentence_target', 'sentence_translated', 'blank_word', 'options'."
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
        user_prompt = f"Target Word: {req.target_word}\nLanguage: {req.target_lang} -> {req.native_lang}"

        response = await self.router.acompletion(
            model="gemini",
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