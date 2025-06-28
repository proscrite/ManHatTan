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

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht/'
from mht.gui.common import *
from mht.gui.plot_pkmn_panel import load_pkmn_stats, draw_rounded_bar, draw_health_bar

PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/mht/gui/Graphics/Battlers/'


class ShowTeamScreen(Screen):
    def __init__(self, name: str, team_lip, end_flag: bool = False, **kwargs):
        super().__init__(name=name, **kwargs)
        self.team_lip = team_lip

         # These lists will be filled by plot_team
        self.img_display = []
        self.anim_list = []
        self.nframes_list = []

        self.nids = np.array(self.team_lip.n_id[:6].values)
        print(self.nids)
        self.fig = self.plot_team(lipstick=self.team_lip, nids=self.nids)

        # Create a BoxLayout to hold the Matplotlib figure
        # self.box = BoxLayout(orientation="vertical", spacing = 10, padding = 10)
        self.box = FloatLayout()
        self.buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), pos_hint={'top': 1})

        # Optionally add a header or control buttons
        header = BoxLayout(size_hint=(1, 0.1))
        header.add_widget(Label(text="Current Team:", color=(1, 1, 1, 1)))
        back_btn = Button(text="Back", size_hint=(0.2, 1))

        # if end_flag:
        #     function_button = App.get_running_app().finish_and_write
        # else:
        #     function_button = App.get_running_app().show_new_team

        back_btn.bind(on_release=self.go_back)        
        header.add_widget(back_btn)
        self.box.add_widget(header)

        # Embed the Matplotlib figure using FigureCanvasKivyAgg
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        self.canvas_widget.size_hint_x = 0.5
        self.canvas_widget.bind(width=lambda instance, width: setattr(instance, 'height', width * 0.4))
        anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint_y=1)
        
        anchor.add_widget(self.canvas_widget)
        self.box.add_widget(anchor)
        self.get_name_buttons(self.team_lip, self.nids, self.box)
        
        self.add_widget(self.box)

    def get_name_buttons(self, lipstick, nids, box):
        buttons_grid = GridLayout(cols=2, size_hint_y=1, spacing = [0.1, 0.1])

        for i, nid in enumerate(nids):
            word_ll = lipstick.loc[nid, 'word_ul']
            # if lipstick.loc[nid, 'learning_language'] == 'iw':
            #     word_ll = get_display(word_ll)
            print(word_ll)
            button_name = Button(text=word_ll,
                                 size_hint=(0.1, 0.05), font_name = FONT_HEB, font_size = 46, 
                                 pos_hint={'x': i/6.0, 'y': i/12.0},
                                 background_color=(0.1, 1., 0.1, 1),
                                 opacity=0.2
            )
            button_name.bind(on_release=self.go_back)
            # buttons_grid.add_widget(button_name)
        box.add_widget(buttons_grid)
        

    def plot_team(self, lipstick, nids):
        self.fig = plt.figure(figsize=(3, 20))
        self.fig.patch.set_facecolor("black")
        gs = GridSpec(6, 2, width_ratios=[1, 1],
                        height_ratios=[0.8, 0.15, 0.8, 0.15, 0.8, 0.15], top = 0.95, bottom = 0.05, hspace=0.6)
        print('Nids in plot_team:', nids)

        for i, nid in enumerate(nids):
            j, k = i // 2, i % 2
            print(f"Processing nid {nid} at position ({j}, {k})")

            entry_stats = load_pkmn_stats(lipstick, nid)
            word_ll = lipstick.loc[nid, 'word_ll']
            if lipstick.loc[nid, 'learning_language'] == 'iw':
                word_ll = get_display(word_ll)

            ax = self.fig.add_subplot(gs[2 * j, k])
            impath = PATH_ANIM + str(nid).zfill(3) + '.png'
            print('Image path:', impath)
            anim = imread(impath)
            self.anim_list.append(anim)
            # Use only the first frame for initialization
            first_frame = anim[:, :anim.shape[0], :]
            im_obj = ax.imshow(first_frame, aspect="auto")
            self.img_display.append(im_obj)
            self.nframes_list.append(0)
            # ax.set(title=word_ll)
            ax.title.set_color('yellow')
            ax.title.set_fontsize(26)

            # Create a bar chart below the image
            hp = entry_stats['hp']
            level = entry_stats['level']
            axbar = self.fig.add_subplot(gs[2 * j + 1, k])
            axbar.set_facecolor("black")
            draw_rounded_bar(axbar, width=0.8, color='lightgray',
                                y_offset=0.2, bar_height=0.3)
            draw_rounded_bar(axbar, width=hp * 0.8, color='green',
                                y_offset=0.2, bar_height=0.3)
            axbar.text(0.5, -0.3, f'Level: {level}/100', size=16,
                        ha='center', color='yellow', transform=ax.transAxes)
            axbar.text(0.5, -0.6, f'HP = {int(hp * 100)}/100', size=16,
                        ha='center', color='yellow', transform=ax.transAxes)
            axbar.set_xlim(0, 1)
            axbar.set_ylim(0, 1)
            axbar.axis("off")
        # self.fig.tight_layout(w_pad=0.1,)
        return self.fig

    def update(self, dt):
        """Update the animation frames."""
        for i, nid in enumerate(self.nids):
            # Ensure the lists have been populated
            if i >= len(self.img_display) or i >= len(self.anim_list):
                continue

            anim = self.anim_list[i]
            total_frames = anim.shape[1] // anim.shape[0]
            self.nframes_list[i] = (self.nframes_list[i] + 1) % total_frames

            # Extract the next frame
            start = anim.shape[0] * self.nframes_list[i]
            end = anim.shape[0] * (self.nframes_list[i] + 1)
            new_img = anim[:, start:end, :]

            # Update the image object
            self.img_display[i].set_data(new_img)

        # Redraw the Matplotlib canvas via its Kivy wrapper
        if self.canvas_widget:
            self.canvas_widget.draw()

    def on_enter(self):
        # Schedule the update loop when the screen is shown
        self.update_event = Clock.schedule_interval(self.update, 1 / 30)

    def on_leave(self):
        # Cancel the update loop when leaving the screen
        if hasattr(self, 'update_event'):
            self.update_event.cancel()
        # Do not close the figure here if it is still in use by the canvas

    def go_back(self, current_name, *args):
     # Get the ScreenManager
        sm = self.manager
        sm.transition = SlideTransition(direction="right")
        sm.current = "main_menu"

class TestApp(App):
    def __init__(self, main_lip_path: str):
        super().__init__()
        self.main_lip = pd.read_csv(main_lip_path)
        self.team_lip = pd.read_csv(main_lip_path.replace('.lip', '_team.lip'))
        # self.main_lip.set_index('n_id', inplace=True)
        # self.team_lip.set_index('n_id', inplace=True)

    def finish_and_write(self):
        App.stop(self)

    def build(self):
        self.sm = ScreenManager()
        self.team_lip.set_index('n_id', inplace=True, drop=False)
        # self.main_lip.set_index('n_id', inplace=True, drop=False)

        # print('main_lip in TEAM MANAGER:', self.main_lip.head())
        print('team_lip in TEAM MANAGER:', self.team_lip)

        # Pass all the necessary lists to the ShowTeamScreen screen
        CurrentTeam = ShowTeamScreen(name="current_team",
                                    team_lip=self.team_lip,
                                    end_flag=False)
        self.sm.add_widget(CurrentTeam)
        return self.sm

def TeamManager_main(main_lip_path, *largs):
    if main_lip_path is None:
        if len(sys.argv) >= 1:
            main_lip_path = sys.argv[1]
        else:
            print("Error: Missing lipstick_path argument.")
            sys.exit(1)

    TestApp(main_lip_path).run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lipstick_path = sys.argv[1]
    else:
        print("Error: Missing lipstick_path argument.")
        lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/mht/data/processed/LIPSTICK/hebrew_db.lip'
    TeamManager_main(lipstick_path)