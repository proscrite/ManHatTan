from googletrans import Translator
translator = Translator()
import pandas as pd
import numpy as np
import sys
import datetime
from copy import deepcopy

def set_lip(gota : pd.DataFrame):

    cols0 = ['lexeme_id', 'translated_word', 'timestamp', 'history_seen', 'history_correct']

    lear_lang = gota.columns[0]
    ui_lang = gota.columns[1]
    timest = gota.creation_time.apply(lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f')).apply(lambda dt : int(datetime.datetime.timestamp(dt)))

    delta = timest - np.min(timest)
    ptruth = ((gota.right_hist ) / gota.seen_hist).fillna(0)
    lipstick = pd.DataFrame({'p_recall':ptruth})

    lipstick['timestamp'] = timest
    lipstick['delta'] = delta
    lipstick['user_id'] = 'pablo'  # Will be customizable later
    lipstick['learning_language'] = lear_lang
    lipstick['ui_language'] = ui_lang
    lipstick['lexeme_id'] = gota[lear_lang]
    lipstick['word_id'] = gota[ui_lang]
    lipstick['lexeme_string'] = 'lernt/lernen<vblex><pri><p3><sg>'  # Just to complete the column for now
    lipstick['history_seen'] = gota['seen_hist']   # Will change this in gotas
    lipstick['history_correct'] = gota['right_hist'].apply(lambda r : int(r))
    lipstick['session_seen'] = gota['seen_hist']   # Will change this in gotas
    lipstick['session_correct'] = gota['right_hist'].apply(lambda r : int(r))

def write_lip(gota_path : str, lipstick : pd.DataFrame):
    """Take basename from GOTA and write LIPSTICK file"""
    pathname = os.path.splitext(os.path.abspath(cadera_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'LIPSTICK', filename+'.lip')
    lipstick.to_csv(fpath, index=False)

    print('Created LIPSTICK file %s' %fpath)

######### Main #########
if __name__ == "__main__":
    gota_path = sys.argv[1]

    gota = pd.read_csv(gota_path, index_col=0)
    lipstick = set_lip(gota)
    write_lip(gota_path, lipstick)
