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


import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
from kivy.logger import Logger as kvLogger
kvLogger.setLevel(logging.WARNING)
from kivy.config import Config
Config.set("kivy", "log_level", "warning")

from bidi.algorithm import get_display

import sys
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

# Use only one backend!
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
# matplotlib.use("Agg")
from skimage.io import imread

import numpy as np
import pandas as pd

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH + '/scripts/python_scripts/')
from common import *
# from plot_pkmn_panel import *  # Provides load_pkmn_stats and draw_rounded_bar

PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

class MiniFigureCell(BoxLayout):
    def __init__(self, team_lip, nid, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.team_lip = team_lip
        self.app = App.get_running_app()

        # Build the figure; store the figure in this cell
        self.fig = self.plot_team(nid=nid)

        # Create canvas widget for this figure
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        # Append this canvas and related objects to the app's lists so they can be updated
        self.app.canvas_widgets.append(self.canvas_widget)

        # Left button (with Hebrew support if needed)
        word_ll = self.team_lip.loc[nid, 'word_ll']
        if self.team_lip.loc[nid, 'learning_language'] == 'iw':
            word_ll = get_display(word_ll)
        left_button = Button(text=word_ll,
                             opacity=1.0,
                             font_name=FONT_HEB,
                             font_size=46,
                             background_color=(1, 1, 1, 0.3),
                             size_hint=(0.4, 1))
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
        self.app.anim_list.append(anim)
        
        # Use only the first frame for initialization
        # (Here we assume that the sprite is a strip with square frames)
        first_frame = anim[:, :anim.shape[0], :]
        # imshow returns the image object we later update
        im_obj = ax_main.imshow(first_frame, aspect="auto")
        self.app.img_display.append(im_obj)
        # Initialize frame counter for this cell
        self.app.nframes_list.append(0)

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

class MyApp(App):
    def __init__(self, lip_path, **kwargs):
        super().__init__(**kwargs)
        # Read team data and set index for easy access
        self.team_lip = pd.read_csv(lip_path)
        self.team_lip = self.team_lip.set_index('n_id', drop=False)
        self.nids = np.array(self.team_lip.n_id[:6].values)

        # Prepare lists to store update-critical objects from each MiniFigureCell:
        self.canvas_widgets = []
        self.img_display = []   # Each is a matplotlib image object returned by imshow
        self.anim_list = []     # Each is an animation image (sprite strip)
        self.nframes_list = []  # Current frame indices for each animation

    def build(self):
        # Create a grid for all cells; adjust rows/cols as desired.
        main_grid = GridLayout(rows=3, cols=2)
        for nid in self.nids:
            cell = MiniFigureCell(self.team_lip, nid)
            main_grid.add_widget(cell)
        # Schedule the update loop. You can schedule it here (or in on_start)
        Clock.schedule_interval(self.update, 1 / 30)
        return main_grid

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

            # Optionally, update any other elements here

            # Force redraw of each cell's canvas widget:
            self.canvas_widgets[i].draw()

if __name__ == '__main__':
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db_team.lip'
    MyApp(lipstick_path).run()
