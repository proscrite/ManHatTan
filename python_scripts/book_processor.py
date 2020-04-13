from googletrans import Translator
translator = Translator()
import pandas as pd
import numpy as np
import os
import sys
import re
import datetime

sys.path.append('~/Documents/ManHatTan/python_scripts/')
from rashib import *
from krahtos import *
from bulkTranslate import *
from init_lipstick import *

######### Main #########
if __name__ == "__main__":
    filename = f'/Users/pabloherrero/Documents/ManHatTan/kindle_raw/Il castello dei destini incrociati - Bloc-notes.html'
    dest_lang = 'es'
    src_lang = 'it'
    filepath, basename = os.path.split(filename)

    if 'html' in basename:
        print('Amazon Kindle file detected')
        cder_path = krahtos_main(filename)

    elif '.docx' in basename:
        print('Google Books file detected')
        cder_path = rashib_main(filename)

    assert '.cder' in cder_path, "Wrong CADERA extension"
    print("Starting automatic translation...")
    gota_path = bulkTranslate_main(cder_path, dest_lang, src_lang)
    assert '.got' in gota_path, "Wrong GOTA extension"

    print('Initializing word bank...')
    lippath = init_lipstick_main(gota_path)
    print("Done! You can start practicing")
#...

# GUI select raw kindle/playbooks -> file
# basename = input()
# dest_lang = input()
# src_lang = input()
# filename = blabla


# print(initializing word bank...)
# python init_lipstick.py gota_path
# print(Done! You can start practicing)
