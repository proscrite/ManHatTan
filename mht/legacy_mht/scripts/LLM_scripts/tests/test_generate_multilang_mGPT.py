from ..multilanguage_generation.generate_multilang_mGPT import gen_multilang_sentence
from bidi.algorithm import get_display

def test_gen_multilang_sentence():
    words_en = ["father", "house", "helmet", "I miss", "book"]
    words_he = ["אבא", "בית", "קסדה", "אני מתגעגע", "ספר"]
    
    # Test English sentences
    for word in words_en:
        sentence = gen_multilang_sentence(word, lang='en')
        assert word.lower() in sentence.lower(), f"Generated English sentence does not contain the word '{word}': {sentence}"
    
    # Test Hebrew sentences
    for word in words_he:
        sentence = gen_multilang_sentence(word, lang='he')
        assert word in sentence, f"Generated Hebrew sentence does not contain the word '{word}': {sentence}"
        # Check if the sentence is displayed correctly in Hebrew
        assert sentence == get_display(sentence), f"Generated Hebrew sentence is not displayed correctly: {sentence}"

if __name__ == "__main__":
    test_gen_multilang_sentence()
    print("All tests passed for multilingual sentence generation.")