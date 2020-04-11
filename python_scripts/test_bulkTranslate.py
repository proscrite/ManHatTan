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
    src.reset_index(drop=True, inplace=True)
    return src

def test_split_dest(dest_str):
    dest_list = re.split('\n', dest_str)
    dest_clean = split_dest(dest_str)
    assert len(dest_clean) == len(dest_list), "Incorrect split and number cleaning of dest_str"

def test_bulk_translate(src : pd.Series, dest_lang : str):
    dest = bulk_translate(src, dest_lang)
    assert len(src) == len(dest), 'bulk_translate error: len(dest) does not match len(src)'


def test_output_bulkTranslate(gotscript_path : str):
    """Test whether bulkTranslate produces the same absolute GOTA as in reference file (Siddhartha)
        and indicate what words differ"""

    gotref_path = '/Users/pabloherrero/Documents/ManHatTan/GOTAs/Siddhartha__eine_indische_Dichtung_(German_Edition)_.got'
    gotref = pd.read_csv(gotref_path)
    gotscript = pd.read_csv(gotscript_path)

    compare_df = (gotscript == gotref)
    compare_df.drop('creation_time', axis=1, inplace=True)  # creation_time is not to be compared
    fails = np.where(compare_df == False)
    print('Found (%i,%i) row,cols replication fails at init_gotstick'%(len(fails[0]), len(fails[1]) ))
    print('On reference file:')
    print(gotref.iloc[fails[0], fails[1]])
    print('On processed file:')
    print(gotscript.iloc[fails[0], fails[1]])
