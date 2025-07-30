from ..english_generation.generate_english_gpt2_medium import gen_en_sentence

def test_gen_en_sentence():
    words = ["father", "house", "helmet", "I miss", "book"]
    for word in words:
        sentence = gen_en_sentence(word)
        assert word.lower() in sentence.lower(), f"Generated sentence does not contain the word '{word}': {sentence}"

if __name__ == "__main__":
    test_gen_en_sentence()
    print("All tests passed for English sentence generation.")