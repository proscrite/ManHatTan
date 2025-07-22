from googletrans import Translator
translator = Translator()
import asyncio
import pandas as pd
import random
import numpy as np
import os
import sys
import re
import datetime
from bidi.algorithm import get_display
import logging


# from mht.scripts.python_scripts.test_bulkTranslate import *

def detect_src(self, N : int = 0):
    """Auto-detect languages in wordset given and arrange them by occurrences
    Parameters:
    N : int = 0
        Number of words to sample from CADERA series. If left to 0, the whole Series is taken"""

    def compute_highest_scoring_language(dictNorm : dict, dictWeights : dict) -> dict:
        """Return highest scoring weighted language over the sample.
        The probability for each language results from summing over all occurrences the product of two factors:
            - Occurrences_language / sum(occurrences_languages)
            - confidence_occurrence """
        ret = dict()
        normFactor = sum(dictNorm.values())
        for key, language in dictWeights.items():
            ret[key] = language*dictNorm.get(key, 1) / normFactor
        return ret

    if N != 0:
        sample = self.dfSrc.sample(N)
    else:
        sample = self.dfSrc

    lang = [translator.detect(w).lang for w in sample]
    conf = [translator.detect(w).confidence for w in sample]
    dfLang = pd.DataFrame({'lang':lang, 'conf':conf})

    dictNorm = dfLang.lang.value_counts().to_dict()  # Dictionary with number of occurences per language
    normFactor = sum(dictNorm.values())              # Total number of words in sample

    a = dfLang.groupby('lang').sum().to_dict()['conf']
    dictWeights = {k: v / normFactor for k, v in a.items()}   # Weights per language, averaged by occurrences

    ret = compute_highest_scoring_language(dictNorm, dictWeights)
    maximum = max(ret, key=ret.get)
    return maximum, ret#[maximum]

def check_language(lang : str, meta_lang : str):
    """Check whether given dest and src languages are valid"""

    from googletrans import LANGUAGES
    langKeys = list(LANGUAGES.keys())

    if lang not in langKeys:
        print('Invalid %s language. Choose from one of the following keys' %meta_lang)
        print(langKeys)
        exit

def load_words_selected_color(cadera_path : str, src_lang : str, word_color: str = 'blue') -> list:
    """Load column with selected from CADERA as list"""
    df = pd.read_csv(cadera_path, index_col=0)
    src_list = df[word_color].dropna().to_list()  # Load blue column as list

    return src_list

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

def get_gota_path(cadera_path : str) -> str:
    """Take basename from cadera and make GOTA path"""
    pathname = os.path.splitext(os.path.abspath(cadera_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    gota_path = os.path.join(dirPath, 'GOTAs', filename+'.got')
    if not os.path.exists(os.path.dirname(gota_path)):
        os.makedirs(os.path.dirname(gota_path))
    return gota_path

def write_gota(gota_df : pd.DataFrame, gota_path : str) -> str:
    """Write GOTA DataFrame to file"""

    gota_df.to_csv(gota_path, index=False)
    print('Created GOTA file %s' %gota_path)
    return gota_path
    
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

    print(f'Starting translation, src = {src_list}, dest_lang = {dest_lang}')
    async with Translator() as translator:
        
        if not dest_lang:
            print('No destination language specified. Using English as default.')
            dest_lang = 'en'

        dest_list = await translator.translate(text = src_list, dest=dest_lang, src=src_lang)
        print('Translation finished')
        
        return dest_list

def check_new_elements(src_list: list, src_lang: str, gota_df: pd.DataFrame) -> list:
    """Check for new elements in the source string that are not in the GOTA DataFrame."""
    
    mask = pd.Series(src_list).isin(gota_df[src_lang])
    new_words = [w for w in src_list if w not in set(gota_df[src_lang])]

    if not new_words:
        print('No new elements to translate.')
        return None
    else:
        print(f'New elements to translate: {len(new_words)}')
        return new_words


def make_gota_df(src_list : list, dest_list : list, src_lang: str, dest_lang: str, cadera_path : str) -> pd.DataFrame:
    """Assemble src and dest lists into gota_df (GOgle Translation Archive)
    and append first creation datetime (read_time)"""
    dest_text_list = [d.text for d in dest_list]

    assert len(src_list) == len(dest_text_list), 'bulk_translate error: len(dest) does not match len(src)'

    dest_dict = {}
    for s, d in zip(src_list, dest_list):
        dest_dict[s] = d.text
    gota_df = pd.DataFrame(dest_dict.items(), columns=[src_lang, dest_lang])
    
    gota_df.name = os.path.splitext(os.path.basename(cadera_path))[0]
    #today = datetime.datetime.today()
    today = int(datetime.datetime.timestamp(datetime.datetime.today())) # Correct in init_lipstick.py

    gota_df['creation_time'] = today
    return gota_df

async def bulkTranslate_main(cadera_path : str, word_color: str, dest_lang : str, src_lang : str):
    """Main function to handle bulk translation from CADERA file
        Parameters:
        cadera_path : str
            Path to the CADERA file.
        word_color : str
            Color of the words to be translated (e.g., 'blue').
        dest_lang : str
            Destination language code (e.g., 'en', 'de', 'es').
        src_lang : str
            Source language code (e.g., 'en', 'de', 'es').
        Returns:
        gota_path : str
            Path to the GOTA file created after translation."""
    
    check_language(dest_lang, 'dest')
    check_language(src_lang, 'src')
    print('Correct language format')

    src_unformat = load_words_selected_color(cadera_path, src_lang, word_color)
    src_list = format_src(src_unformat)    # Remove non-alphanumeric characters

    gota_path = get_gota_path(cadera_path)
    if os.path.exists(gota_path):
        print('GOTA file already exists, overwriting...')
        current_gota_df = pd.read_csv(gota_path)
        src_list = check_new_elements(src_list, src_lang, current_gota_df)  # Keep only new elements
        if src_list is None:
            print('No new elements to translate. Finished translating...')
            return gota_path
    else:
        current_gota_df = None
        print('Creating new GOTA file...')
        
    dest_list = await bulk_translate(src_list, src_lang, dest_lang)

    gota_df = make_gota_df(src_list, dest_list, src_lang=src_lang, dest_lang=dest_lang, cadera_path= cadera_path)
    
    if current_gota_df is not None:   # If GOTA file already exists, append new data
        print('Appending new data to existing GOTA file...')
        gota_df = pd.concat([current_gota_df, gota_df], ignore_index=True)
    gota_path = write_gota(gota_df, gota_path)
    print('GOTA file written to %s' %gota_path)
    return gota_path

######### Main #########
if __name__ == "__main__":
    cadera_path = sys.argv[1]
    word_color = sys.argv[2]
    dest_lang = sys.argv[3]
    src_lang = sys.argv[4]

    bulkTranslate_main(cadera_path, word_color, dest_lang, src_lang)
    #transl.detect_fails()
