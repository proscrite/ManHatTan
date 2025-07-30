from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
from bidi.algorithm import get_display
def main():
    model_name = "Norod78/distilgpt2-base-pretrained-he"
    # 1) load once
    print("Loading model/tokenizer…")
    model     = AutoModelForCausalLM.from_pretrained(model_name, low_cpu_mem_usage=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    gen       = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=-1,           # CPU
        batch_size=1
    )

    word = input("Enter Hebrew word for CLAW: ").strip()

    # 2) properly quote the target word in Hebrew
    prompt = f"כתוב משפט אחד בעברית עם המילה '{word}' בלבד."
    prompt = get_display(prompt) 
    print(f"\n🦞 CLAW prompt: {prompt}")
    # 3) Generate with stricter parameters
    outputs = gen(
        prompt,
        max_length=50,        # total tokens (prompt + response)
        min_length=10,        # at least ~10 tokens
        num_beams=5,          # beam search for coherence
        do_sample=True,      # disable sampling for deterministic output
        early_stopping=True,  # stop as soon as beam search is done
        no_repeat_ngram_size=2,
        pad_token_id=tokenizer.eos_token_id
    )

    text = outputs[0]["generated_text"]

    # 4) strip the prompt prefix if model echoes it
    # if text.startswith(prompt):
    #     text = text[len(prompt):].strip()

    # # 5) truncate to first sentence
    # text = re.split(r"[\.!\?]", text)[0].strip()

    # 6) blank out the word
    # if f"{word}" in text:
    #     text = re.sub(rf"\b{re.escape(word)}\b", "___", text, count=1)
    # else:
    #     # fallback: just prepend blank
    #     text = "___ " + text

    # 7) ensure punctuation
    if not text.endswith((".", "!", "?")):
        text += "."

    print("\n🦞 CLAW exercise:")
    print(text)


if __name__ == "__main__":
    main()
