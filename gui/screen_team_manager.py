import os
# os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ["KIVY_NO_FILELOG"] = "1"

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import spacy
import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
from kivy.logger import Logger as kvLogger
kvLogger.setLevel(logging.WARNING)
from kivy.config import Config
Config.set("kivy", "log_level", "warning")

from bidi.algorithm import get_display

from random import sample
import sys
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

# Use only one backend!
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
# matplotlib.use("Agg")
from skimage.io import imread
import asyncio
from googletrans import Translator
from googletrans import LANGUAGES
import numpy as np
import pandas as pd

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH + '/scripts/python_scripts/')
sys.path.append(ROOT_PATH + '/gui/')

# from ..scripts.python_scripts.bulkTranslate import bulk_translate
# from gui.screen_multipleAnswer import MultipleAnswerScreen

from common import *
# from plot_pkmn_panel import *  # Provides load_pkmn_stats and draw_rounded_bar

PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

class MiniFigureCell(BoxLayout):
    def __init__(self, team_lip, nid, screen_ref, button_active = True, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.team_lip = team_lip
        self.screen_ref = screen_ref
        self.button_active = button_active
        # Build the figure; store the figure in this cell
        self.fig = self.plot_team(nid=nid)

        # Create canvas widget for this figure
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        # Append this canvas and related objects to the app's lists so they can be updated
        self.screen_ref.canvas_widgets.append(self.canvas_widget)

        # Left button (with Hebrew support if needed)
        word_ll = self.team_lip.loc[nid, 'word_ll']
        if self.team_lip.loc[nid, 'learning_language'] == 'iw':
            word_ll = get_display(word_ll)
        left_button = Button(text=word_ll,
                             opacity=1.0,
                             font_name=FONT_HEB,
                             font_size=46,
                             background_color=(1, 1, 1, 0.3),
                             size_hint=(0.4, 1),
                             disabled = not self.button_active)
        left_button.bind(on_release=self.screen_ref.trigger_similar_words)
        self.add_widget(left_button)
        self.add_widget(self.canvas_widget)

    def plot_team(self, nid):
        """ Plot the team of Pokémon using the provided LIP data."""
        fig = plt.figure(figsize=(2, 3))
        fig.patch.set_facecolor("black")
        gs = GridSpec(4, 2,
                      width_ratios=[1, 1],
                      height_ratios=[4, 0.1, 1, 0.15],
                      top=0.95, bottom=0.05, hspace=0.6)

        # Get the stats using your helper function
        entry_stats = load_pkmn_stats(self.team_lip, nid)

        # Main axes for the animation (first two rows)
        ax_main = fig.add_subplot(gs[:2, :])
        ax_main.set_facecolor('black')
        
        # Load the animation sprite
        impath = PATH_ANIM + str(nid).zfill(3) + '.png'
        anim = imread(impath)
        # Append the animation to the app's list
        self.screen_ref.anim_list.append(anim)
        
        # Use only the first frame for initialization
        # (Here we assume that the sprite is a strip with square frames)
        first_frame = anim[:, :anim.shape[0], :]
        # imshow returns the image object we later update
        im_obj = ax_main.imshow(first_frame, aspect="auto")
        self.screen_ref.img_display.append(im_obj)
        # Initialize frame counter for this cell
        self.screen_ref.nframes_list.append(0)

        # Create additional axes for a health bar, etc.
        axbar = fig.add_subplot(gs[2, :3])
        axbar.set_facecolor("black")
        hp = entry_stats['hp']
        level = entry_stats['level']
        draw_rounded_bar(axbar, width=0.8, color='lightgray',
                         y_offset=0.2, bar_height=0.3)
        draw_rounded_bar(axbar, width=hp * 0.8, color='green',
                         y_offset=0.2, bar_height=0.3)
        axbar.text(0.5, 0.8, f'Level: {level}/100', size=16,
                   ha='center', color='yellow', transform=axbar.transAxes)
        axbar.text(0.5, -0.5, f'HP = {int(hp * 100)}/100', size=16,
                   ha='center', color='yellow', transform=axbar.transAxes)
        axbar.set_xlim(0, 1)
        axbar.set_ylim(0, 1)
        axbar.axis("off")
        return fig


# class MyApp(App):
class TeamScreen(Screen):
    def __init__(self, lip_path, buttons_active: bool = False, **kwargs):
        super().__init__(**kwargs)
        # Read team data and set index for easy access
        self.team_lip = pd.read_csv(lip_path)
        self.team_lip = self.team_lip.set_index('n_id', drop=False)
        self.nids = np.array(self.team_lip.n_id[:6].values)
        self.buttons_active = buttons_active

        self.canvas_widgets = []
        self.img_display = []   # Each is a matplotlib image object returned by imshow
        self.anim_list = []     # Each is an animation image (sprite strip)
        self.nframes_list = []  # Current frame indices for each animation

        # Create a grid for all cells; adjust rows/cols as desired.
        self.main_grid = GridLayout(rows=3, cols=2)
        self.add_widget(self.main_grid)
        for nid in self.nids:
            cell = MiniFigureCell(self.team_lip, nid, self, buttons_active)
            self.main_grid.add_widget(cell)
        # Schedule the update loop. You can schedule it here (or in on_start)
    # def on_enter(): 
        Clock.schedule_interval(self.update, 1 / 30)

    def update(self, dt):
        # Update the animation frames for each cell.
        # Loop over each cell's stored image and animation references.
        for i in range(len(self.nids)):
            # Ensure that indices exist in all our lists
            if i >= len(self.img_display) or i >= len(self.anim_list):
                continue

            anim = self.anim_list[i]
            frame_height = anim.shape[0]
            # Calculate how many frames there are assuming frames are arranged horizontally:
            total_frames = anim.shape[1] // frame_height

            self.nframes_list[i] = (self.nframes_list[i] + 1) % total_frames

            # Determine the slice for the new frame:
            start = frame_height * self.nframes_list[i]
            end = frame_height * (self.nframes_list[i] + 1)
            new_img = anim[:, start:end, :]

            # Update the image object of the corresponding cell:
            self.img_display[i].set_data(new_img)

            # Force redraw of each cell's canvas widget:
            self.canvas_widgets[i].draw()
    
    def trigger_similar_words(self, instance):
    
        # if there’s already a SimilarWordsScreen, remove it:
        if self.manager.has_screen('similar_words'):
            self.manager.remove_widget(self.manager.get_screen('similar_words'))

        # create & add the new screen
        sws = SimilarWordsScreen(
            name= 'similar_words',
            selected_word = instance.text,  
            lipstick= self.team_lip
        )
        self.manager.add_widget(sws)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'similar_words'



class SimilarWordsScreen(Screen):
    def __init__(self, selected_word, lipstick, **kwargs):
        super().__init__(**kwargs)
        self.sel_word = selected_word
        self.team_lip = lipstick
        self.main_grid = GridLayout(cols=1, size_hint = (1, 1))
        self.button_grid = GridLayout(cols = 2, size_hint = (1, 2))

        vec_path = '/Users/pabloherrero/Documents/ManHatTan/notebooks/he_vectors'
        self.nlp = spacy.load(vec_path)
        self._init_similar_words()

        back_btn = Button(text="Back to Menu", on_release=self.go_back,
                          size_hint=(0.5, 1))
        self.main_grid.add_widget(self.button_grid)
        self.main_grid.add_widget(back_btn)

        self.add_widget(self.main_grid)
    
    def _init_similar_words(self):
        new_words = calculate_similar_words(self.sel_word, self.nlp)
        sample_words = sample(new_words, 4)
        source_series = pd.Series(sample_words)
        dest_series = bulk_translate(source_series, dest_lang = self.team_lip.ui_language)
        
        for w in new_words:
            label = Button(text = w, font_name=FONT_HEB, font_size=40,)
                          
            self.button_grid.add_widget(label)

    def go_back(self, *args):
        sm = self.manager
        sm.transition = SlideTransition(direction="right")
        sm.current = "team"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        team_screen = TeamScreen(name='team', lip_path='/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db_team.lip')
        sm.add_widget(team_screen)

        return sm
if __name__ == '__main__':
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db_team.lip'
    MyApp().run()
