from transformers import pipeline
import re

def gen_en_sentence(word: str, max_attempts=5, max_new_tokens=30, pipe=None):
    """ Generate an English sentence containing the specified word.
    Args:
        word (str): The word to include in the generated sentence.
        max_attempts (int): Number of attempts to generate a valid sentence.
        max_new_tokens (int): Maximum number of new tokens to generate.
        pipe (transformers.pipeline, optional): Pre-initialized text generation pipeline. If None, it will be created.
    Returns:
        str: The generated sentence containing the word, or a fallback message.
    """
    if pipe is None:
        print("Loading GPT-2 model...")
        eng_gen = pipeline("text-generation", model="gpt2-medium")
    is_phrase = " " in word.strip()
    if is_phrase:
        prompt = word
    else:
        prompt = f'Write an English sentence that includes the exact phrase "{word}":\n'
    for _ in range(max_attempts):
        out = eng_gen(
            prompt,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.7,
            min_length=5,
            repetition_penalty=1.3,
            pad_token_id=eng_gen.tokenizer.eos_token_id
        )
        if is_phrase:
            generated = out[0]["generated_text"].strip()
        else:
            generated = out[0]["generated_text"][len(prompt):].strip()
        if word.lower() in generated.lower():
            return generated
    return f"(Model did not use the phrase. Try again.)"

if __name__ == "__main__":
    eng_gen = pipeline("text-generation", model="gpt2-medium")
    for w in ["solution", "house", "helmet", "I miss", "It seems", "recommendation"]:
        print(f"{w} → {gen_en_sentence(w, max_attempts=5, max_new_tokens=30, pipe=eng_gen)}")
