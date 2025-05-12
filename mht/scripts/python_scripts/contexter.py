import apertium
import re
import sys
sys.path.append('../python_scripts/')
from bulkTranslate import *

from googletrans import Translator
translator = Translator(service_urls=['translate.google.com'])

corpus_file = '../ML/frequency/frequent.txt'
corpus = pd.read_table(corpus_file, sep='\s+', engine='python', index_col=0)


def find_uncommon_words(sentence: str, corpus: pd.DataFrame) -> dict:
    """Find the candidate words whose baseform aren't among the 5000 most used words in English
        If all words are among the most common, store the least common one
        If more than one word is deemed candidate, the user will be prompted to select the target."""
    words = sentence.split()
    candidates = {}
    maxRank = 0
    for i,w in enumerate(words):
        anaWd = apertium.analyze('en', w.lower())
        if len(anaWd) > 1: # For composite words
            baseform = w.lower()
        else:
            try:
                if 'vblex' in [i[0].tags[0] for i in anaWd[0].readings]:
                    baseform = apertium.analyze('en', 'moving')[0].readings[-1][0].baseform  # The verb is always the last reading option, so access it directly with [-1]
                else:
                    baseform = anaWd[0].readings[0][0].baseform
            except IndexError:
                print('Index error with ', w, anaWd)

        if baseform == 'prpers': baseform = w.lower()

        if baseform.lower() not in corpus.Word.values:
            # If the word is not among the most common ones it is automatically a candidate
            candidates[i] = w.lower()
        else:
            # Else store the rank of occurrence and store the least common among them
            rank = corpus.Word[baseform == corpus.Word.values].index[0]  # The index[0] selects the most frequent option in the case an entry appears more than once in the corpus (ex. 'in' as preposition or adjective)
            if rank > maxRank:
                maxRank = rank
                least_common = w.lower()
                least_position = i

    if len(candidates) == 0:     # If all words are among the most common return the least frequent
        candidates[i] = least_common
    return candidates

def revTransl_allPossible(candidate: str, dest_lang: str, src_lang: str):
    """Check all possible translations in google translator entry"""
    print('Session: ', translator.client)
    Transl = translator.translate(candidate, src=dest_lang, dest=src_lang)
    try:
        optsTransl = Transl.extra_data['all-translations'][0][1]     # For assured translations with more than one meaning for the word
    except TypeError:
        try:
            optsTransl = Transl.extra_data['possible-translations'][0][2] # For likely but not sure translation possibilities
            optsTransl = [op[0] for op in optsTransl]
        except TypeError:
            optsTransl = [Transl.text]
    return optsTransl

def revTranslate_test(candidate: str, sentence_src: str, dest_lang: str, src_lang: str):
    """Reverse translate candidate word and check whether some possible translation is in original src entry"""
    optsTransl = revTransl_allPossible(candidate, dest_lang, src_lang)

    for op in optsTransl:
        if op in sentence_src:
            return op
        else:
            pass
    return False

def revAperTranslate_test(candidate: str, sentence_src: str, dest_lang: str, src_lang: str):
    revTrAp = apertium.translate(src_lang, dest_lang, candidate)
    return revTrAp if revTrAp in sentence_src else False

def infer_by_exclusion(sentence: str, sentence_src: str, candidates: list, dest_lang: str, src_lang: str)->list:
    """Reverse translate the common words (those included in the corpus)
        and exclude them from the original entry"""
    common_wd = {}
    words = sentence.split()
    words_src = sentence_src.split()
    for i, w in enumerate(words_src):
        optTransl = revTransl_allPossible(candidate=w, dest_lang=dest_lang, src_lang=src_lang)

        for op in optTransl:
            if op in candidates.values():
                break

        common_wd[i] = optTransl[0]

    for i in sorted(list(common_wd.keys()), reverse=True):
        words_src.pop(i)
    return words_src if len(words_src) > 0 else False

def loop_over_sentences(lipstick: pd.DataFrame, dest_lang: str, src_lang: str):
    """Loop over all entries in LIPSTICK with over 3 words, predict the least common (English-translated) word,
        attempt to find original one by reverse translation"""

    for i,(entry_ui, entry_src) in enumerate(zip(lipstick.word_ul, lipstick.word_ll)):
        if len(entry_ui.split()) > 3:
            print('\n', i, entry_ui)
            print(entry_src)
            candidates = find_uncommon_words(entry_ui, corpus)
            print('Candidates: ', candidates)

            for c in candidates:
                revC = revTranslate_test(candidates[c], entry_src, dest_lang, src_lang)
                if revC == False:
                    revC = revAperTranslate_test(candidates[c], entry_src, dest_lang, src_lang)
                if revC == False:
                    print('Reverse translation failed for ', c, '... inferring by exclusion')
                    revC = infer_by_exclusion(entry_ui, entry_src, candidates, dest_lang, src_lang)
                if (revC == False) or (c == -1): # Ask for user confirmation
                    print('Could not find reverse translation for ', candidates[c])
                else:
                    print('Found least common word: ', candidates[c], revC)
                    lipstick.loc[entry_src, 'word_ll'] = revC
                    lipstick.loc[entry_src, 'word_ul'] = candidates[c]
                    lipstick.loc[entry_src, 'context'] = entry_src

    return lipstick


def contexter_main(lippath : str, word_color: str, dest_lang : str, src_lang : str):

    lipstick = pd.read_csv(lippath)
    lipstick['context'] = pd.Series(np.zeros_like(lipstick.delta))
    lipstick.set_index('word_ll', drop=False, inplace=True)
    contexted_lips = loop_over_sentences(lipstick, dest_lang, src_lang)

    lipstick.sort_values('p_recall', inplace=True)
    lipstick.to_csv(lipstick_path, index=False)


######### Main #########
if __name__ == "__main__":
    lippath = sys.argv[1]
    word_color = sys.argv[2]
    dest_lang = sys.argv[3]
    src_lang = sys.argv[4]

    contexter_main(lippath, word_color, dest_lang, src_lang)
