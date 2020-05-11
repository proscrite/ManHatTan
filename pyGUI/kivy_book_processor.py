from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

import kivy.core.window as window
from kivy.base import EventLoop
from kivy.cache import Cache


from functools import partial
from time import sleep
from glob import glob
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from rashib import *
from krahtos import *
from bulkTranslate import bulkTranslate_main
from googletrans import Translator

from gost import *
from init_lipstick import *

from kivy_multipleAnswer import FTextInput
from kivy_select_book import BookButton
from kivy_choose_word_color import choose_color_main
from kivy_choose_lang import choose_lang_main


class addNewBook(App):

    def __init__(self):
        App.__init__(self)
        self.grid = GridLayout(cols=2)
        self.path : str

    def load_books(self):
        #kindles = '/Users/pabloherrero/Documents/ManHatTan/kindle_raw/*'
        playbooks = '/Users/pabloherrero/Documents/ManHatTan/playbooks_raw/*'
        books_full = glob(playbooks)
        #books_full.append(glob(playbooks))
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
        lb = Label(text='Select book to process:', size_hint=(1,1))
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        self.giveup.bind(on_release=self.exit)
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)
        return self.grid

    def run(self):
        super().run()
        return self.path

    def exit(self, instance):
        print("break")
        App.stop(self)


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

    filepath, basename = os.path.split(filename)
    if 'html' in basename:
        print('Amazon Kindle file detected')
        cder_path = krahtos_main(filename)

    elif '.docx' in basename:
        print('Google Books file detected')
        cder_path = rashib_main(filename)
    """elif '.csv' in basename:
        print('Google Saved Translations detected')
        lippath = gost_main(filename, dest_lang, src_lang)
        print("Done! Now you can start practicing")
        return 0"""

    assert '.cder' in cder_path, "Wrong CADERA extension"
    reset()
    word_color = choose_color_main(cder_path)
    reset()
    user_lang, learn_lang = choose_lang_main(cder_path, word_color)
    print('user_lang: %s\nlearning_lang: %s' %(user_lang, learn_lang))
    print('Words color: %s' %word_color)
    gota_path = bulkTranslate_main(cder_path, word_color, user_lang, learn_lang)
    assert '.got' in gota_path, "Wrong GOTA extension"

    print('Initializing word bank...')
    lippath = init_lipstick_main(gota_path)
    print("Done! You can start practicing")

    # Call MainAppView() with Practice button, currentBook selector, Progress/word DB view...

if __name__ == "__main__":
    add_new_book_main()
    #learn_lang = Translator().detect(cadera.to_string()).lang

    #book_processor_main(path, dest_lang, src_lang)
