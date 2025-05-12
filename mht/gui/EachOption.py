import time, threading, sys, unicodedata, pandas as pd, numpy as np

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window


from bidi.algorithm import get_display
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
from update_lipstick import update_all

# --- EachOption class for multiple choice answers ---
class EachOption(Button):
    def __init__(self, text, val, rtl_flag=False):
        super(EachOption, self).__init__(size_hint=(1, 0.8))
        self.app = App.get_running_app()
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        # Add a colored background using canvas instructions
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.color_instruction = Color(0.4, 0.2, 0, 1)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.text = get_display(text) if rtl_flag else text
        self.val = val
        self.font_name = FONT_HEB
        self.font_size = 40
        self.bold = True

    def update_rect(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def update_color(self):
        with self.canvas.before:
            if self.val:
                self.color_instruction.rgba = (0, 1, 0, 0.3)  # green for correct
                self.text = "Correct! " + self.text
                self.perf = 1
            else:
                self.color_instruction.rgba = (1, 0, 0, 0.3)  # red for incorrect
                self.text = "Incorrect! " + self.text
                self.perf = 0
        self.canvas.ask_update()

    def on_release(self, *args):
        if self.app.root.current != "multiple_answer":
            return
        self.disabled = True
        self.update_color()
        self.parent.parent.parent.parent.on_close(self.perf)