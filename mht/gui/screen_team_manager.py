import os
# os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ["KIVY_NO_FILELOG"] = "1"

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import threading
import spacy
import logging
import datetime
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
from kivy.logger import Logger as kvLogger
kvLogger.setLevel(logging.WARNING)
from kivy.config import Config
Config.set("kivy", "log_level", "warning")
logging.getLogger('kivy.network.urlrequest').setLevel(logging.WARNING)
logging.getLogger('kivy.network.httpclient').setLevel(logging.WARNING)

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

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht/'
from mht.gui.common import *
from mht.scripts.python_scripts.bulkTranslate import bulk_translate
from mht.scripts.python_scripts.init_lipstick import set_lip
from mht.scripts.python_scripts.update_lipstick import rebag_team
from mht.gui.screen_eggMA import EggScreen

TEAM_LIP_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db_team.lip'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

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
        self.word_ll = self.team_lip.loc[nid, 'word_ll']
        if self.team_lip.loc[nid, 'learning_language'] == 'iw':
            self.word_ll = get_display(self.word_ll)
        left_button = Button(text=self.word_ll,
                             opacity=1.0,
                             font_name=FONT_HEB,
                             font_size=46,
                             background_color=(1, 1, 1, 0.3),
                             size_hint=(0.6, 1),
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
        qentry = self.team_lip.loc[nid].copy()
        entry_stats = load_pkmn_stats(qentry)

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
    def __init__(self, team_lip, buttons_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        # Read team data and set index for easy access
        self.team_lip = team_lip
        self.team_lip = self.team_lip.set_index('n_id', drop=False)
        self.nids = np.array(self.team_lip.n_id[:6].values)
        self.buttons_active = buttons_active
        self.app = App.get_running_app()

        self.canvas_widgets = []
        self.img_display = []   # Each is a matplotlib image object returned by imshow
        self.anim_list = []     # Each is an animation image (sprite strip)
        self.nframes_list = []  # Current frame indices for each animation

        root_v = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(root_v)
        anchor = AnchorLayout(
            anchor_x='center',
            anchor_y='center'
        )
        root_v.add_widget(anchor)

        # Create a grid for all cells; adjust rows/cols as desired.
        self.main_grid = GridLayout(rows=3, cols=2, size_hint = (0.8, 1.0))
        anchor.add_widget(self.main_grid)
        for nid in self.nids:
            cell = MiniFigureCell(self.team_lip, nid, self, buttons_active)
            self.main_grid.add_widget(cell)
        # Schedule the update loop. You can schedule it here (or in on_start)

        self.back_btn = Button(text="Back to Menu", on_release=self.back_to_menu,
                          size_hint=(1, 0.1))
        root_v.add_widget(self.back_btn)

        if not self.buttons_active:
            # If buttons are not active, replace back button by continue button
            self.remove_widget(self.back_btn)
            continue_button = Button(text="Continue", size_hint=(1, 0.1))
            continue_button.bind(on_release=self.call_rebag_team)
            self.add_widget(continue_button)

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
        print(f'Manager in TeamScreen = {self.manager}')
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

    def call_rebag_team(self, instance):
        self.app.continue_rebag_team()

    def back_to_menu(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "main_menu"

####   Screen for Similar Words loading  ####

class SimilarWordsScreen(Screen):
    def __init__(self, selected_word, lipstick, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.sel_word = selected_word
        self.team_lip = lipstick

        # Root layout: vertical, black background
        self.root_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        with self.root_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        info_label = Label(text="Searching the genealogy tree for eggs...", size_hint=(1, None),
            height=70, color=(1, 1, 1, 1), font_size=40 )
        self.root_layout.add_widget(info_label)

        # Animation container (fills most of the space)
        self.anim_container = BoxLayout( orientation='vertical', size_hint=(1, None),
                                         height=700, padding=0, spacing=0)

        with self.anim_container.canvas.before:
            Color(0, 0, 0, 1)
            self.anim_bg_rect = Rectangle(size=self.anim_container.size, pos=self.anim_container.pos)
        self.anim_container.bind(size=self._update_anim_bg_rect, pos=self._update_anim_bg_rect)
        self.root_layout.add_widget(self.anim_container)

        self.add_widget(self.root_layout)

        # Bottom back button
        back_btn = Button(text="Back to Menu", on_release=self.go_back,
            size_hint=(1, None), height=90, font_size=40, background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1)
        )
        self.root_layout.add_widget(back_btn)

        self.anim = None
        self.im_obj = None
        self.fig = None
        self.fig_canvas = None
        self.nframe = 0

    def on_enter(self, *args):
        self.path_egg = self.get_eggpath()
        self.show_egg_animation()
        if not os.path.exists(self.path_egg):
            print(f'No egg file found for {self.sel_word}. Creating new one...')
            threading.Thread(target=self._make_egg_file_and_continue, daemon=True).start()
        else:
            Clock.schedule_once(lambda dt: self.trigger_new_MA(None), 0.5)

    def on_leave(self, *args):
        Clock.unschedule(self.update_animation)
        if hasattr(self, 'fig_canvas'):
            self.anim_container.remove_widget(self.fig_canvas)

    def show_egg_animation(self):
        """Show the egg animation in the main grid."""
        fig, ax = plt.subplots(figsize=(2.25, 2.25))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.axis('off')
        im_obj, anim = load_pkmn_animation(ax, nframe=0, nid=0)
        self.anim = anim
        self.im_obj = im_obj
        self.fig = fig
        self.fig_canvas = FigureCanvasKivyAgg(fig)
        self.anim_container.clear_widgets()
        self.anim_container.add_widget(self.fig_canvas)
        self.nframe = 0
        Clock.schedule_interval(self.update_animation, 1/12)

    def update_animation(self, dt):
        frame_width = self.anim.shape[0]
        total_frames = self.anim.shape[1] // frame_width
        self.nframe = (self.nframe + 1) % total_frames
        new_img = self.anim[:, frame_width * self.nframe: frame_width * (self.nframe + 1), :]
        self.im_obj.set_data(new_img)
        self.fig_canvas.draw()

    def _make_egg_file_and_continue(self):
        self._make_egg_file()
        Clock.schedule_once(lambda dt: self.trigger_new_MA(None), 0)

    def _make_egg_file(self):
        """Create a new egg file with similar words to the selected word."""
        vec_path = '/Users/pabloherrero/Documents/ManHatTan/mht/data/processed/he_vectors'
        nlp = spacy.load(vec_path)
        new_words = calculate_similar_words(self.sel_word, nlp)
        sample_words = sample(new_words, 10)
        if 'Monster' in sample_words:
            sample_words.remove('Monster')

        print(f'Sample words: {sample_words}')

        gota = pd.DataFrame({
            "word_ll": sample_words,
            "learning_language": self.team_lip.learning_language.values[0],
            "ui_language": self.team_lip.ui_language.values[0],
        })        

        print(f'Before Asyncio Gota: {gota}')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        dicdf = loop.run_until_complete(
            bulk_translate(gota, dest_lang='en')
        )
        loop.close()
        print('After asyncio: ', dicdf)

        today = int(datetime.datetime.timestamp(datetime.datetime.today())) # Correct in init_lipstick.py
        dicdf['creation_time'] = today

        egg = set_lip(dicdf, flag_lexeme=False)
        egg['n_id'] = 0
        print(f'Word_ll in egg: {egg.word_ll}')
        # dicdf['learning_language'] = self.team_lip['learning_language'].values[0]
        # dicdf['ui_language'] = self.team_lip['ui_language'].values[0]
        
        egg.to_csv(self.path_egg, index=False)

    def load_egg(self):
        """Load the egg file and create buttons for each similar word."""
        egg = pd.read_csv(self.path_egg)
        egg = egg.set_index('word_ll', drop=False)

    def trigger_new_MA(self, instance):
        print(f'Manager in similarwords = {self.manager}')
        # if there’s already a SimilarWordsScreen, remove it:
        if self.manager.has_screen('egg_multiple_answer'):
            self.manager.remove_widget(self.manager.get_screen('egg_multiple_answer'))

        # create & add the new screen
        self.manager.add_widget(EggScreen(self.path_egg, modality='rt', name="egg_multiple_answer"))
        
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'egg_multiple_answer'
    
    def go_back(self, *args):
        sm = self.manager
        sm.transition = SlideTransition(direction="right")
        sm.current = "team"

    def _update_bg_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _update_anim_bg_rect(self, *args):
        self.anim_bg_rect.size = self.anim_container.size
        self.anim_bg_rect.pos = self.anim_container.pos
    
    def get_eggpath(self, *args):
        lippath_dir, lippath_fname = os.path.split(self.app.teamlippath)
        append_fname = '_' + self.sel_word[::-1] + '.eggs'
        self.path_egg = os.path.join(lippath_dir.replace('LIPSTICK', 'EGGs'), lippath_fname.replace('.lip', append_fname) )
        return self.path_egg


class MyApp(App):
    def build(self):
        Window.size = (600, 600)
        self.sm = ScreenManager()
        self.teamlippath = TEAM_LIP_PATH
        self.team_lip = load_lipstick(self.teamlippath, modality='dt')
        team_screen = TeamScreen(name='team', team_lip=self.team_lip, buttons_active=False)
        self.sm.add_widget(team_screen)

        return self.sm
    
    def manage_rebag_team(self):
        print('Rebagging team...')
        print(f"Current team: {self.team_lip}")

        new_team = rebag_team(self.team_lip, self.teamlippath)
        if new_team == 0:
            print('Rebagging is not needed yet')
            # self.sm.current = 'main_menu'
        else:
            print(f"New team: {new_team}")
            self.team_lip = new_team
            # Update the screen with the new team
            new_team_screen = TeamScreen(name='team', team_lip=new_team, buttons_active=False)
            self.sm.remove_widget(self.sm.get_screen('team'))
            self.sm.add_widget(new_team_screen)
            self.sm.current = 'team'
            self.sm.transition = SlideTransition(direction="right")
        
if __name__ == '__main__':
    MyApp().run()
