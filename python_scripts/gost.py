import pandas as pd
import numpy as np
import sys

sys.path.append('../python_scripts/')
from init_lipstick import *

def make_lang_dic(languages: list):
    """Return a dict with inverted langcodes
    Ex: {'en': 'English'
        'eu': 'Basque'}
    Takes a list with long languages names ('English', 'Basque')
    """
    from googletrans import LANGCODES as dictTrans

    langs = {}
    for la in languages:
        try:
            lang = dictTrans[la.lower()]
        except KeyError:
            pass
        langs[lang] = la
    return langs

def gost2gota(gost: pd.DataFrame, langs: dict, ll: str, ul: str):
    """
        Adapt GOST to GOTA format for LIPSTICK processing
        Parameters:
            ll: learning language in short format
            ul: user language in short format ('en', 'de', 'es'...)
    """
    # Seach for coincidences with the learning language (ll)
    targetEntries = gost[gost['source_lang'] == langs[ll]]

    newGota = pd.DataFrame({ll:[], ul: []})
    newGota[ll] = targetEntries['source_word']
    newGota[ul] = targetEntries['translation']
    newGota.reset_index(drop=True, inplace=True)

    # Search as well for reverse translation: coincidences in the translation
    invGota = pd.DataFrame({ll:[], ul: []})
    targetEntries = gost[gost['target_lang'] == langs[ll]]
    invGota[ul] = newGota[ul].append(targetEntries['source_word'], ignore_index=True)
    invGota[ll] = newGota[ll].append(targetEntries['translation'], ignore_index=True)

    # Add creation timestamp
    today = int(datetime.datetime.timestamp(datetime.datetime.today()))
    invGota['creation_time'] = today
    return invGota


def gost_main(gost_path: str, ll: str, ul:str):

    gost = pd.read_csv(gost_path, names=['source_lang', 'target_lang', 'source_word', 'translation'])
    languages = gost['source_lang'].unique()
    langs = make_lang_dic(languages)

    print(gost[gost['source_lang'] == langs[ll]])
    
    gosta = gost2gota(gost, langs, ll, ul)

    lipstick = set_lip(gosta)
    lippath = write_lip(gost_path, lipstick)
    return lippath

if __name__ == "__main__":
    gost_path = sys.argv[1]
    ll = sys.argv[2]
    ul = sys.argv[3]
    gost_main(gost_path, ll, ul)
