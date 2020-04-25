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

from functools import partial
from time import sleep
from copy import deepcopy
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import *
from add_correctButton import CorrectionDialog

class WriteInput(App):

    def __init__(self, lipstick: pd.DataFrame, lippath: str,
      modality: str, word_ll: str, word_ul: str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath
        self.modality = modality
        self.word_ll: str = word_ll
        self.word_ul: str = word_ul
        self.grid = GridLayout(cols=2)

    def load_question(self):
        if self.modality == 'dt':
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'

        elif self.modality == 'rt':
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        else:
            print('Error: modality is not "dt" or "rt"')

        lb = Label(text='Translate: %s'%self.question, size_hint=(2,1), )
        self.giveup = Button(text='Exit', on_release=self.exit, size_hint=(0.5,1),
            background_color=(0.6, 0.5, 0.5, 1))
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)

        self.input = TextInput(hint_text='Write here', size_hint=(2,1)) # Add hint button?

        input_callback = partial(self.checkAnswer)

        enter = Button(text='Enter', on_release=input_callback, size_hint=(0.5,1))
        self.grid.add_widget(self.input)
        self.grid.add_widget(enter)

    def checkAnswer(self, instance):
        print('Checking answer: ', self.input.text)
        checkPop = GridLayout(cols=2, padding=10)
        lb2 = Label(text='Translate: %s'%self.question, size_hint=(2,1), )
        checkPop.add_widget(lb2) # Keep same label as in previous screen
        correction = CorrectionDialog(self.question, self.answer)
        checkPop.add_widget(correction)

        print('self.checkEntry: ', self.checkEntry)
        print('self.lipstick.loc[self.word_ul, self.checkEntry] = ', self.lipstick.loc[self.word_ul, self.checkEntry])
        print('equality condition: ', self.lipstick.loc[self.word_ul, self.checkEntry] == self.input.text )
        #self.lipstick.set_index('word_ll', inplace=True, drop=False)
        if self.lipstick.loc[self.word_ul, self.checkEntry] == self.input.text:
            print('Correct answer')
            yes = Button(text='Correct! The translation is \n'+self.answer, size_hint=(2,1),
              background_color=(0, 1, 0, 1))
            checkPop.add_widget(yes)
            self.perf = 1
        else:
            print('Incorrect answer')
            no = Button(text=self.input.text+': Incorrect! The translation is \n'+self.answer, size_hint=(2,1),
              background_color=(1, 0, 0, 1))
            checkPop.add_widget(no)
            self.perf = 0

        carryon = Button(text='Continue', on_release=self.on_close, size_hint=(0.5,1), background_color=(1,1,0,1))
        checkPop.add_widget(carryon)

        popChecker = Popup(content=checkPop)
        popChecker.open()

    def on_close(self, *args):
        update_all(self.lipstick, self.lippath, self.word_ul, self.perf)
        App.stop(self)

    def exit(self, instance):
        print("break")
        App.stop(self)

    def build(self):
        return self.grid

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    word_ll, word_ul, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    WI = WriteInput(lipstick, lipstick_path,
      word_ll=word_ll, word_ul=word_ul, modality='dt')
    WI.load_question()
    #WI.load_options(qu, answ)  # Only exit button, correctionDialog after checking
    #WI.load_answers(shufOpts)

    perf = WI.run()
    print(perf)
