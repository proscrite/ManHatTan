### MADTE: Multiple Answer Reverse Translation Exercise ###
from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import *

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ll', inplace=True, drop=False)

    answ, qu, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu, modality='rt')
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer(lipstick, lipstick_path)
    MA.load_question(qu)
    MA.load_options(qu, answ, modality='rt')
    MA.load_answers(shufOpts)

    perf = MA.run()
    print(perf)
