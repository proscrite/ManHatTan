import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

from mht.scripts.ML_duolingo.duolingo_hlr import *


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

def update_eligibility(lipstick: pd.DataFrame, iw: str, stop_level : int = 6):
    """Update stop attribute if the level of the word (history_correct) is a multiple of stop_level (6 by default) """
    current_level = lipstick.loc[iw, 'history_correct']        # Select current level (total number of successful exercises)
    residual_level = (current_level + 1) % (stop_level + 1)    # Check whether it is a multiple of stop_level (+1 to avoid zero as multiple)

    flag_update_team = False
    if residual_level == stop_level:
        lipstick.at[iw, 'rebag'] = True

    if (lipstick['rebag'] == True).all():         # If all entries have been sufficiently practiced: update_team (rebag) with new entries
        flag_update_team = True
    return lipstick, flag_update_team

def rebag_team(current_team: pd.DataFrame, team_lip_path: str):
    """Rebag function: return current_team to main lipstick and sample again for a new team"""
    
    dropped_rebag_team = current_team.drop(current_team[current_team['rebag'] == False].index)
    # print(f"team with dropped rebag = False: {dropped_rebag_team}")
    ##### This "test" is necessary to avoid an error of calling rebag_team in infinite loop when all entries are False
    try:
        print(dropped_rebag_team.index[0])

    except IndexError as e:
        ##### Return 0 allows continue_rebag_team to return to main menu
        print('All rebag entries in current team are False. No rebagging needed yet')
        return 0
    
    main_lip_path = team_lip_path.replace('_team', '')   # Extract main_lip_path from current_team
    main_lip = pd.read_csv(main_lip_path)                # Read main_lip
    main_lip.set_index('word_ul', inplace=True, drop=False)
    current_team.set_index('word_ul', inplace=True, drop=False)

    team_inds = current_team['word_ul']                       # Assign the current_team entries to main_lip and write
    main_lip.update(current_team)
    print(f"Before writing, main lip is \n{main_lip.loc[team_inds]}")
    main_lip.to_csv(main_lip_path, index=False)

    # Resample:
    new_team = main_lip.drop(main_lip[main_lip['rebag'] == True].index).head(6).copy()
    try:
        print(new_team.index[0])
    except IndexError as e:
        print('Main lipstick is fully rebagged. Resetting it')
        main_lip['rebag'] = False
        main_lip.to_csv(main_lip_path, index=False)
        new_team = main_lip.drop(main_lip[main_lip['rebag'] == True].index).sample(6).copy()
        return new_team, 2
    
    return new_team

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
    _, flag_update_team = update_eligibility(lipstick, word)
    
    lipstick.sort_values('p_recall', inplace=True)
    lipstick.set_index('p_recall')
    lipstick.to_csv(lipstick_path, index=False)

    print('Eligibility flag:', flag_update_team)
    if flag_update_team:
        print('Calling for Rebagging team...')
        return True
    else:
        print('No rebagging needed yet')
        return False
    
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