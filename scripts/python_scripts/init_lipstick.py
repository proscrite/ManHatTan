import pandas as pd
import numpy as np
import sys
import datetime
import os
from random import shuffle
from copy import deepcopy

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

    if flag_lexeme:
        lexeme = []
        for wd in lipstick.word_ll:
            tagSplit = str(apertium.tag(lear_lang, wd)[0]).split('/')
            lexeme.append(tagSplit[0] + '/' + tagSplit[1])
    else:
        lexeme = 'lernt/lernen<vblex><pri><p3><sg>'

    pathnid = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/index_stage_0.csv'
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
    lipstick['lexeme_string'] = lexeme
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

    return lipstick
    # lipstick['history_seen'] = gota['seen_hist']   # Will change this in gotas     # legacy: to retrieve performance when using GOTA as DB
    # lipstick['history_correct'] = gota['right_hist'].apply(lambda r : int(r))
    # lipstick['session_seen'] = gota['seen_hist']   # Will change this in gotas
    # lipstick['session_correct'] = gota['right_hist'].apply(lambda r : int(r))


def write_lip(gota_path : str, lipstick : pd.DataFrame):
    """Take basename from GOTA and write LIPSTICK file"""
    pathname = os.path.splitext(os.path.abspath(gota_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'LIPSTICK', filename+'.lip')
    lipstick.to_csv(fpath, index=False)

    print('Created LIPSTICK file %s' %fpath)
    return fpath

def init_lipstick_main(gota_path : str):

    gota = pd.read_csv(gota_path, index_col=0)
    lipstick = set_lip(gota)
    lippath = write_lip(gota_path, lipstick)

    return lippath

######### Main #########
if __name__ == "__main__":
    gota_path = sys.argv[1]
    init_lipstick_main(gota_path)