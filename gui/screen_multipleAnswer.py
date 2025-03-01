# --- Multiple Answer Screen (refactored from kivy_multipleAnswer.py) --- #
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
import time, threading

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from skimage.io import imread
from bidi.algorithm import get_display

from common import *
# from update_lipstick import update_all
from add_correctButton import CorrectionDialog

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

from EachOption import EachOption

class MultipleAnswerScreen(Screen):
    def __init__(self, lipstick_path, **kwargs):
        super(MultipleAnswerScreen, self).__init__(**kwargs)
        # Set parameters (modality 'rt' as in the original)
        self.lippath = lipstick_path
        self.modality = 'rt'
        self.start_time = time.time()

        self.lipstick = self.load_lipstick()
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')

        # Set the lipstick on the running app so CorrectionDialog can access it.
        app = App.get_running_app()
        app.lipstick = self.lipstick
        app.lippath = self.lippath

        # Pick a question
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
        if self.modality == 'dt':
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        else:
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        self.box = BoxLayout(orientation='vertical')
        self.upper_panel = GridLayout(cols=3, size_hint_y=0.8)

        # Create the options panel (using rnd_options and shuffle_dic)
        self.optMenu = GridLayout(cols=1, rows=2, size_hint_x=0.25, padding=20, spacing=20)
        exit_btn = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        exit_btn.bind(on_release=self.go_back)
        self.optMenu.add_widget(exit_btn)
        # Add a CorrectionDialog (for demonstration)
        correction = CorrectionDialog(self.answer, self.question)
        self.optMenu.add_widget(correction)
        self.upper_panel.add_widget(self.optMenu)

        # Create answer buttons
        options = rnd_options(self.lippath, iquest=self.iqu, modality=self.modality)
        options[self.answer] = True  # include correct answer
        shufOpts = shuffle_dic(options)
        self.load_answers(shufOpts)

        # Add animated combat stats panel
        self.nframe = 0
        self.lipstick.set_index('n_id', inplace=True, drop=False)
        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig = self.plot_combat_stats(entry_stats)
        self.fig_canvas = FigureCanvasKivyAgg(self.fig)
        self.upper_panel.add_widget(self.fig_canvas)

        self.box.add_widget(self.upper_panel)
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.1))
        back_btn.bind(on_release=self.go_back)
        self.box.add_widget(back_btn)
        self.add_widget(self.box)

        Clock.schedule_interval(self.update, 1/30)
        Window.bind(on_key_down=self._on_keyboard_handler)

    def load_lipstick(self):
        index = 'word_ll' if self.modality == 'rt' else 'word_ul'
        lipstick = pd.read_csv(self.lippath)
        lipstick.set_index(index, inplace=True, drop=False)
        return lipstick

    def load_answers(self, answers: dict):
        self.listOp = []
        self.AnswerPanel = GridLayout(cols=2, rows=2, padding=40, spacing=20)
        hints = ['A', 'B', 'C', 'D']
        for h, ans_text in zip(hints, answers):
            answer_button_layout = BoxLayout(orientation='vertical')
            hint_label = Label(text=h, size_hint=(0.2, 0.2))
            answer_button_layout.add_widget(hint_label)
            op = EachOption(ans_text, answers[ans_text], self.rtl_flag)
            answer_button_layout.add_widget(op)
            self.listOp.append(op)
            self.AnswerPanel.add_widget(answer_button_layout)
        self.box.add_widget(self.AnswerPanel)

    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        # Map keycodes to option buttons (adjust keycodes as needed)
        if keycode in range(30, 33):
            self.listOp[keycode - 30].on_release()
        elif keycode == 4:
            self.listOp[0].on_release()
        elif keycode == 5:
            self.listOp[1].on_release()
        elif keycode == 6:
            self.listOp[2].on_release()
        elif keycode == 7:
            self.listOp[3].on_release()

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
        from skimage.io import imread
        impath = PATH_ANIM + str(self.nid).zfill(3) + '.png'
        self.anim = imread(impath)
        img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe + 1), :]
        self.img_display = axim.imshow(img)
        axim.set(xlabel=f'Translate: {self.question}')
        axim.xaxis.label.set_color('yellow')
        axim.xaxis.label.set_fontsize(26)
        return fig

    def update(self, dt):
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        new_img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe + 1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()

    def go_back(self, instance):
        self.manager.current = "main_menu"
