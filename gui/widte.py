### WIDTE: Write Input Direct Translation Exercise ###
from time import sleep
import sys

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
sys.path.append(ROOT_PATH+'/scripts/ML_duolingo')

from bidi.algorithm import get_display
from duolingo_hlr import *
from update_lipstick import *
from kivy_writeInput import *

def widte_main(lipstick_path, *largs):
    print('Welcome to WIDTE: Written Input Direct Translation Exercise')
    if lipstick_path is None:
        if len(sys.argv) > 1:
            lipstick_path = sys.argv[1]
        else:
            print("Error: Missing lipstick_path argument.")
            sys.exit(1)

    modality = 'dt'
    WI = WriteInput(lipstick_path, modality='dt')

    perf = WI.run()
    print(perf)

if __name__ == "__main__":
    widte_main(sys.argv[1])
