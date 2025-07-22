import pandas as pd
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

    langs = {}
    for la in languages:
        try:
            lang = dictTrans[la.lower()]
        except KeyError:
            pass
        langs[lang] = la
    return langs

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

    gost = pd.read_csv(gost_path, names=['source_lang', 'target_lang', 'source_word', 'translation'])
    languages = gost['source_lang'].unique()
    langs = make_lang_dic(languages)

    print(gost[gost['source_lang'] == langs[ll]])
    
    gosta = gost2gota(gost, langs, ll, ul)

    if ll == 'iw':
        gosta = remove_nikud(gosta)

    # print('GOST after remove nikud:', gosta.head(5) )
    ## Refactor: this is basically init_lipstick
    new_lip = set_lip(gosta, flag_lexeme=True)
    lippath = make_lippath(gost_path)

    if check_lip_exists(gost_path, lippath):
        current_lip = pd.read_csv(lippath)
        print('LIPSTICK already exists, updating with newly found entries')
        lipstick = add_new_gota_terms(new_lip, current_lip)
    
    else:
        lipstick = new_lip

    lipstick.to_csv(lippath, index=False)
    print('Created LIPSTICK file %s' %lippath)

    return lippath

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
