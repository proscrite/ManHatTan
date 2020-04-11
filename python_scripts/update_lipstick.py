import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('../python_scripts/')
sys.path.append('../ML')
from duolingo_hlr import *

def update_performance(lipstick : pd.DataFrame, iw : str, perf : float):
    """Update times the entry iw was practice and the performance"""
    lipstick.loc[iw, 'history_seen'] += 1
    lipstick.loc[iw, 'history_correct']+= perf
    lipstick.loc[iw, 'p_recall'] = lipstick.loc[iw, 'history_seen'] / lipstick.loc[iw, 'history_correct']
    return lipstick

def update_timedelta(lipstick : pd.DataFrame, iw : str):
    """Update last practice timestamp and timedelta"""
    today = int(datetime.datetime.timestamp(datetime.datetime.today()))
    lipstick.loc[iw, 'timestamp'] = today
    lipstick.delta = lipstick.timestamp - lipstick.timestamp.min()
    return lipstick

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    idw = sys.argv[2]
    prob = sys.argv[3]
    perf = sys.argv[4]
    print('index : ', int(idw))
    print('probability : ', prob)
    print('performance : ', perf)

    lipstick = pd.read_csv(lipstick_path)

    newLipstick = update_performance(lipstick, int(idw), float(perf))
    newLipstick = update_timedelta(newLipstick, int(idw))

    print('Updating performance...')
    newLipstick.to_csv(lipstick_path, index=False)

    #### Now train the model  ####

    trainset, testset = read_data(lipstick_path, method='hlr', omit_lexemes=False)

    trainset += testset # Ignore the separation for the update

    model = SpacedRepetitionModel(method='hlr', omit_h_term=False, )
    model.train(trainset)

    prob = pd.Series({i.index: model.predict(i)[0] for i in trainset})
    newLipstick.p_pred.update(prob)

    newLipstick.sort_values('p_recall', inplace=True)
    newLipstick.to_csv(lipstick_path, index=False)
