from googletrans import Translator
translator = Translator()
import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('~/Documents/ManHatTan/python_scripts/')
from test_bulkTranslate import *

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

def load_blue_words(cadera_path : str, src_lang : str) -> pd.Series:
    """Load blue column pd.Series from CADERA and name it src_lang language"""
    df = pd.read_csv(cadera_path, index_col=0)
    src = df.blue.dropna()
    src.name = src_lang

    return src

def format_src(src : pd.Series) -> (str, pd.Series):
    """Remove non-alphanumeric characters from source array
    Returns
    src : pd.Series
        Formatted source series
    """
    src_str = re.sub(pattern = '[\W_](?<![\n\s])', repl='', string=src.to_string()) # Remove tabs
    src_str = re.sub(r'[,.;:"]', '', src_str)  #Remove ortographic symbols

    ### Remove also index number from Series
    src_list = re.split(pattern = '\n\d+\s+', string = src_str)
    src_list[0] = re.sub(pattern='\d\s+', repl= '', string= src_list[0])
    src = pd.Series(src_list, name = src.name)

    return src

def split_dest(dest_str : str) -> list:
    """Split translated chunk by line and clean numbers and blank spaces"""
    dest_list = re.split('\n', dest_str)
    nonum = [re.sub(r'[0-9,.;:"]', '', t) for t in dest_list]  # Remove numbers and punctuation symbols
    dest_clean = [e.strip() for e in nonum]  # Strip from whitespaces at beginning & end of string
    return dest_clean

def bulk_translate(src : pd.Series, dest_lang : str) -> pd.Series:
    """Send single src_str for bulk translation request to server,
    split retrieved dest_str into its entries using RegEx.
    Returns dest : final formatted Series in dest_lang language"""

    dest_str = translator.translate(src.to_string(), src=src.name, dest=dest_lang).text

    dest_clean = split_dest(dest_str)

    dest = pd.Series(dest_clean, name = dest_lang)

    print('Attempted translation of %i entries. Check DB for mistranslations.' %len(dest))
    return dest


def make_dicdf(src : pd.Series, dest : pd.Series, cadera_path : str) -> pd.DataFrame:
    """Assemble src and dest pd.Series into dictionary df
    and append first creation datetime (read_time)"""

    dicdf = pd.DataFrame([src, dest]).T
    dicdf.name = os.path.splitext(os.path.basename(cadera_path))[0]

    #today = datetime.datetime.today()
    today = int(datetime.datetime.timestamp(datetime.datetime.today())) # Correct in init_lipstick.py

    dicdf['creation_time'] = today
    return dicdf

def write_gota(cadera_path : str, dicdf : pd.DataFrame):
    """Take basename from cadera and write dictDf to GOTA file"""
    pathname = os.path.splitext(os.path.abspath(cadera_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'GOTAs', filename+'.got')
    dicdf.to_csv(fpath)

    print('Created GOTA file %s' %fpath)
    return fpath

def check_language(lang : str, meta_lang : str):
    """Check whether given dest and src languages are valid"""

    from googletrans import LANGUAGES
    langKeys = list(LANGUAGES.keys())

    if lang not in langKeys:
        print('Invalid %s language. Choose from one of the following keys' %meta_lang)
        print(langKeys)
        exit

def bulkTranslate_main(cadera_path : str, dest_lang : str, src_lang : str):
    check_language(dest_lang, 'dest')
    check_language(src_lang, 'src')

    src = load_blue_words(cadera_path, src_lang)
    src = format_src(src)    # Remove non-alphanumeric characters
    src = test_long_sentence(src)   # Seek & destroy entries longer than 3 words

    dest = bulk_translate(src, dest_lang)

    assert len(src) == len(dest), 'bulk_translate error: len(dest) does not match len(src)'
    dicDf = make_dicdf(src, dest, cadera_path)

    gota_path = write_gota(cadera_path, dicDf)
    return gota_path

######### Main #########
if __name__ == "__main__":
    cadera_path = sys.argv[1]
    dest_lang = sys.argv[2]
    src_lang = sys.argv[3]

    bulkTranslate_main(cadera_path, dest_lang, src_lan)
    #transl.detect_fails()
