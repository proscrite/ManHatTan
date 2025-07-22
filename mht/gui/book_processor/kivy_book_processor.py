
import kivy.core.window as window
from kivy.base import EventLoop
from kivy.cache import Cache
from mht import gui

import os
import asyncio
from glob import glob
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

# from duolingo_hlr import *

from mht.scripts.python_scripts.rashib import rashib_main
from mht.scripts.python_scripts.krahtos import krahtos_main
from mht.scripts.python_scripts.gost import gost_main
from mht.scripts.python_scripts.bulkTranslate import bulkTranslate_main
from mht.scripts.python_scripts.init_lipstick import *
from mht.scripts.python_scripts.update_lipstick import *
from mht.gui.common import PATH_PLAYBOOKS, PATH_GOOGLE_TRANSL, PATH_KINDLES


from mht.gui.book_processor.kivy_select_book import BookButton
from mht.gui.book_processor.kivy_cadera_DfWidget import choose_color_main
from mht.gui.book_processor.kivy_choose_lang import choose_lang_main

class addNewBook(gui.App):

    def __init__(self):
        gui.App.__init__(self)
        self.grid = gui.GridLayout(cols=2)
        self.path : str

    def load_books(self):
        kindles = PATH_KINDLES 
        playbooks = PATH_PLAYBOOKS 
        googletranslations = PATH_GOOGLE_TRANSL
        books_full = glob(kindles)
        books_full += glob(playbooks)
        books = {}

        for b in books_full:
            dirpath, filename = os.path.split(b)
            filename = os.path.splitext(filename)[0]
            books[filename] = b

            op = BookButton(filename, b)
            #op = Button(text=filename, on_release=self.return_path(b))
            self.grid.add_widget(op)

    def set_path(self, path):
        self.path = path

    def build(self):
        lb = gui.Label(text='Select book to process:', size_hint=(1,1))
        self.giveup = gui.Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        self.giveup.bind(on_release=self.exit)
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)
        return self.grid

    def run(self):
        super().run()
        return self.path

    def exit(self, instance):
        print("break")
        gui.App.stop(self)


def reset():
    if not EventLoop.event_listeners:
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}


def add_new_book_main():
    AB = addNewBook()
    AB.load_books()
    filename = AB.run()
    flag_needs_processing = True

    filepath, basename = os.path.split(filename)
    if '.html' in basename:
        print('Amazon Kindle file detected')
        cder_path = krahtos_main(filename)

    elif '.docx' in basename:
        print('Google Books file detected')
        cder_path = rashib_main(filename)
    
    elif '.csv' in basename:
        print('Google Saved Translations detected')
        flag_needs_processing = False
        gota_df = gost_main(filename, dest_lang, src_lang)
        print("Done! Now you can start practicing")

    if flag_needs_processing:
        assert '.cder' in cder_path, "Wrong CADERA extension"
        reset()
        word_color = choose_color_main(cder_path)
        reset()
        user_lang, learn_lang = choose_lang_main(cder_path, word_color)
        print('user_lang: %s\nlearning_lang: %s' %(user_lang, learn_lang))
        print('Words color: %s' %word_color)

        # Detect language using asyncio and googletrans
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gota_path = loop.run_until_complete(
            bulkTranslate_main(cder_path, word_color, user_lang, learn_lang)
        )
        loop.close()
        assert '.got' in gota_path, "Wrong GOTA extension"

        print('Initializing word bank...')

    lippath = init_lipstick_main(gota_path)
    print("Done! You can start practicing")

    # Call MainAppView() with Practice button, currentBook selector, Progress/word DB view...

if __name__ == "__main__":
    add_new_book_main()
    #learn_lang = Translator().detect(cadera.to_string()).lang

    #book_processor_main(path, dest_lang, src_lang)
