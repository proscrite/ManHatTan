from googletrans import Translator
translator = Translator()
import asyncio
import pandas as pd
import random
import numpy as np
import os
import re
from bidi.algorithm import get_display

### Helper functions for bulk translation and language detection ###

def check_language(lang : str, meta_lang : str):
    """Check whether given dest and src languages are valid"""

    from googletrans import LANGUAGES
    langKeys = list(LANGUAGES.keys())

    if lang not in langKeys:
        print('Invalid %s language. Choose from one of the following keys' %meta_lang)
        print(langKeys)
        exit

def format_src(src_list : list) -> list:
    """Remove non-alphanumeric characters from source array
        Parameters
        src_list : list
            Source series to be formatted
        Returns
        src_formatted : list
            Formatted source series
    """
    
    src_formatted = [re.sub(pattern = '[\W_](?<![\n\s])', repl='', string=w) for w in src_list]   # Remove tabs
    src_formatted = [re.sub(r'[,.;:"]', '', w) for w in src_formatted]    #Remove ortographic symbols

    return src_formatted


def split_dest(dest_str : str) -> list:
    """Split translated chunk by line and clean numbers and blank spaces"""
    dest_list = re.split('\n', dest_str)
    nonum = [re.sub(r'[0-9,.;:"]', '', t) for t in dest_list]  # Remove numbers and punctuation symbols
    dest_clean = [e.strip() for e in nonum]  # Strip from whitespaces at beginning & end of string
    return dest_clean


######### Automatic language detection and bulk translation functions #########
    
async def detect_language(text):
    async with Translator() as translator:
        try:
            # Detect the language of the text
            detected = await translator.detect(text)
            return detected.lang
        except Exception as e:
            print(f"Error during language detection: {e}")
            return None

async def detect_language_list(texts: list):
    async with Translator() as translator:
        try:
            # Detect the languages of a list of texts
            detected = await translator.detect(texts)
            return detected
        except Exception as e:
            print(f"Error during language detection: {e}")
            return None

async def find_language(word_list: list, min_confidence=4.0):
    """Detect language of the blue column in CADERA.
    Parameters:
    word_list : list
        List of words to sample for language detection. Should be at least 10 words long.
    min_confidence : float
        Minimum confidence threshold for language detection. Default is 4.0.
    Returns:
    str or None
        Detected language code if confidence is above the threshold, otherwise None.
    Usage:
    >>> detected_lang = await find_language(['Hello', 'world', 'ich', 'liebe', 'dich'], min_confidence=4.0)
    """

    if not word_list or len(word_list) < 10:
        print("The word list too short. Cannot detect language confidently.")
        return None
    # Sample 10 words from the word_list

    sample_list = random.sample(word_list, 10)

    result = await detect_language_list(sample_list)
    
    detected_languages = [res.lang for res in result]
    detected_confidence = [res.confidence for res in result]
    
    detection_stats = pd.DataFrame({
        'detected_language': detected_languages,
        'confidence': detected_confidence
    })
    
    grouped_confidences = detection_stats.groupby('detected_language').sum().sort_values(by='confidence', ascending=False)
    
    max_confidence = grouped_confidences[grouped_confidences['confidence'] == grouped_confidences['confidence'].max()]
    predicted_lang, summed_conf = max_confidence.index[0], max_confidence['confidence'].values[0]
    
    if summed_conf < min_confidence:
        print(f"Predicted language '{predicted_lang}' with confidence {summed_conf/10} is below the minimum threshold of {min_confidence/10}.")
        return None
    else:
        print(f"Predicted language: {predicted_lang} with confidence: {summed_conf/10}")
        return predicted_lang
    
##### Bulk translation functions #####

async def bulk_translate(src_list: list, src_lang: str, dest_lang: str = None):
    """Translate a list of strings from src_lang to dest_lang using googletrans.
    Parameters:
    src_list : list
        List of strings to be translated.
    src_lang : str
        Source language code (e.g., 'en', 'de', 'es').
    dest_lang : str, optional
        Destination language code (e.g., 'en', 'de', 'es'). If not specified, defaults to 'en'.
    Returns:
    dest_list : list
        List of translated strings in the destination language.
    Usage:
    >>> translated_df = await bulk_translate(['Hello', 'World'], 'en', 'es')
    """

    if not src_list:
        return {}
    
    if not dest_lang:
        print('No destination language specified. Using English as default.')
        dest_lang = 'en'

    print(f'Starting translation, src = {src_list[:5]}..., dest_lang = {dest_lang}')
    async with Translator() as translator:
        try:
            dest_list = await translator.translate(text = src_list, dest=dest_lang, src=src_lang)
            
            if not isinstance(dest_list, list):
                dest_list = [dest_list]
            print('Translation finished')
            return dict(zip(src_list, [t.text for t in dest_list]))
    
        except Exception as e:
            print(f"Error during batch translation: {e}")
            return {src: "" for src in src_list}