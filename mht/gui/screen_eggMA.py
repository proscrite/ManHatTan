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
import os

from mht.gui.common import *
from mht.gui.add_correctButton import CorrectionDialog
from mht.gui.screen_multipleAnswer import MultipleAnswerScreen
from mht.gui.EachOption import EachOption
from mht.scripts.python_scripts.update_lipstick import update_all

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

class EggScreen(MultipleAnswerScreen):
    def __init__(self, lipstick_path, modality='rt', **kwargs):
        super().__init__(lipstick_path, modality=modality, **kwargs)
        self.is_egg_screen = True
        # Any Egg-specific initialization can go here

    def on_close(self, *_):
        # Dismiss the popup if it exists
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        flag_rebag = update_all(self.lipstick, self.teamlippath, self.word_ul, self.perf, self.speed, mode='m' + self.modality)
        # Egg-specific logic for resetting paths
        print('Egg mode active, resetting lipstick_path: ', self.teamlippath)
        eggpath_dir, eggpath_fname = os.path.split(self.teamlippath)
        list_fname_split = eggpath_fname.split('_')[:-1]
        lippath_fname = '_'.join(list_fname_split) + '.lip'
        self.teamlippath = os.path.join(eggpath_dir.replace('EGGs', 'LIPSTICK'), lippath_fname)
        print('New teamlippath:', self.teamlippath)
        self.app.teamlippath = self.teamlippath
        print('Updating BaseExerciseScreen lippath: ', self.lippath)
        self.lippath = self.teamlippath

        if flag_rebag:
            print('Rebagging team...')
            self.app.init_rebag()
        else:
            current_name = self.name
            self.go_back(current_name)