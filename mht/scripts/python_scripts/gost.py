import pandas as pd
import datetime
import sys
from hebrew import Hebrew

from mht.scripts.python_scripts.init_lipstick import set_lip, make_lippath, check_lip_exists, add_new_gota_terms

def make_lang_dic(languages: list):
    """Return a dict with inverted langcodes
    Ex: {'en': 'English'
        'eu': 'Basque'}
    Takes a list with long languages names ('English', 'Basque')
    """
    from googletrans import LANGCODES as dictTrans

    langs_dict = {}
    for la in languages:
        try:
            lang = dictTrans[la.lower()]
            langs_dict[lang] = la
        except KeyError:
            pass
    return langs_dict

def gost2gota(gost: pd.DataFrame, langs: dict, ll: str, ul:str):
    """Adapt GOST to GOTA format for LIPSTICK processing
    Parameters:
        ll: learning language in short format
        ul: user language in short format ('en', 'de', 'es'...)
    """
    lll, lul = langs[ll], langs[ul]             # Long-format Learning Language // Long-format User Language
    # Group and rearrange the words by language
    gota = pd.DataFrame({ll:[], ul: []})
    gota[ll] = gost.apply(lambda x: x["source_word"] if x["source_lang"] == lll else x["translation"], axis=1 )
    gota[ul] = gost.apply(lambda x: x["source_word"] if x["source_lang"] == lul else x["translation"], axis=1 )

    # Add creation timestamp
    today = int(datetime.datetime.timestamp(datetime.datetime.today()))
    gota['creation_time'] = today
    return gota

def remove_nikud(gost):
    gost['iw'] = gost['iw'].apply(lambda x: Hebrew(x).no_niqqud())
    gost['iw'] = gost['iw'].apply(lambda x: str(x))
    return gost

def gost_main(gost_path: str, ll: str, ul:str):
    """Main function to process GOST file and convert it to GOTA format
    Parameters:
        gost_path: path to the GOST csv file
        ll: learning language (short format: en, de, es, it, iw...)
        ul: user language (short format)
    """
    gost = pd.read_csv(gost_path, names=['source_lang', 'target_lang', 'source_word', 'translation'])
    languages = gost['source_lang'].unique()
    langs_dict = make_lang_dic(languages)

    if len(languages) < 2:
        print('GOST file does not contain enough languages to process. Exiting...')
        return None
    print('GOST file contains the following languages:', languages)
    if ll not in langs_dict or ul not in langs_dict:
        print('Learning language (%s) or User language (%s) not found in GOST file. Exiting...' %(ll, ul))
        return None
    
    
    
    gota_df = gost2gota(gost, langs_dict, ll, ul)

    if ll == 'iw':
        gota_df = remove_nikud(gota_df)

    return gota_df

if __name__ == "__main__":
    """Welcome to GOST processing: GOogle-Saved Translations: 
    Input: csv export from google translation bank
    Output: LIPSTICK ready for practice
    Parameters: 
        gost_path: path to the csv file with Google Saved Translations
        ll: learning language (short format: en, de, es, it, iw...)
        ul: user language (short format)
    """

    gost_path = sys.argv[1]
    ll = sys.argv[2]
    ul = sys.argv[3]
    gost_main(gost_path, ll, ul)
