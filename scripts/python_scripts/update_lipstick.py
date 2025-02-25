import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('../../gui')
sys.path.append('../ML')
from duolingo_hlr import *


def update_speed(lipstick: pd.DataFrame, iw: str, new_speed: float):
    avg_v = lipstick.loc[iw, 'speed'].copy()
    ntest = lipstick.loc[iw, ['mdt_history', 'mrt_history', 'wdt_history', 'wrt_history']].sum()
    sumentries = ntest*avg_v
    new_avg = (sumentries + new_speed) / (ntest+1)
    lipstick.at[iw, 'speed'] = round(new_avg, 4) 
    return lipstick
 
def update_performance(lipstick : pd.DataFrame, iw : str, perf : float, mode = ['mdt', 'mrt', 'wdt', 'wrt']):
    """Update times the entry iw was practiced and the performance
        iw is the index column of lipstick, can be word_ul, word_ll, or a number"""
    
    print(f'Updating performance in mode {mode}')

    lipstick.loc[iw, mode+'_history'] += 1
    lipstick.loc[iw, mode+'_correct'] += perf
    lipstick.loc[iw, 'history_seen'] += 1
    lipstick.loc[iw, 'history_correct']+= perf
    lipstick.loc[iw, 'p_recall'] = round(lipstick.loc[iw, 'history_correct'] / lipstick.loc[iw, 'history_seen'], 3)

    return lipstick

def update_timedelta(lipstick : pd.DataFrame, iw : str):
    """Update last practice timestamp and timedelta"""
    today = int(datetime.datetime.timestamp(datetime.datetime.today()))
    lipstick.loc[iw, 'timestamp'] = today
    lipstick.delta = lipstick.timestamp - lipstick.timestamp.min()
    return lipstick

def train_model(lipstick : pd.DataFrame, lipstick_path : str):
    trainset, testset = read_data(lipstick_path, method='hlr', omit_lexemes=False)

    trainset += testset # Ignore the separation for the update

    model = SpacedRepetitionModel(method='hlr', omit_h_term=False, )
    model.train(trainset)
    prob = pd.Series({i.index: model.predict(i)[0] for i in trainset})
    lipstick.loc[:, 'p_pred'] = prob
    
    lipstick.sort_values('p_recall', inplace=True)
    lipstick['timestamp'] = lipstick['timestamp'].astype('int64')
    lipstick.to_csv(lipstick_path, index=False)

def update_all(lipstick : pd.DataFrame, lipstick_path : str, word : str, perform, speed, mode = ['mdt', 'mrt', 'wdt', 'wrt']):
    """Call all update functions and train hlr model"""
    lipstick.set_index('word_ul', inplace=True, drop=False)

    update_performance(lipstick, word, perform, mode=mode)
    update_speed(lipstick, word, speed)
    update_timedelta(lipstick, word)
    lipstick.sort_values('p_recall', inplace=True)
    lipstick.set_index('p_recall')
    lipstick.to_csv(lipstick_path, index=False)
    # sleep(1)
    # train_model(lipstick, lipstick_path)


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
