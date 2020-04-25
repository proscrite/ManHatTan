### MADTE: Multiple Answer Direct Translation Exercise ###
from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import *
import rnd_exercise_scheduler as daemon

def madte_main(lipstick_path):
    print('Welcome to MADTE')
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    qu, answ, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu, modality='dt')
    opts[answ] = True
    shufOpts = shuffle_dic(opts)
    BREAK = daemon.init()

    print('Global BREAK = ', BREAK)
    MA = MultipleAnswer(lipstick, lipstick_path)
    MA.load_question(qu)
    MA.load_options(qu, answ, modality='dt')
    MA.load_answers(shufOpts)

    out = MA.run()

if __name__ == "__main__":
    madte_main(sys.argv[1])
