import re
import asyncio
from googletrans import Translator
import pandas as pd
import logging
logging.getLogger("stanza").setLevel(logging.ERROR)


# Extracts the first sentence from a text that contains a specific word.
def extract_single_sentence(text: str, word: str) -> str:
    """
    Returns the first sentence from the text that contains `word`.
    If no sentence contains the word, returns an empty string.
    """
    # Split on sentence-ending punctuation while preserving the punctuation
    sentences = re.split(r'(?<=[\.!\?\…])\s+', text.strip())
    for sent in sentences:
        if word.lower() in sent.lower():
            return sent.strip()
    return f"(Model did not use the phrase. Try again.)"

def extract_strings(nested):
    """   Extracts all strings from a nested structure (list or string).
    This function recursively traverses the structure and collects all strings.
    """
    strings = []
    if isinstance(nested, str):
        strings.append(nested)
    elif isinstance(nested, list):
        for item in nested:
            strings.extend(extract_strings(item))
    return strings

async def translate_sentence(sentence: str, src_lang: str = 'en', dest_lang: str = 'he') -> str:
    """    Translates a sentence from the source language to the destination language.
    Uses Google Translate API asynchronously"""

    print(f'Starting translation, src = {sentence}, dest_lang = {dest_lang}')
    async with Translator() as translator:
        
        if not dest_lang:
            print('No destination language specified. Using Hebrew as default.')
            dest_lang = 'he'

        translation = await translator.translate(text = sentence, dest=dest_lang, src=src_lang)
        
        return translation

def check_direct_contains(sentence, word: str) -> tuple[bool, str]:
    """
    Checks if the translated sentence contains the specified word.
    Returns True if it does, False otherwise.
    """
    if word.lower() in sentence.lower():
        sentence_blank = sentence.replace(word, '_' * len(word))
        return True, sentence_blank
    else: 
        return False, None
    
def get_lexeme(token, nlp=None):
    """ Extracts the lexeme from a token using a NLP pipeline.
    """
    if not isinstance(token, str):
        raise ValueError("Input must be a string token.")
    if nlp is None:
        import stanza
        nlp = stanza.Pipeline('he', processors='tokenize,pos,lemma,depparse')
    doc = nlp(token)

    for sent in doc.sentences:
        for word in sent.words:
            if word.lemma:
                return word.lemma 
    print ("Lexeme not found for token: {token}")
    return None

def check_lexeme_contains(sentence: str, word: str, lip: pd.DataFrame, nlp = None) -> tuple[bool, str]:
    """
    Checks if the translated sentence contains the lexeme of the specified word.
    Returns True if it does, False otherwise.
    """
    target_lip_lexeme = lip.loc[word].lexeme_string
    for word in sentence.split():
        lexeme_word = get_lexeme(word, nlp)
        if lexeme_word in target_lip_lexeme:
            sentence_blank = sentence.replace(word, '_' * len(word))
            return True, sentence_blank
    return False, None

def check_other_translations(result_translation, word_ll, lip, nlp=None):
    """
    Checks if the translation contains other possible translations for the word.
    Returns a list of possible translations if found, otherwise an empty list.
    """
    if not result_translation.extra_data or 'possible-translations' not in result_translation.extra_data:
        return False, None
    possible_tranlations = result_translation.extra_data['possible-translations'][0]
    possible_translations_flat = extract_strings(possible_tranlations)
    if not possible_translations_flat:
        return False, None
    
    # Iterate through the possible translations and check if any of them contain the lexeme of the word
    for possibility in possible_translations_flat:
        # For each sentence use check_lexeme_contains to iterate through the words
        flag_contains, blank_sentence = check_lexeme_contains(possibility, word_ll, lip, nlp)
        if flag_contains:
            return True, blank_sentence
    return False, None

def claw_english_processing(word_ll: str, word_ul: str, en_sentence: str, lip: pd.DataFrame, nlp=None):
    """
    Processes an English sentence to check if it contains the specified word or its lexeme.
    Returns True and the blanked sentence if found, otherwise False and None.
    """
    print("Original sentence:", en_sentence)
    print("Word to extract:", word_ll)
    
    extracted_sentence = extract_single_sentence(en_sentence, word_ul)
    print("Extracted sentence:", extracted_sentence)
    
    result_translation = asyncio.run(translate_sentence(extracted_sentence, src_lang='en', dest_lang='he') )
    print("Translation:", result_translation) 

    # List of check functions and their arguments
    checks = [
        (check_direct_contains, [result_translation.text, word_ll], f"The translated sentence contains the word '{word_ll}'."),
        (check_lexeme_contains, [result_translation.text, word_ll, lip, nlp], f"The translated sentence contains the lexeme of '{word_ll}'."),
        (check_other_translations, [result_translation, word_ll, lip, nlp], f"The translated sentence contains the lexeme of '{word_ll}' in alternative translations.")
    ]

    for check_func, args, success_msg in checks:
        flag_contains, blank_sentence = check_func(*args)
        if flag_contains:
            print(success_msg)
            return True, blank_sentence, result_translation.text

    print(f"The translated sentence does not contain the word or its lexeme '{word_ll}'.")
    return False, '', ''

def claw_hebrew_processing(word_ll: str, word_ul: str, he_sentence: str, lip: pd.DataFrame, nlp=None) -> tuple[bool, str, str]:
    """
    Processes a Hebrew sentence to check if it contains the specified word or its lexeme.
    Returns True and the blanked sentence if found, otherwise False and None.
    """
    print("Original sentence:", he_sentence)
    print("Word to extract:", word_ll)
    
    result_translation = asyncio.run(translate_sentence(he_sentence, src_lang='he', dest_lang='en') )
    print("Translation:", result_translation) 

    # List of check functions and their arguments
    checks = [
        (check_direct_contains, [he_sentence, word_ll], f"The generated sentence contains the word '{word_ll}'."),
        (check_lexeme_contains, [he_sentence, word_ll, lip, nlp], f"The generated sentence contains the lexeme of '{word_ll}'."),
    ]

    for check_func, args, success_msg in checks:
        flag_contains, blank_sentence = check_func(*args)
        if flag_contains:
            print(success_msg)
            return True, blank_sentence, result_translation.text

    print(f"The generated sentence does not contain the word or its lexeme '{word_ll}'.")
    return False, '', ''
