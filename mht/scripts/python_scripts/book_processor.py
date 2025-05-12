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
from gost import *
from init_lipstick import *

######### Main #########
def book_processor_main(filename: str, dest_lang: str, src_lang: str):

    filepath, basename = os.path.split(filename)

    if 'html' in basename:
        print('Amazon Kindle file detected')
        cder_path = krahtos_main(filename)

    elif '.docx' in basename:
        print('Google Books file detected')
        cder_path = rashib_main(filename)
    elif '.csv' in basename:
        print('Google Saved Translations detected')
        lippath = gost_main(filename, dest_lang, src_lang)
        print("Done! Now you can start practicing")
        return 0

    assert '.cder' in cder_path, "Wrong CADERA extension"
    print("Starting automatic translation...")
    gota_path = bulkTranslate_main(cder_path, dest_lang, src_lang)
    assert '.got' in gota_path, "Wrong GOTA extension"

    print('Initializing word bank...')
    lippath = init_lipstick_main(gota_path)
    print("Done! You can start practicing")

if __name__ == "__main__":
    filename = sys.argv[1]
    dest_lang = sys.argv[2]
    src_lang = sys.argv[3]
    book_processor_main(filename, dest_lang, src_lang)

#...

# GUI select raw kindle/playbooks -> file
# basename = input()
# dest_lang = input()
# src_lang = input()
# filename = blabla


# print(initializing word bank...)
# python init_lipstick.py gota_path
# print(Done! You can start practicing)
