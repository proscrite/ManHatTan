import os
# os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ["KIVY_NO_FILELOG"] = "1"

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

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
from common import FigureCanvasKivyAgg
from skimage.io import imread

import numpy as np
import pandas as pd

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH + '/scripts/python_scripts/')
from plot_pkmn_panel import *  # Provides load_pkmn_stats and draw_rounded_bar

PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

# Set window dimensions (width, height)
Window.size = (400, 800)


class ShowTeamScreen(Screen):
    def __init__(self, name: str, fig, nids, anim_list, img_display, nframes_list, end_flag: bool = False, **kwargs):
        super().__init__(name=name, **kwargs)
        self.fig = fig
        self.nids = nids
        self.anim_list = anim_list
        self.img_display = img_display
        self.nframes_list = nframes_list

        # Create a BoxLayout to hold the Matplotlib figure
        self.box = BoxLayout(orientation="vertical")

        # Optionally add a header or control buttons
        header = BoxLayout(size_hint=(1, 0.1))
        header.add_widget(Label(text="Current Team:", color=(1, 1, 1, 1)))
        continue_btn = Button(text="Continue", size_hint=(0.2, 1))

        if end_flag:
            function_button = App.get_running_app().finish_and_write
        else:
            function_button = App.get_running_app().show_new_team

        continue_btn.bind(on_release=lambda *args: function_button())
        header.add_widget(continue_btn)
        self.box.add_widget(header)

        # Embed the Matplotlib figure using FigureCanvasKivyAgg
        self.canvas_widget = FigureCanvasKivyAgg(self.fig)
        self.box.add_widget(self.canvas_widget)


        # Add the BoxLayout to the Screen
        self.add_widget(self.box)

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


class TestApp(App):
    def __init__(self, main_lip_path: str):
        super().__init__()
        self.main_lip = pd.read_csv(main_lip_path)
        self.team_lip = pd.read_csv(main_lip_path.replace('.lip', '_team.lip'))
        # self.main_lip.set_index('n_id', inplace=True)
        # self.team_lip.set_index('n_id', inplace=True)

        # These lists will be filled by plot_team
        self.img_display = []
        self.anim_list = []
        self.nframes_list = []
        self.nids = None
        self.fig = None

    def plot_team(self, lipstick, nids):
        self.fig = plt.figure(figsize=(3, 20))
        self.fig.patch.set_facecolor("black")
        gs = GridSpec(6, 2, width_ratios=[1, 1],
                      height_ratios=[0.8, 0.15, 0.8, 0.15, 0.8, 0.15])
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
            ax.set(title=word_ll)
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
        self.fig.tight_layout(w_pad=0.1)
        return self.fig

    def show_new_team(self):
        self.main_lip.set_index('n_id', inplace=True, drop=False)
        print(self.main_lip[self.main_lip['rebag'] == False]) 
        new_team = self.main_lip[self.main_lip['rebag'] == False].head(6)
        new_team.set_index('n_id')
        print(new_team)
        self.new_nids = new_team.index.values
        print("New NIDs:", self.new_nids)

        # Reset lists before generating a new figure
        self.img_display = []
        self.anim_list = []
        self.nframes_list = []

        # Generate the new figure
        self.fig2 = self.plot_team(lipstick=new_team, nids=self.new_nids)

        # Create the new team screen
        NewTeam = ShowTeamScreen(
            name="new_team",
            fig=self.fig2,
            nids=self.new_nids,
            anim_list=self.anim_list,
            img_display=self.img_display,
            nframes_list=self.nframes_list,
            end_flag=True
        )

        # Add the screen to the ScreenManager and switch
        self.sm.add_widget(NewTeam)
        self.sm.current = 'new_team'

    def finish_and_write(self):
        App.stop(self)

    def build(self):
        self.sm = ScreenManager()
        self.team_lip.set_index('n_id', inplace=True, drop=False)
        self.main_lip.set_index('n_id', inplace=True, drop=False)

        print('main_lip in TEAM MANAGER:', self.main_lip.head())
        print('team_lip in TEAM MANAGER:', self.team_lip)


        self.nids = np.array(self.team_lip.n_id[:6].values)
        print(self.nids)
        self.fig = self.plot_team(lipstick=self.team_lip, nids=self.nids)

        # Pass all the necessary lists to the ShowTeamScreen screen
        CurrentTeam = ShowTeamScreen(name="current_team",
                                    fig=self.fig,
                                    nids=self.nids,
                                    anim_list=self.anim_list,
                                    img_display=self.img_display,
                                    nframes_list=self.nframes_list,
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
        lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db.lip'
    TeamManager_main(lipstick_path)