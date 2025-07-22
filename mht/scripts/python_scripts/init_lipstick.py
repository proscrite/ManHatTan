import pandas as pd
import numpy as np
import sys
import datetime
import os
import stanza
from random import shuffle
from bidi.algorithm import get_display
from copy import deepcopy

def get_lexemes_stanza(lip):
    """Get lexemes from a LIPSTICK DataFrame"""

    lang = lip.learning_language.iloc[0]
    if lang == 'iw':
        lang = 'he'
    nlp = stanza.Pipeline(lang=lang, processors='tokenize,pos,lemma,depparse', tokenize_pretokenized=True)
    # nlp = stanza.Pipeline(lang=lang, processors='tokenize,mwt,pos,lemma,depparse')
    tokens_list = list(lip['word_ll'].values)
    tokens_list = [get_display(t) for t in tokens_list]
    print('In get_lexemes:', tokens_list[:9])
    print(f'Type token[0]: {type(tokens_list[0])}')
    lexemes = []

    doc = nlp(tokens_list)
    for sent in doc.sentences:
        lexeme_string = ''
        # print(len(sent.words))
        for word in sent.words:
            lexeme_string += word.text 
            if word.lemma:
                lexeme_string += '/' + word.lemma 
            if word.upos:
                lexeme_string += '<' + word.upos + '>'
            if word.feats:
                feats = word.feats.split('|')
                lexeme_string += ''.join(feat.split('=')[1] +'|' for feat in feats)
            if word.deprel != 'root':
                lexeme_string +=  ',' + word.deprel
        lexemes.append(lexeme_string)
    return lexemes

def get_lexemes_apertium(lipstick, lear_lang):
    """Get lexemes from a LIPSTICK DataFrame using Apertium"""
    import apertium
    lexemes = []
    for wd in lipstick.word_ll:
        tagSplit = str(apertium.tag(lear_lang, wd)[0]).split('/')
        lexemes.append(tagSplit[0] + '/' + tagSplit[1])
    
    # Return the lexemes
    return lexemes

def get_word_vectors(lip, nlp):    # Need to implement this in main workflow
    """Get word vectors from a LIPSTICK DataFrame
    Args:
        lip (pd.DataFrame): LIPSTICK DataFrame
        nlp (spacy.Pipeline): Spacy NLP pipeline
    Returns:
        vect_word (list): List of words with vectors
        vectors (list): List of vectors corresponding to the words
    """

    all_entries = lip.word_ll.values.tolist()
    vect_word = []
    vectors = []
    for word in all_entries:
        token = nlp(word)[0]
        # Check if both tokens have vectors
        if token.has_vector:
            vect_word.append(word)
            vectors.append(token.vector)
    return vect_word, vectors

def write_word_vectors(vect_word, vectors, lippath):
    """Write word vectors to a file
    Args:
        vect_word (list): List of words with vectors
        vectors (list): List of vectors corresponding to the words
        lippath (str): Path to the LIPSTICK file
    """
    # Get the base name of the LIPSTICK file
    lip_bname = os.path.splitext(os.path.split(lippath)[1])[0]
    # Create a new file name for the word vectors
    vec_bname = os.path.join(os.path.dirname(lippath), lip_bname + '_vectors.txt')
    
    with open(vec_bname, 'w') as f:
        np.savez(f, tokens=vect_word, vectors=vectors)
    print(f"Word vectors written to {vec_bname}")

def force_rtl(s):
    # Add RLM only if the string contains Hebrew characters
    return ''.join('\u200F' + str(w) if any('\u0590' <= c <= '\u05FF' for c in str(w)) else str(w) for w in [s])


def set_lip(gota : pd.DataFrame, flag_lexeme = False):
    """Provisional simple initialization of lipstick from GOTA.
        Attrs:
        ------
        p_recall : truth recall probability = history_correct/history_correct
        timestamp : last time practice timestamp
        delta : timedelta w.r.t. most unpracticed word (with minimum timestamp)
        user_id : user name
        learning_language: target language
        ui_language: user reference language
        lexeme_id: word in target language, lexeme in the future?
        word_id: word in reference language
        lexeme_string: lexeme tag with grammatical/syntactical information
        history_seen: times the word has been practiced from initialization
        history_correct: times the translation has been correctly recalled from initialization
        session_seen: practice times in last session (not implemented)
        session_correct: correctly recalled times in last session (not implemented)
        mdt_history: times the word has been practiced in mdt mode
        mdt_correct: times the word has been correctly recalled in mdt mode (attack attribute)
        mrt_history: times the word has been practiced in mrt mode
        mrt_correct: times the word has been correctly recalled in mrt mode (defense attribute)
        wdt_history: times the word has been practiced in wdt mode
        wdt_correct: times the word has been correctly recalled in wdt mode (special attack attribute)
        wrt_history: times the word has been practiced in wrt mode
        wrt_correct: times the word has been correctly recalled in wrt mode (special defense attribute)
        speed: average speed of recall
        Additional attrs:
        ------
        p_pred: predicted probability from hlr model (not in initialization)
    """
    cols0 = ['lexeme_id', 'translated_word', 'timestamp', 'history_seen', 'history_correct']

    lear_lang = gota.columns[0]
    ui_lang = gota.columns[1]
    timest = gota.creation_time # .apply(lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f')).apply(lambda dt : int(datetime.datetime.timestamp(dt)))

    delta = timest - np.min(timest)
    # ptruth = ((gota.right_hist ) / gota.seen_hist).fillna(0)   # Legacy from using GOTA as DB corpus with updatePerformance.py
    ptruth = pd.Series(np.zeros_like(timest))  # Initialize on 0, also for seen and correct attrs.
    lipstick = pd.DataFrame({'p_recall':ptruth})

    pathnid = '/Users/pabloherrero/Documents/ManHatTan/mht/gui/Graphics/index_stage_0.csv'
    lenlip = len(lipstick)
    stage0_nids = pd.read_csv(pathnid, index_col=None).T.values[0][:lenlip]
    shuffle(stage0_nids)

    lipstick['n_id'] = stage0_nids
    lipstick['timestamp'] = timest.astype('int')
    lipstick['delta'] = delta
    lipstick['user_id'] = 'pablo'  # Will be customizable later
    lipstick['learning_language'] = lear_lang
    lipstick['ui_language'] = ui_lang
    lipstick['word_ll'] = gota[lear_lang]
    lipstick['word_ul'] = gota[ui_lang]
    lipstick['lexeme_string'] = 'No lexeme'
    lipstick['history_seen'] = 0
    lipstick['history_correct'] = 0
    lipstick['session_seen'] = 0
    lipstick['session_correct'] = 0
    lipstick['p_pred'] = ptruth
    lipstick['mdt_history'] = 0
    lipstick['mdt_correct'] = 0
    lipstick['mrt_history'] = 0
    lipstick['mrt_correct'] = 0
    lipstick['wdt_history'] = 0
    lipstick['wdt_correct'] = 0
    lipstick['wrt_history'] = 0
    lipstick['wrt_correct'] = 0
    lipstick['speed'] = 0.
    lipstick['rebag'] = False

    # print('In set_lip:', lipstick.head(5))
    if flag_lexeme:
        try:
            lexemes = get_lexemes_stanza(lipstick)
            lipstick['lexeme_string'] = lexemes
        except FileNotFoundError as e:
            print(f"Error: {e}. Please ensure that the Stanza models are installed for the language {lear_lang}.")
            print("You can install them using: stanza.download('language_code')")
            
            try:
                lexemes = get_lexemes_apertium(lipstick, lear_lang)
            except Exception as e:
                print(f"Error with Apertium: {e}. Using default lexeme string.")
                lexemes = ['lernt/lernen<vblex><pri><p3><sg>'] * len(lipstick)
        lipstick['lexeme_string'] = lexemes
        

    if lipstick['learning_language'].iloc[0] in ['he', 'iw']:
        
        lipstick['word_ll'] = [w[::-1] for w in lipstick['word_ll'].values]  # Reverse Hebrew words
        print('In set_lip, displayed_word_ll:', lipstick['word_ll'].head(5))

    return lipstick
    # lipstick['history_seen'] = gota['seen_hist']   # Will change this in gotas     # legacy: to retrieve performance when using GOTA as DB
    # lipstick['history_correct'] = gota['right_hist'].apply(lambda r : int(r))
    # lipstick['session_seen'] = gota['seen_hist']   # Will change this in gotas
    # lipstick['session_correct'] = gota['right_hist'].apply(lambda r : int(r))

def check_lip_exists(gota_path: str, lippath: str):
    gota_bname = os.path.splitext(os.path.split(gota_path)[1])[0]
    lip_bname = os.path.splitext(os.path.split(lippath)[1])[0]
    return gota_bname == lip_bname

def add_new_gota_terms(new_lip: pd.DataFrame, current_lip: pd.DataFrame):
    """Include updated terms from GOTA respecting the practiced ones already present"""
    
    newEntries = []

    for i,wd in zip(new_lip.index, new_lip.word_ul):
        if wd not in current_lip.word_ul.values:
            
            newEntries.append(i)

    current_lip = pd.concat([current_lip, new_lip.iloc[newEntries] ])
    return current_lip

def make_lippath(gota_path : str):
    """Take basename from GOTA and write LIPSTICK file"""
    pathname = os.path.splitext(os.path.abspath(gota_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    dirPathproc = dirPath.replace('raw', 'processed')
    fpath = os.path.join(dirPathproc, 'LIPSTICK', filename+'.lip')
    return fpath


def init_lipstick_main(gota_path : str):

    gota = pd.read_csv(gota_path, index_col=0)
    new_lip = set_lip(gota, flag_lexeme=True)

    lippath = make_lippath(gota_path)

    if check_lip_exists(gota_path, lippath):
        current_lip = pd.read_csv(lippath)
        print('LIPSTICK already exists, updating with newly found entries')
        lipstick = add_new_gota_terms(new_lip, current_lip)
    
    else:
        lipstick = new_lip

    lipstick.to_csv(lippath, index=False)
    print('Created LIPSTICK file %s' %lippath)

    return lippath

######### Main #########
if __name__ == "__main__":
    gota_path = sys.argv[1]
    init_lipstick_main(gota_path)