from random import sample
import pandas as pd
import numpy as np
import stanza
# -*- coding: utf-8 -*-

def get_random_nid(lipstick):
    """Get a random n_id from the available ones in stage 0"""
    # Ensure that lipstick is initialized
    if lipstick.empty:
        raise ValueError("Lipstick DataFrame is empty. Please initialize it first.")
    
    # Get the path to the stage 0 n_ids
    pathnid = '/Users/pabloherrero/Documents/ManHatTan/mht/gui/Graphics/index_stage_0.csv'
    stage0_nids = pd.read_csv(pathnid, index_col=None).T.values[0]
    available_nids = np.setdiff1d(stage0_nids, lipstick['n_id'].values)
    random_nid = sample(list(available_nids), 1)[0]
    
    return random_nid

def get_single_lexeme(lip):
    """Get lexeme for a single LIPSTICK entry"""

    lang = lip['learning_language']
    token = lip['word_ll']

    if lang == 'iw':
        lang = 'he'

    nlp = stanza.Pipeline(lang=lang, processors='tokenize,pos,lemma,depparse', tokenize_pretokenized=True)
    # nlp = stanza.Pipeline(lang=lang, processors='tokenize,mwt,pos,lemma,depparse')
    print(f'Token: {token}')
    print(f'Type token[0]: {type(token)}')

    doc = nlp(token)
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
    return lexeme_string

def init_hatched_egg(egg : pd.DataFrame, word_ul : str, random_nid : int, flag_lexeme = False):
    """Initialize a new entry in the egg dataframe for a specific word."""
    egg_entry = egg.loc[word_ul].copy()
    egg_entry['n_id'] = random_nid

    egg_entry['session_seen'] = 0
    egg_entry['session_correct'] = 0
    egg_entry['p_pred'] = 0
    egg_entry['rebag'] = False
    if flag_lexeme:
        lexeme = get_single_lexeme(egg_entry)
        egg_entry['lexeme_string'] = lexeme
    else:
        egg_entry['lexeme_string'] = 'No lexeme'
    return egg_entry

def add_egg_to_lipstick(egg_entry, lipstick):
    """Add a new egg entry to the lipstick DataFrame."""
    # Ensure that egg_entry is a Series with the correct index
    if not isinstance(egg_entry, pd.Series):
        raise ValueError("egg_entry must be a pandas Series.")
    # Check if the word_ul exists in lipstick
    if egg_entry['word_ul'] in lipstick.index:
        raise ValueError(f"Word '{egg_entry['word_ul']}' already exists in lipstick DataFrame.")
    # Add the egg entry to the lipstick DataFrame
    
    lipstick = lipstick.set_index('word_ul', drop=False)
    new_lipstick = pd.concat([lipstick, egg_entry.to_frame().T])
    # Reset the index to ensure word_ul is the index
    new_lipstick = new_lipstick.reset_index(drop=True)

    return new_lipstick

def delete_word_from_egg(word_ul: str, egg_path: str):
    """Delete the word from the EGG database after hatching."""
    egg_df = pd.read_csv(egg_path)
    if word_ul in egg_df['word_ul'].values:
        egg_df = egg_df[egg_df['word_ul'] != word_ul]
        egg_df.to_csv(egg_path, index=False)
        print(f"Removed {word_ul} from EGG database after hatching.")
    else:
        print(f"{word_ul} not found in EGG database.")