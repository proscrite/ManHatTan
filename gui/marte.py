### MARTE: Multiple Answer Reverse Translation Exercise ###
from time import sleep
import sys
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
sys.path.append(ROOT_PATH+'/scripts/ML_duolingo')

from duolingo_hlr import *
from update_lipstick import *
# from kivy_multipleAnswer import *
from kivy_multipleAnswer import *

# import rnd_exercise_scheduler as daemon

def marte_main(lipstick_path, *largs):
    print('Welcome to MARTE: Multioption Answer Reverse Translation Exercise')
    if lipstick_path is None:
        if len(sys.argv) > 1:
            lipstick_path = sys.argv[1]
        else:
            print("Error: Missing lipstick_path argument.")
            sys.exit(1)

    modality = 'rt'
    
    MA = MultipleAnswer(lipstick_path, modality=modality)

    perf = MA.run()
    print(perf)

if __name__ == "__main__":
    marte_main(sys.argv[1])
