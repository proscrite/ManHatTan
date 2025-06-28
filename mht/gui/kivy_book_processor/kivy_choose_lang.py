
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

import datetime
import numpy as np
import pandas as pd
from googletrans import Translator
from kivy_choose_word_color import DfguiWidget

class LangButton(Button):

    def __init__(self, ulang, **kwargs):
        self.text : str = ulang[0]
        self.ulang_short: str = ulang[1]
        #self. : str = path
        self.app = App.get_running_app()
        super(LangButton, self).__init__(**kwargs)

    def on_release(self, *args):
        self.disable = True
        self.background_color = (0, 1, 0, 1)
        self.app.set_ulang(self.ulang_short)

class chooseLangs(App):
    def __init__(self, cder_path: str, word_color: str, **kwargs):
        super(chooseLangs, self).__init__(**kwargs)
        App.__init__(self)
        self.learn_lang: str
        self.user_lang: str
        self.word_color = word_color
        self.cder_path = cder_path

    def select_cadera_entries(self):
        words_ll = pd.read_csv(self.cder_path, index_col=0, nrows=10)[self.word_color]
        words_header = self.word_color + ' entries'
        self.cadera = pd.DataFrame({words_header : words_ll})
        self.learn_lang = Translator().detect(words_ll.to_string()).lang
        self.cadera['Detected language'] = self.learn_lang

    def set_ulang(self, ulang):
        self.user_lang = ulang
        App.stop(self)

    def set_word_col(self, *args):
        pass

    def build(self):
        mainGrid = GridLayout(cols=2)
        boxDf = BoxLayout(orientation='vertical')
        boxDf.add_widget(DfguiWidget(self.cadera))
        mainGrid.add_widget(boxDf)

        langGrid = GridLayout(cols=1)
        langGrid.add_widget(Label(text='Select user language:'))
        ulangs = {'Spanish' : 'es', 'English': 'en', 'French': 'fr'}

        for la in ulangs.items():
            op = LangButton(la)
            #op = Button(text=la, on_release=self.set_ulang(la))
            langGrid.add_widget(op)
        mainGrid.add_widget(langGrid)

        return mainGrid


    def run(self):
        super().run()
        return self.user_lang, self.learn_lang

def choose_lang_main(cder_path, word_color):
    CLang = chooseLangs(cder_path, word_color)
    CLang.select_cadera_entries()

    user_lang = CLang.run()
    print('Selected user language: ', user_lang)
    return user_lang

if __name__ == '__main__':

  cder_path = '~/Documents/ManHatTan/CADERAs/Il castello dei destini incrociati - Notizbuch.cder'
  word_color = 'blue'
  CLang = chooseLangs(cder_path, word_color)
  CLang.select_cadera_entries()

  user_lang = CLang.run()
  print('Selected user language: ', user_lang)
