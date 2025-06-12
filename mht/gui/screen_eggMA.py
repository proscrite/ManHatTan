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
from mht.scripts.python_scripts import egg_processing as egg_proc

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

class EggScreen(MultipleAnswerScreen):
    def __init__(self, lipstick_path, modality='rt', **kwargs):
        super().__init__(lipstick_path, modality=modality, **kwargs)
        self.is_egg_screen = True
        print('Initializing EggScreen with lipstick path:', lipstick_path)
        # Any Egg-specific initialization can go here

    def _get_liptick_path(self):
        eggpath_dir, eggpath_fname = os.path.split(self.teamlippath)
        list_fname_split = eggpath_fname.split('_')[:-1]
        lippath_fname = '_'.join(list_fname_split) + '.lip'
        lippath = os.path.join(eggpath_dir.replace('EGGs', 'LIPSTICK'), lippath_fname)
        return lippath
    
    def _reset_lipstick_path(self, team_lippath):
        """Reset the lipstick path to the team lipstick path."""
        print('New teamlippath:', team_lippath)
        self.app.teamlippath = team_lippath
        print('Updating BaseExerciseScreen lippath: ', self.lippath)
        self.lippath = team_lippath

    def _check_egg_hatch(self):
        """Check if the egg has hatched and add it to main lipstick accordingly."""
        self.lipstick = self.lipstick.set_index('word_ul', drop=False)
        rebag = self.lipstick.loc[self.word_ul, 'rebag']

        if rebag:
            print('Egg hatched! Adding to main lipstick')
            self._hatch_egg(self.word_ul, self.answer, self.lipstick, self.lippath, self.modality)

        else:
            print('Egg not hatched yet')
            return

    def _hatch_egg(self, word_ul, answer, lipstick, lipstick_path, modality):
        """Add the entry from the egg to the main lipstick."""
        egg_path = lipstick_path
        team_lippath = self._get_liptick_path()
        lippath = team_lippath.replace('_team.lip', '.lip')
        actual_lipstick = pd.read_csv(lippath)
        random_nid = egg_proc.get_random_nid(actual_lipstick)
        egg_entry = egg_proc.init_hatched_egg(lipstick, word_ul, random_nid, flag_lexeme=True)
        
        new_lipstick = egg_proc.add_egg_to_lipstick(egg_entry, actual_lipstick)
        if new_lipstick is not None:
            print('New lipstick after hatching:', new_lipstick)
            new_lipstick.to_csv(lippath, index=False)
            print(f'New lipstick saved to {lippath}')
        else:
            print('No new lipstick entry created.')

    def on_close(self, *_):
        # Dismiss the popup if it exists
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        _ = update_all(self.lipstick, self.teamlippath, self.word_ul, self.perf, self.speed, mode='m' + self.modality)
        
        # Check whether the egg hatches:
        self._check_egg_hatch()

        # Egg-specific logic for resetting paths
        print('Egg mode active, resetting lipstick_path: ', self.teamlippath)
        team_lippath = self._get_liptick_path()
        self._reset_lipstick_path(team_lippath)

        current_name = self.name
        self.go_back(current_name)