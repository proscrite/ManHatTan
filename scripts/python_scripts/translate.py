import pandas as pd
import numpy as np
import sys
import os
import googletrans
from googletrans import Translator

class Translation:

    def __init__(self, cadera : str, dest : str, src : str, color : str = 'blue') -> pd.Series :
        """ Import source CADERA file and keep only column specified as 'color' """
        self.dfSrc = pd.read_csv(cadera, index_col=0)[color].dropna()
        self.src : str = src
        self.dest : str = dest
        self.translator = Translator()

    def detect_src(self, N : int = 0):
        """Auto-detect languages in wordset given and arrange them by occurrences
        Parameters:
        N : int = 0
            Number of words to sample from CADERA series. If left to 0, the whole Series is taken"""

        def compute_highest_scoring_language(dictNorm : dict, dictWeights : dict) -> dict:
            """Return highest scoring weighted language over the sample.
            The probability for each language results from summing over all occurrences the product of two factors:
                - Occurrences_language / sum(occurrences_languages)
                - confidence_occurrence """
            ret = dict()
            normFactor = sum(dictNorm.values())
            for key, language in dictWeights.items():
                ret[key] = language*dictNorm.get(key, 1) / normFactor
            return ret

        if N != 0:
            sample = self.dfSrc.sample(N)
        else:
            sample = self.dfSrc

        lang = [translator.detect(w).lang for w in sample]
        conf = [translator.detect(w).confidence for w in sample]
        dfLang = pd.DataFrame({'lang':lang, 'conf':conf})

        dictNorm = dfLang.lang.value_counts().to_dict()  # Dictionary with number of occurences per language
        normFactor = sum(dictNorm.values())              # Total number of words in sample

        a = dfLang.groupby('lang').sum().to_dict()['conf']
        dictWeights = {k: v / normFactor for k, v in a.items()}   # Weights per language, averaged by occurrences

        ret = compute_highest_scoring_language(dictNorm, dictWeights)
        maximum = max(ret, key=ret.get)
        return maximum, ret#[maximum]


    def main_translate(self) -> list:
        """Translate dfSrc from src to dest language
        Returns list of translate objects"""
        trans = [self.translator.translate(w, src=self.src, dest=self.dest) for w in self.dfSrc]
        return trans

    def arrange_dicDf(self) -> pd.DataFrame:
        trans = self.main_translate()
        dfDest = pd.Series([w.text for w in trans])
        dicDf = pd.DataFrame({self.src : self.dfSrc,  self.dest: dfDest})
        dicDf.names = [self.src, self.dest]
        return dicDf

    def detect_fails(self, meth : str = 'dest'):
        """Fails are interpreted as words that remained untranslated (if using default method 'src')
        or simply if the detected language doesn't correspond to 'dest'  """

        trans = self.main_translate()
        if meth == 'src':
            fails = np.where(translator.detect(w).lang == self.src for w in trans)[0]
        elif meth == 'dest':
            fails = np.where(translator.detect(w).lang != self.dest for w in trans)[0]
        return fails

    def fix_fails(self, meth : str = 'src'):
        """For failed translations, look into extra_data attribute 'possible-translation', flatten the list
        and take the first one in the correct language"""
        from copy import deepcopy
        def flatten_str_list(nested_list):
            """Flatten an arbitrarily nested list, without recursion (to avoid
            stack overflows). Returns a new list, the original list is unchanged.
            >> list(flatten_list([1, 2, 3, [4], [], [[[[[[[[[5]]]]]]]]]]))
            [1, 2, 3, 4, 5]
            >> list(flatten_list([[1, 2], 3]))
            [1, 2, 3]
            Note: additionally, only return type 'str' elements
            """
            nested_list = deepcopy(nested_list)

            while nested_list:
                sublist = nested_list.pop(0)

                if isinstance(sublist, list):
                    nested_list = sublist + nested_list
                else:
                    if type(sublist) == str:
                        yield sublist

        trans = self.main_translate()
        fails = self.detect_fails(meth)
        fixes = []
        for f in fails:
            messy_list = trans[f].extra_data['possible-translations']
            possibleTrans = [w for w in flatten_list(messy_list)]
            fixes.append(  possibleTrans[ np.where( [translator.detect(w).lang == self.dest for w in possibleTrans] ) [0][0]  ]  )
        return fixes


def write_gota(cadera : str, dicDf):
    """Take basename from cadera and write dictDf to GOTA file"""
    pathname = os.path.splitext(os.path.abspath(cadera_path))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'GOTAs', filename+'.cder')
    dicdf.to_csv(fpath)

    print('Created GOTA file %s' %fpath)

######## Main ########

cadera_path = sys.argv[1]
dest = sys.argv[2]
src = sys.argv[3]

### Check whether given dest and src languages are valid

from googletrans import LANGUAGES
langKeys = list(LANGUAGES.keys())

if dest not in langKeys:
    print('Invalid dest language. Choose from one of the following keys')
    print(langKeys)
    exit

if src not in langKeys:
    print('Invalid dest language. Choose from one of the following keys')
    print(langKeys)
    exit

transl = Translation(cadera = cadera_path, dest=dest, src=src)

dicDf = transl.arrange_dicDf()

write_gota(cadera_path, dicDf)
#transl.detect_fails()
