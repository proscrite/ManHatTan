from bidi.algorithm import get_display


from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re

MODEL = "Norod78/hebrew-gpt_neo-small"

# Load once
tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(MODEL, low_cpu_mem_usage=True)
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1,
    batch_size=1
)

def generate_hebrew_sentence(word: str, max_tokens: int = 30) -> str:
    prompt = f"{word} "

    result = generator(
        prompt,
        max_new_tokens=max_tokens,
        do_sample=True,
        top_p=0.9,
        top_k=50,
        temperature=0.85,
        repetition_penalty=1.2,
        num_beams=3,
        # early_stopping=True,
        no_repeat_ngram_size=2,
        pad_token_id=tokenizer.eos_token_id
    )
    if not result or not isinstance(result, list) or len(result) == 0:
        return f"Error generating sentence for word: {word}"
    else:
        out = result[0]["generated_text"]

    sentence = out[len(prompt):].strip()
    sentence = re.split(r"[\.!\?]", sentence)[0].strip()
    if sentence and sentence[0] != sentence[0].upper():
        sentence = sentence[0].upper() + sentence[1:]
    sentence += "."
    return sentence

if __name__ == "__main__":
    for w in ["אבא", "בית", "משפחה", "שלום", "ספר", "מורה"]:
        print(f"{w}:\n")
        print(get_display(generate_hebrew_sentence(w)) )
