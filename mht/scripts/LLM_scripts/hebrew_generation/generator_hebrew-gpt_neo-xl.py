import os, re, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from bidi.algorithm import get_display
# ————————————————————————————————
# 0. Tame parallelism & set quant engine
# ————————————————————————————————
os.environ["TOKENIZERS_PARALLELISM"] = "false"
torch.set_num_threads(1)
torch.backends.quantized.engine = "qnnpack"   # ensure we have a quant backend

# ————————————————————————————————
# 1. LOAD & DYNAMIC‑QUANTIZE
# ————————————————————————————————
MODEL = "Norod78/hebrew-gpt_neo-xl"

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)

# Full‑precision model
model_fp = AutoModelForCausalLM.from_pretrained(MODEL).to("cpu").eval()

# Dynamic quantization (Linear layers → int8)
quantized_model = torch.quantization.quantize_dynamic(
    model_fp,
    {torch.nn.Linear},
    dtype=torch.qint8
)
quantized_model.to("cpu").eval()

# ————————————————————————————————
# 2. SIMPLE TEMPLATE FALLBACK
# ————————————————————————————————
def get_simple_template(word: str) -> str:
    return f"{word} נמצא במשפט פשוט."

# ————————————————————————————————
# 3. GENERATION FUNCTION
# ————————————————————————————————
def generate_hebrew_sentence(word: str, max_new_tokens: int = 25) -> str:
    """
    Dynamically quantized, pure-sampling generation that
    ensures `word` appears or falls back.
    """
    # Anchor prompt so continuation must include the word
    prompt = f"כתוב משפט פשוט בעברית המכיל את המילה '{word}':\n{word} "
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")

    # 3a) Generate
    try:
        output_ids = quantized_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,          # sampling for variation
            num_beams=1,             # pure sampling path
            top_k=50,
            top_p=0.9,
            temperature=0.85,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id,
        )
    except Exception as e:
        print("⚠️ Generation error:", e)
        return get_simple_template(word)

    # 3b) Decode and structure as pipeline output
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    result = [{"generated_text": generated_text}]

    # 3c) Fallback condition
    if not result or not isinstance(result, list) or len(result) == 0:
        return get_simple_template(word)
    out = result[0]["generated_text"]

    # Strip prompt echo
    text = out.split(f"{word} ", 1)[-1].strip()

    # Truncate at first sentence-ending punctuation
    sentence = re.split(r"[\.!\?]", text)[0].strip()

    # Ensure the word is present
    if word not in sentence:
        return get_simple_template(word)

    # Capitalize & punctuate
    sentence = sentence[0].upper() + sentence[1:]
    if not sentence.endswith("."):
        sentence += "."

    return sentence

# ————————————————————————————————
# 4. TEST RUN
# ————————————————————————————————
if __name__ == "__main__":
    for w in ["אבא", "בית", "קסדה", "להתגעגע", "ספר", ]:
        print(f"{w} → \n")
        print(get_display(generate_hebrew_sentence(w)))
