from transformers import pipeline
eng_gen = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")


def gen_en_sentence(word, max_attempts=3):
    prompt = f'Write an English sentence that includes the exact phrase "{word}":\n'
    for _ in range(max_attempts):
        out = eng_gen(
            prompt,
            max_new_tokens=20,
            do_sample=True,
            top_p=0.95,
            temperature=0.7,
            repetition_penalty=1.2,
            pad_token_id=eng_gen.tokenizer.eos_token_id
        )
        generated = out[0]["generated_text"][len(prompt):].strip()
        if word.lower() in generated.lower():
            return generated
    return f"(Model did not use the phrase. Try again.)"

if __name__ == "__main__":
    for w in ["father", "house", "helmet", "I miss", "book"]:
        print(f"{w} → {gen_en_sentence(w)}")