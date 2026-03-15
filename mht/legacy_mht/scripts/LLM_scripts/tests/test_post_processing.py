from ..post_processing import *

def test_check_direct_contains():
    """
    Test the check_direct_contains function with various inputs.
    """
    # Example sentence that contains the word
    class Sentence:
        def __init__(self, text):
            self.text = text
    sentence = Sentence("אני אוהב את התפוזים של הקיץ")
    word = "תפוזים"
    assert check_direct_contains(sentence, word) == (True, "אני אוהב את ה______ של הקיץ")


    # Example sentence that does not contain the word
    sentence = Sentence("אני אוהב את התפוחים")
    word = "תפוזים"
    assert check_direct_contains(sentence, word) == (False, None)

    # Example sentence where the word is present at the end of the sentence (weird ___ positioning)
    sentence = Sentence("אני אוהב את התפוזים")
    word = "תפוזים"
    print(check_direct_contains(sentence, word))
    assert check_direct_contains(sentence, word) == (True, "אני אוהב את ה______")


def test_get_lexeme():
    """Test the get_lexeme function with various inputs.
    """
    target_word = 'מפלגה'
    generated_word = 'מפלגות'
    target_lexeme = 'מפלגה/מפלגה<NOUN>Fem|Sing|'
    lexeme_generated_word = get_lexeme(generated_word)
    print(f"Lexeme for {generated_word}: {lexeme_generated_word}")
    assert lexeme_generated_word in target_lexeme, f"Expected lexeme '{lexeme_generated_word}' to be in '{target_lexeme}'"
    
    target_word2 = 'מפלגה'
    generated_word2 = 'מסיבות'
    lexeme_generated_word2 = get_lexeme(generated_word2)
    target_lexeme2 = 'מפלגה/מפלגה<NOUN>Fem|Sing|'
    print(f"Lexeme for {generated_word2}: {lexeme_generated_word2}")
    assert lexeme_generated_word2 in target_lexeme2, f"Expected lexeme '{lexeme_generated_word2}' to be in '{target_lexeme2}'"

    target_word3 = 'מעריץ'
    generated_word3 = 'מעריצים'
    target_lexeme3 = 'מעריץ/העריץ<VERB>Masc|HIFIL|Sing|1,2,3|Part|Act|'
    lexeme_generated_word3 = get_lexeme(generated_word3)
    print(f"Lexeme for {generated_word3}: {lexeme_generated_word3}")
    assert lexeme_generated_word3 in target_lexeme3, f"Expected lexeme '{lexeme_generated_word3}' to be in '{target_lexeme3}'"

    generated_word4 = 'יעריצו'
    lexeme_generated_word4 = get_lexeme(generated_word4)
    target_lexeme4 = target_lexeme3  # Reusing the same target lexeme for consistency
    print(f"Lexeme for {generated_word4}: {lexeme_generated_word4}")
    assert lexeme_generated_word4 in target_lexeme4, f"Expected lexeme '{lexeme_generated_word4}' to be in '{target_lexeme4}'"

def test_check_lexeme_contains():
    """Test the check_lexeme_contains function with various inputs.
    """
    lip = pd.DataFrame({
        'lexeme_string': {
            'מפלגה': 'מפלגה/מפלגה<NOUN>Fem|Sing|',
            'מעריץ': 'מעריץ/העריץ<VERB>Masc|HIFIL|Sing|1,2,3|Part|Act|'
        }
    })

    # Test with a sentence that contains the lexeme of the word
    sentence = "המעריצים של המפלגה התאספו."
    word = "מפלגה"
    assert check_lexeme_contains(sentence, word, lip)[0] == True

    # Test with a sentence that does not contain the lexeme of the word
    sentence = "המעריצים של הקבוצה התאספו."
    word = "מפלגה"
    assert check_lexeme_contains(sentence, word, lip)[0] == False

    # Test with a sentence that contains the lexeme of the word in a different form
    sentence = 'אנשים מעריצים את הזמר'
    word = 'מעריץ'
    assert check_lexeme_contains(sentence, word, lip)[0] == True

    # Test with an empty string
    sentence = ""
    word = "מפלגה"
    assert check_lexeme_contains(sentence, word, lip)[0] == False

def test_extract_strings():
    """Test the extract_strings function with various inputs.
    """
    # Test with a simple string
    nested = "Hello, world!"
    assert extract_strings(nested) == ["Hello, world!"]

    # Test with a list of strings
    nested = ["Hello", "world"]
    assert extract_strings(nested) == ["Hello", "world"]

    # Test with a mixed structure
    nested = ["Hello", ["world", "Python"]]
    assert extract_strings(nested) == ["Hello", "world", "Python"]

    # Test with an empty input
    nested = []
    assert extract_strings(nested) == []

    # Test with a nested structure containing strings and lists (real use example)
    nested = [
        'You bought several helmets',
        None,
        [['קנית כמה קסדות', None, True, False, [3], None, [[3]]],
        ['קניתם כמה קסדות', None, True, False, [8]]],
        [[0, 26]],
        'You bought several helmets',
        0,
        0
    ]

    assert extract_strings(nested) == [
        'You bought several helmets',
        'קנית כמה קסדות',
        'קניתם כמה קסדות',
        'You bought several helmets'
    ]

def test_check_other_translations():
    """
    Test the check_other_translations function with various inputs.
    """
    # Example translation with possible translations
    he_translation = {
        'extra_data': {
            'possible-translations': [
                ['אני קניתי כמה קסדות', 'אתה קנית כמה קסדות']
            ]
        }
    }
    
    word_ll = 'קסדה'
    lip = pd.DataFrame({
        'word_ll': ['קסדה'],
        'lexeme_string': ['קסדה/קסדה<NOUN>Number=Sing|Gender=Fem']
    }).set_index('word_ll')
    
    assert check_other_translations(he_translation, word_ll, lip)[0] == True

    # Example translation with possible translations that do not match the lexeme
    he_translation = {
        'extra_data': {
            'possible-translations': [
                ['אני קניתי כמה מכנסיים', 'אתה קנית כמה מכנסיים']
            ]
        }
    }
    word_ll = 'קסדה'
    lip = pd.DataFrame({
        'word_ll': ['קסדה'],
        'lexeme_string': ['קסדה/קסדה<NOUN>Number=Sing|Gender=Fem']
    }).set_index('word_ll')

    assert check_other_translations(he_translation, word_ll, lip)[0] == False


def test_claw_english_processing():
    """Test the claw_english_processing function with various inputs.
    """
    lip = pd.DataFrame({
        'word_ll': ['קסדה'],
        'lexeme_string': ['קסדה/קסדה<NOUN>Number=Sing|Gender=Fem']
    }).set_index('word_ll')

    # Test with a sentence that contains the word
    en_sentence="I bought a new helmet for my bike ride. It is very comfortable and safe."
    word_ll="קסדה"
    word_ul="helmet"
    result = claw_english_processing(word_ll, word_ul, en_sentence=en_sentence, lip=lip)
    assert result[0]

    # Test with a sentence that contain a word with the same root
    en_sentence="I bought many helmets for my bike ride."
    word_ll="קסדה"
    word_ul="helmets"
    result = claw_english_processing(word_ll, word_ul, en_sentence=en_sentence, lip=lip)
    assert result[0]

    # Test with a sentence that does not contain the word
    en_sentence="I bought a new bike for my ride. It is very comfortable and safe."
    word_ll="קסדה"
    word_ul="helmet"
    result = claw_english_processing(word_ll, word_ul, en_sentence=en_sentence, lip=lip)
    assert result == False
    
    # Test with an empty string
    text = ""
    word_ll = "קסדה"
    word_ul = "helmet"
    result = claw_english_processing(word_ll, word_ul, en_sentence=text, lip=lip)
    assert result == False

# Run the tests
test_check_direct_contains()
test_get_lexeme()
test_check_lexeme_contains()
test_extract_strings()
test_check_other_translations()
test_claw_english_processing()
print("All tests passed successfully!")