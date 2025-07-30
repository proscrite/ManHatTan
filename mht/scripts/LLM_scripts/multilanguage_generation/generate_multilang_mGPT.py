from transformers import pipeline
from bidi.algorithm import get_display

def gen_multilang_sentence(word: str, lang='en', max_attempts=5, max_new_tokens=30, pipe=None):
    """ Generate a sentence in English or Hebrew containing the specified word.
    Args:
        word (str): The word to include in the generated sentence.
        lang (str): Language code, must be 'en' or 'he'.
        max_attempts (int): Number of attempts to generate a valid sentence.
    Returns:
        str: The generated sentence containing the word, or a fallback message.
    """
    if pipe is None:
        print("Loading mGPT model...")
        pipe = pipeline("text-generation", model="ai-forever/mGPT")

    allowed_langs = ['en', 'he']
    if lang not in allowed_langs:
        raise ValueError(f"lang must be one of {allowed_langs}, got '{lang}'")
    print(f"Generating sentence in {lang} with word: {word}")

    prompt = word
    is_phrase = " " in word.strip()
    if not is_phrase:
        if lang == 'en':
            prompt = f'Write an English sentence that contains the word "{word}":'
        elif lang == 'he':
            prompt = f'כתוב משפט בעברית שמכיל את המילה "{word}":'
    
    print(f"Prompt: {prompt}")

    for _ in range(max_attempts):
        out = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            min_length=5,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95,
            temperature=0.7,
            repetition_penalty=1.2,
            pad_token_id=pipe.tokenizer.eos_token_id
        )
        if is_phrase:
            generated = out[0]["generated_text"].strip()
        else:
            generated = out[0]["generated_text"][len(prompt):].strip()
        if word.lower() in generated.lower() and len(generated) > 5:
            return generated
    return f"(Model did not use the phrase. Try again.)"

if __name__ == "__main__":
    pipe = pipeline("text-generation", model="ai-forever/mGPT")
    # for w in ["father", "house", "helmet", "I miss", "It seems", "book"]:
    #     print(f"{w} → {gen_multilang_sentence(w, lang='en', pipe=pipe)}")

    for w in ["אבא", "מעריץ", "איום", "קסדה", "אני מתגעגע", "ספר"]:
        print(f"{get_display(w)} →")
        # print(get_display(gen_multilang_sentence(w, lang='he')))
        print(gen_multilang_sentence(w, lang='he', pipe=pipe))
