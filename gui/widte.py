### WIDTE: Write Input Direct Translation Exercise ###
from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_writeInput import *

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    #print(lipstick.loc[qu])
    word_ll, word_ul, iqu = set_question(lipstick_path, size_head=10)

    WI = WriteInput(lipstick, lipstick_path,
      word_ll=word_ll, word_ul=word_ul, modality='dt')
    WI.load_question()

    perf = WI.run()
    print(perf)