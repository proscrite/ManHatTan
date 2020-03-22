from googletrans import Translator
translator = Translator()
import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('~/Documents/ManHatTan/python_scripts/')

from bulkTranslate import *

def test_long_sentence(src):
    """Search entries with more than 3 words and drop them"""
    for i,w in enumerate(src):
        if ' ' in w:
            sentence = w
            if len(re.findall(' ', sentence)) >= 3:
                print("Entry with more than 3 words detected: ", sentence)
                src.pop(i)
    return src

def test_split_dest(dest_str):
    dest_list = re.split('\n', dest_str)
    dest_clean = split_dest(dest_str)
    assert len(dest_clean) == len(dest_list), "Incorrect split and number cleaning of dest_str"

def test_bulk_translate(src : pd.Series, dest_lang : str):
    dest = bulk_translate(src, dest_lang)
    assert len(src) == len(dest), 'bulk_translate error: len(dest) does not match len(src)'
