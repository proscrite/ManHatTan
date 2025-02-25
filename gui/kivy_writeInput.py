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
from kivy.clock import Clock

from add_correctButton import CorrectionDialog
from gui.kivy_multipleAnswer import set_question, update_all
from formats.format_text_input import FTextInput, RTLTextInput
from gui.plot_pkmn_panel import *

import threading
import time
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatch
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

from io import BytesIO
from skimage.io import imread
from skimage import color, img_as_ubyte
from skimage.transform import resize

from time import sleep
from bidi.algorithm import get_display


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


def strip_accents(s):
    print('Input string: ', s)
    stripped = ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
    print('Accent-stripped string: ', stripped)
    return stripped

class WriteInput(App):

    def __init__(self, lippath: str, modality: str):
        App.__init__(self)
        self.lippath = lippath
        self.modality = modality

        self.start_time = time.time()
        self.lipstick = self.load_lipstick()
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')

        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
        if self.modality == 'dt': 
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        elif self.modality == 'rt':
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        else:
            print('Error: modality is not "dt" or "rt"')

        self.box = BoxLayout(orientation = 'horizontal') # Used this to nest grid into box
        self.InputPanel = GridLayout(cols= 1, rows=2, size_hint_x=0.8, size_hint_y = 1, padding=20, spacing=20)
        self.optMenu = GridLayout(cols=1, rows=2, size_hint_x=0.2, size_hint_y=0.5, padding=20, spacing=20)
        # self.grid = GridLayout(cols=2, padding=80, spacing=40)
    
    def load_lipstick(self):
        if self.modality == 'rt': self.index = 'word_ll'
        elif self.modality == 'dt': self.index = 'word_ul'

        lipstick = pd.read_csv(self.lippath)
        lipstick.set_index(self.index, inplace=True, drop=False)
        return lipstick

    def load_question(self):

        if self.rtl_flag: 
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)

        else: 
            self.question_displ = self.question
            self.answer_displ = self.answer

        # lb = Label(text='Translate: %s'%self.question_displ, font_size=40, font_name = FONT_HEB, size_hint=(2,1), )
        # self.InputPanel.add_widget(lb)
        
    def load_input(self):
        
        input_callback = partial(self.checkAnswer)
        self.text_input_focus = True
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
        

        self.InputPanel.add_widget(self.input)
        
        enter = Button(text='Enter', on_release=input_callback, size_hint=(0.5,1))
        self.optMenu.add_widget(enter)
   
    def load_options(self):
        self.giveup = Button(text='Exit', on_release=self.exit, size_hint=(0.5,1), font_size=40,
            background_color=(0.6, 0.5, 0.5, 1))
        self.optMenu.add_widget(self.giveup)

    def checkAnswer(self, instance):
        elapsed_time = time.time() - self.start_time
        self.speed = 1/elapsed_time
        
        checkPop = GridLayout(cols=2, padding=10)
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

        else:
            self.input.text_displ = self.input.text
            input_answer = strip_accents(self.input.text.lower())
            self.answer = strip_accents(self.answer.lower())

        if self.answer == input_answer:

            yes = Button(text='Correct! The translation is \n'+self.answer_displ, font_size=40, font_name=FONT_HEB, size_hint=(2,1),
              background_color=(0, 1, 0, 1))
            checkPop.add_widget(yes)
            self.perf = 1

        # elif self.double_check_input(correct_answer, input_answer)[0]:
        #     baseAnsw = self.double_check_input(correct_answer, input_answer)[1]
        #     yes = Button(text='Correct! The baseform translation is \n'+baseAnsw, font_name=FONT_HEB, font_size=40, size_hint=(2,1),
        #       background_color=(0, 1, 0, 1))
        #     checkPop.add_widget(yes)
        #     self.perf = 1

        else:
            no = Button(text=self.input.text+': Incorrect! The translation is \n'+self.answer_displ, font_name=FONT_HEB, font_size=40, size_hint=(2,1),
              background_color=(1, 0, 0, 1))
            checkPop.add_widget(no)
            self.perf = 0

        carryon = Button(text='Continue', on_release=self.on_close, size_hint=(0.5,1), background_color=(1,1,0,1))
        checkPop.add_widget(carryon)

        popChecker = Popup(content=checkPop)
        popChecker.open()
        Window.bind(on_key_down=self._on_keyboard_handler)

    def plot_combat_stats(self, entry_stats, ax = None):
        
        positions = [(0.125, 0.75), (0.25, 0.75), (0.375, 0.75), (0.175, 0.4), (0.325, 0.4)]
        fig = plt.figure(figsize=(12, 4))
        fig.patch.set_facecolor("black")
        gs = GridSpec(3, 4, width_ratios=[0.3, 0.3, 0.3, 0.9], height_ratios=[1, 1, 1])

        colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange']
        
        for i, ((x, y), (k, v) )in enumerate(zip(positions, entry_stats.items()) ):
            ax = fig.add_axes([x - 0.1, y - 0.1, 0.3, 0.3])  # [x, y, width, height]
            ax.pie([v, 10-v], wedgeprops=dict(width=0.5), startangle=270, colors=[colors[i], '0.9'])
            ax.set_xlabel(k, fontsize=16)
            ax.xaxis.label.set_color('yellow')

        health_ax = fig.add_subplot(gs[2, :3])  # Spans the second row, columns 2-3
        health_ax.set_xlim(0, 1)
        # health_ax.set_ylim(0, 1)
        draw_health_bar(entry_stats, health_ax)

        axim = fig.add_subplot(gs[:, 3])         # Spans all rows, last column
        impath = PATH_ANIM+str(self.nid).zfill(3)+'.png'
        self.anim = imread(impath)
        
        img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe+1) , :]        
        self.img_display = axim.imshow(img)  # Store reference to imshow
        axim.set(xlabel=f'Translate: {self.question_displ}',)
        axim.xaxis.label.set_color('yellow')
        axim.xaxis.label.set_fontsize(26)

        return fig
    
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
        update_all(self.lipstick, self.lippath, self.word_ul, 
                   self.perf, self.speed, mode='w'+self.modality)
        App.stop(self)

    def exit(self, instance):
        print("break")
        App.stop(self)

    def build(self):
        self.load_question()

        self.nframe = 0
        self.lipstick.set_index('n_id', inplace=True, drop=False)

        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig = self.plot_combat_stats(entry_stats)
        self.canvas = FigureCanvasKivyAgg(self.fig)

        self.InputPanel.add_widget(self.canvas)
        # self.lipstick.set_index(self.checkEntry, inplace=True, drop=False)

        self.load_input()
        self.load_options()        
        Clock.schedule_interval(self.update, 1 / 30)  # 30 FPS
        self.box.add_widget(self.InputPanel)
        self.box.add_widget(self.optMenu)
        return self.box

    def update(self, dt):
        """Update function for animation"""
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])  # Loop through frames

        new_img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe+1), :]
        self.img_display.set_data(new_img)  # Update image data

        self.canvas.draw()  # Redraw the canvas

if __name__ == "__main__":
    # lipstick_path = sys.argv[1]
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db.lip'
    
    WI = WriteInput(lipstick_path, modality='dt')

    perf = WI.run()
    print(perf)
