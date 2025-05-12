import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('~/Documents/ManHatTan/python_scripts/')
from bulkTranslate import *

def test_hist_column(gota: pd.DataFrame):
    """Test whether performance columns exist in gota and create them else"""
    try:
        gota['seen_hist']
    except KeyError:
        print("Creating column 'seen_hist'")
        gota['seen_hist'] = 0

    try:
        gota['right_hist']
    except KeyError:
        print("Creating column 'right_hist'")
        gota['right_hist'] = 0

    return gota

def update_performance(gota : pd.DataFrame, iw : int, perf : float):
    """Update times the entry iw was practice and the performance"""
    gota['seen_hist'].loc[iw] += 1
    gota['right_hist'].loc[iw] += perf
    return gota

######### Main #########

if __name__ == "__main__":
    gota_path = sys.argv[1]
    idw = sys.argv[2]
    perf = sys.argv[3]

    idw = idw.replace(',', '')

    print('gota_path: %s, idw : %s, perf: %s' %(gota_path, idw, perf))
    gota = pd.read_csv(gota_path, index_col=0)
    gota = test_hist_column(gota)
    newGota = update_performance(gota, int(idw), float(perf))

    print('Updating performance...')
    write_gota(gota_path, newGota)
