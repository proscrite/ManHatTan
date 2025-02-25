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

from kivy.core.window import Window
from bidi.algorithm import get_display

from kivy.clock import Clock

from functools import partial
from time import sleep
from copy import deepcopy
import sys
import apertium
import unicodedata

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH+'/data/fonts/NotoSansHebrew.ttf'

sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
sys.path.append(ROOT_PATH+'/scripts/ML_duolingo')

from update_lipstick import *
from duolingo_hlr import *
from add_correctButton import CorrectionDialog
from kivy_multipleAnswer import set_question, update_all
from formats.format_text_input import FTextInput, RTLTextInput

def strip_accents(s):
    print('Input string: ', s)
    stripped = ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
    print('Accent-stripped string: ', stripped)
    return stripped

class WriteInput(App):

    def __init__(self, lipstick: pd.DataFrame, lippath: str,
      modality: str, word_ll: str, word_ul: str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath
        self.modality = modality
        self.word_ll: str = word_ll
        self.word_ul: str = word_ul
        self.rtl_flag = False
        if self.lipstick.learning_language.iloc[0] == 'iw':
            self.rtl_flag = True

        self.grid = GridLayout(cols=2, padding=80, spacing=40)

    def load_question(self):
        if self.modality == 'dt':
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'

        elif self.modality == 'rt':
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        else:
            print('Error: modality is not "dt" or "rt"')

        if self.rtl_flag: 
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)

        else: 
            self.question_displ = self.question
            self.answer_displ = self.answer

        print(f'self.rtl_flag = {self.rtl_flag}')
        print(f'self.question = {self.question}, self.question_displ = {self.question_displ}')
        lb = Label(text='Translate: %s'%self.question_displ, font_size=40, font_name = FONT_HEB, size_hint=(2,1), )
        self.giveup = Button(text='Exit', on_release=self.exit, size_hint=(0.5,1), font_size=40,
            background_color=(0.6, 0.5, 0.5, 1))
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)

        input_callback = partial(self.checkAnswer)
        self.text_input_focus = False
        #self.input = TextInput(hint_text='Write here', multiline=False,
         # on_text_validate=input_callback, focus=self.text_input_focus, size_hint=(2,1)) # Add hint button?
        
        if self.rtl_flag:
            self.input = RTLTextInput(hint_text='Write here', multiline=False, font_name = FONT_HEB,
                                       on_text_validate=input_callback, font_size=40, background_color=(0.9,0.9,0.9,1),
                                       pos_hint={"center_x": 0.5, "center_y": 0.5}, center_y=0.5, halign="center",)
        else:
            self.input = FTextInput(hint_text='Write here', multiline=False, font_name = FONT_HEB, 
                                    on_text_validate=input_callback, font_size=40, background_color=(0.9,0.9,0.9,1),
                                    pos_hint={"center_x": 0.5, "center_y": 0.5}, center_y=0.5, halign="center",)
        

        enter = Button(text='Enter', on_release=input_callback, size_hint=(0.5,1))
        self.grid.add_widget(self.input)
        self.grid.add_widget(enter)

    def checkAnswer(self, instance):

        print('Checking answer: ', self.input.text)
        checkPop = GridLayout(cols=2, padding=10)
        print(self.question_displ)
        lb2 = Label(text='Translate: %s'%self.question_displ, font_name=FONT_HEB, font_size = 40, size_hint=(2,1), )
        checkPop.add_widget(lb2) # Keep same label as in previous screen
        """TEST:
        if self.modality == 'dt': correction = CorrectionDialog(self.question, self.answer)
        elif self.modality == 'rt': correction = CorrectionDialog(self.answer, self.question)"""
        correction = CorrectionDialog(self.question_displ, self.answer)
        checkPop.add_widget(correction)

        if self.rtl_flag: 
            self.input.text_displ = get_display(self.input.text)
            input_answer = self.input.text_displ
            correct_answer = self.lipstick.loc[self.word_ul, self.checkEntry]
        else:
            self.input.text_displ = self.input.text
            input_answer = strip_accents(self.input.text.lower())
            correct_answer = strip_accents((self.lipstick.loc[self.word_ul, self.checkEntry]).lower() )
        print('self.lipstick.loc[self.word_ul, self.checkEntry] = ', self.lipstick.loc[self.word_ul, self.checkEntry])
        print('equality condition: ', self.lipstick.loc[self.word_ul, self.checkEntry] == self.input.text_displ )
        #self.lipstick.set_index('word_ll', inplace=True, drop=False)


        if correct_answer == input_answer:
            print('Correct answer')
            yes = Button(text='Correct! The translation is \n'+self.answer_displ, font_size=40, font_name=FONT_HEB, size_hint=(2,1),
              background_color=(0, 1, 0, 1))
            checkPop.add_widget(yes)
            self.perf = 1
            print('ENTERED CORRECT ANSWER CONDITION')

        # elif self.double_check_input(correct_answer, input_answer)[0]:
        #     print('Correct answer')
        #     baseAnsw = self.double_check_input(correct_answer, input_answer)[1]
        #     yes = Button(text='Correct! The baseform translation is \n'+baseAnsw, font_name=FONT_HEB, font_size=40, size_hint=(2,1),
        #       background_color=(0, 1, 0, 1))
        #     checkPop.add_widget(yes)
        #     self.perf = 1

        else:
            print('Incorrect answer')
            no = Button(text=self.input.text+': Incorrect! The translation is \n'+self.answer_displ, font_name=FONT_HEB, font_size=40, size_hint=(2,1),
              background_color=(1, 0, 0, 1))
            checkPop.add_widget(no)
            self.perf = 0

        carryon = Button(text='Continue', on_release=self.on_close, size_hint=(0.5,1), background_color=(1,1,0,1))
        checkPop.add_widget(carryon)

        popChecker = Popup(content=checkPop)
        popChecker.open()
        Window.bind(on_key_down=self._on_keyboard_handler)


    ##### Attempt of keyboard_handler #####
    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        if keycode == 40:
            print("Keyboard pressed! {}".format(keycode))
            self.on_close()
        else:
            print("Keyboard pressed! {}".format(keycode))


    def double_check_input(self, answer: str, input_answer: str):
        """"Use apertium to check lexeme root of the answer"""
        # First extract the language of the entry
        if self.checkEntry == 'word_ll':
            lang = self.lipstick.loc[self.word_ul, 'learning_language']
        elif self.checkEntry == 'word_ul':
            lang = self.lipstick.loc[self.word_ul, 'ui_language']

        anInput = apertium.analyze(lang, input_answer)
        baseInput = anInput[0].readings[0][0].baseform
        anAnsw = apertium.analyze(lang, answer)
        baseAnsw = anAnsw[0].readings[0][0].baseform

        if baseAnsw == baseInput:
            return True, baseAnsw
        else:
            return False, None

    def on_close(self, *args):
        print('Mode: ', 'w'+self.modality)
        update_all(self.lipstick, self.lippath, self.word_ul, self.perf, mode='w'+self.modality)
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
