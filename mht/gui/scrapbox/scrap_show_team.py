from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window

import logging
from kivy.logger import Logger as kvLogger

from bidi.algorithm import get_display

kvLogger.setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

import sys
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")

matplotlib.use("Agg")
from skimage.io import imread

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
from test_statimages import *

PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

# Set the window dimensions

# Set window dimensions (width, height)
Window.size = (400, 800)


class ShowTeam(App):
    def __init__(self, lipstick: pd.DataFrame):
        App.__init__(self)
        self.lipstick = lipstick
        self.box = BoxLayout(orientation = 'vertical')
        self.img_display = []
        self.anim_list = []
        self.nframes_list = []


    def plot_team(self, nids, ax = None):
        
        fig = plt.figure(figsize=(3, 20))
        fig.patch.set_facecolor("black")
        gs = GridSpec(6, 2, width_ratios=[1, 1], height_ratios=[0.8, 0.15, 0.8, 0.15, 0.8, 0.15])
        print('Nids in plot_team:', nids)

        for i, nid in enumerate(nids):
            j, k = i//2, i % 2
            print(i, j, k)
            print(nid)
            entry_stats = load_pkmn_stats(self.lipstick, nid)
            word_ll = self.lipstick.loc[nid, 'word_ll']
            if self.lipstick.loc[nid, 'learning_language'] == 'iw': 
                word_ll = get_display(word_ll)

            ax = fig.add_subplot(gs[2*j, k])
            impath = PATH_ANIM+str(nid).zfill(3)+'.png'
            print('impath: ', impath)
            anim = imread(impath)
            self.anim_list.append(anim)
            img = anim[:, : anim.shape[0], :]                     # This is only the initialization, so nframe = 0
            # img = anim[:, anim.shape[0] * self.nframe: anim.shape[0] * (self.nframe+1) , :]       
            self.img_display.append(ax.imshow(img,  aspect="auto") ) 
            self.nframes_list.append(0)     # Start frame counter at 0
            ax.set(title=word_ll)
            ax.title.set_color('yellow')
            ax.title.set_fontsize(26)

            hp = entry_stats['hp']
            level = entry_stats['level']
            axbar = fig.add_subplot(gs[2*j+1, k])
            axbar.set_facecolor("black")


            draw_rounded_bar(axbar, width=0.8, color='lightgray', y_offset=0.2, bar_height=0.3)
            draw_rounded_bar(axbar, width=hp * 0.8, color='green', y_offset=0.2, bar_height=0.3)
            axbar.text(0.5, -0.3, f'Level: {level}/100', size=16, ha='center', color='yellow', transform=ax.transAxes)
            axbar.text(0.5, -0.6, f'HP = {int(hp * 100)}/100', size=16, ha='center', color='yellow', transform=ax.transAxes)
            axbar.set_xlim(0, 1)
            axbar.set_ylim(0, 1)
            axbar.axis("off")
        fig.tight_layout(w_pad=0.1)
        return fig

    def build(self):
        lb = Label(text= 'Current team:', size_hint=(1, 0.1) , pos_hint={"x": 0, "y": 0.9})
        self.box.add_widget(lb)
        self.nframe = 0

        self.lipstick.set_index('n_id', inplace=True, drop=False)

        self.nids = np.array(self.lipstick.n_id.values)
        print(self.nids)
        self.fig = self.plot_team(self.nids)
        self.canvas = FigureCanvasKivyAgg(self.fig)
        self.box.add_widget(self.canvas)
        
        Clock.schedule_interval(self.update, 1 / 30)  # 30 FPS
        return self.box

    def update(self, dt):
        """Update function for animation"""

        for i, nid in enumerate(self.nids):
            total_frames = self.anim_list[i].shape[1] // self.anim_list[i].shape[0]  # Total frames
            self.nframes_list[i] = (self.nframes_list[i] + 1) % total_frames  # Loop through frames
            self.nframe = (self.nframe + 1) % (self.anim_list[i].shape[1] // self.anim_list[i].shape[0])  # Loop through frames

            new_img = self.anim_list[i][
                :, self.anim_list[i].shape[0] * self.nframes_list[i]: self.anim_list[i].shape[0] * (self.nframes_list[i]+1), :
            ]
            self.img_display[i].set_data(new_img)  # Update image data

        self.canvas.draw()  # Redraw the canvas
    

if __name__ == "__main__":
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db_team.lip'

    lipstick = pd.read_csv(lipstick_path, index_col=False)
    # lipstick.set_index('word_ul', inplace=True, drop=False)

    ST = ShowTeam(lipstick)#, lipstick_path)
    ST.run()