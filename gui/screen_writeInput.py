# --- Write Input Screen (refactored from kivy_writeInput.py) --- #
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from functools import partial
import time

import matplotlib.pyplot as plt
from bidi.algorithm import get_display

# Import common functionality and constants
from common import *
# from update_lipstick import update_all
from add_correctButton import CorrectionDialog

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'


class WriteInputScreen(Screen):
    def __init__(self, lipstick_path, **kwargs):
        super(WriteInputScreen, self).__init__(**kwargs)
        # Set parameters (modality 'dt' as in the original)
        self.lippath = lipstick_path
        self.modality = 'dt'
        self.start_time = time.time()

        # Load lipstick and determine if RTL is needed
        self.lipstick = self.load_lipstick()
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')

        # Pick a question using set_question (imported from kivy_multipleAnswer)
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
        if self.modality == 'dt': 
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        else:  # for modality 'rt'
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        # Create layout containers
        self.box = BoxLayout(orientation='horizontal')
        self.InputPanel = GridLayout(cols=1, rows=2, size_hint=(0.8, 1), padding=20, spacing=20)
        self.optMenu = GridLayout(cols=1, rows=3, size_hint=(0.2, 0.5), padding=20, spacing=20)


        # Prepare question display text (handle RTL if needed)
        self.load_question()
        # Add the animated panel
        self.nframe = 0
        self.lipstick.set_index('n_id', inplace=True, drop=False)
        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig = self.plot_combat_stats(entry_stats)
        self.fig_canvas = FigureCanvasKivyAgg(self.fig)
        self.InputPanel.add_widget(self.fig_canvas)

        # Create text input and Enter button
        self.load_input()
        # Create an Exit/back button
        self.load_options()

        self.box.add_widget(self.InputPanel)
        self.box.add_widget(self.optMenu)
        self.add_widget(self.box)

        # Schedule animation update (30 FPS)
        Clock.schedule_interval(self.update, 1/30)
        
        # Optionally, add a “Back to Menu” button if not already in optMenu
        back_button = Button(text="Back to Menu", size_hint=(0.5, 1))
        back_button.bind(on_release=self.go_back)
        self.optMenu.add_widget(back_button)

    def load_lipstick(self):
        index = 'word_ul' if self.modality == 'dt' else 'word_ll'
        lipstick = pd.read_csv(self.lippath)
        lipstick.set_index(index, inplace=True, drop=False)
        return lipstick

    def load_question(self):
        if self.rtl_flag:
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)
        else:
            self.question_displ = self.question
            self.answer_displ = self.answer

    def load_input(self):
        from kivy.uix.textinput import TextInput
        from functools import partial
        input_callback = partial(self.checkAnswer)
        self.text_input_focus = True
        # For simplicity, using a standard TextInput here.
        self.input = TextInput(
            hint_text='Write here', 
            multiline=False, 
            on_text_validate=input_callback, 
            font_size=40,
            size_hint=(2, 1)
        )
        self.InputPanel.add_widget(self.input)
        enter = Button(text='Enter', on_release=input_callback, size_hint=(0.5, 1))
        self.optMenu.add_widget(enter)

    def load_options(self):
        exit_btn = Button(text='Exit', on_release=self.go_back, size_hint=(0.5, 1), font_size=40,
                          background_color=(0.6, 0.5, 0.5, 1))
        self.optMenu.add_widget(exit_btn)

    def strip_accents(self, s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    def checkAnswer(self, instance):
        elapsed_time = time.time() - self.start_time
        self.speed = 1 / elapsed_time

        checkPop = GridLayout(cols=2, padding=10)
        lb2 = Label(text='Translate: %s' % self.question_displ, font_size=40, size_hint=(2, 1))
        checkPop.add_widget(lb2)
        # Create a CorrectionDialog (from add_correctButton)
        correction = CorrectionDialog(self.question_displ, self.answer)
        checkPop.add_widget(correction)

        if self.rtl_flag:
            input_answer = get_display(self.input.text)
        else:
            input_answer = self.strip_accents(self.input.text.lower())
            self.answer = self.strip_accents(self.answer.lower())

        if self.answer == input_answer:
            yes = Button(text='Correct! The translation is \n' + self.answer_displ,
                         font_size=40, size_hint=(2, 1), background_color=(0, 1, 0, 1))
            checkPop.add_widget(yes)
            self.perf = 1
        else:
            no = Button(text=self.input.text + ': Incorrect! The translation is \n' + self.answer_displ,
                        font_size=40, size_hint=(2, 1), background_color=(1, 0, 0, 1))
            checkPop.add_widget(no)
            self.perf = 0

        carryon = Button(text='Continue', on_release=self.on_close, size_hint=(0.5, 1), background_color=(1, 1, 0, 1))
        checkPop.add_widget(carryon)
        popChecker = Popup(content=checkPop)
        popChecker.open()

    def on_close(self, *args):
        # Update performance; here we call update_all (from update_lipstick)
        update_all(self.lipstick, self.lippath, self.word_ul, self.perf, self.speed, mode='w' + self.modality)
        # Optionally, navigate back to the main menu instead of closing the entire app:
        self.go_back(None)

    def plot_combat_stats(self, entry_stats):
        positions = [(0.125, 0.75), (0.25, 0.75), (0.375, 0.75), (0.175, 0.4), (0.325, 0.4)]
        fig = plt.figure(figsize=(12, 4))
        fig.patch.set_facecolor("black")
        gs = GridSpec(3, 4, width_ratios=[0.3, 0.3, 0.3, 0.9], height_ratios=[1, 1, 1])
        colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange']

        for (x, y), (k, v) in zip(positions, entry_stats.items()):
            ax = fig.add_axes([x - 0.1, y - 0.1, 0.3, 0.3])
            ax.pie([v, 10 - v], wedgeprops=dict(width=0.5), startangle=270, colors=[colors.pop(0), '0.9'])
            ax.set_xlabel(k, fontsize=16)
            ax.xaxis.label.set_color('yellow')

        health_ax = fig.add_subplot(gs[2, :3])
        health_ax.set_xlim(0, 1)
        draw_health_bar(entry_stats, health_ax)

        axim = fig.add_subplot(gs[:, 3])
        # Load animated image
        from skimage.io import imread
        impath = PATH_ANIM + str(self.nid).zfill(3) + '.png'
        self.anim = imread(impath)
        img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe + 1), :]
        self.img_display = axim.imshow(img)
        axim.set(xlabel=f'Translate: {self.question_displ}')
        axim.xaxis.label.set_color('yellow')
        axim.xaxis.label.set_fontsize(26)
        return fig

    def update(self, dt):
        # Update animation frame (assumes self.anim is a sprite sheet)
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        new_img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe + 1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()

    def go_back(self, instance):
        self.manager.current = "main_menu"
        
