from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
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



    def plot_team(self, nids):
        self.buttons = []  # To keep track of buttons for animations
        fig = plt.figure(figsize=(6, 10))
        fig.patch.set_facecolor("black")
        gs = GridSpec(
            6, 2,
            width_ratios=[1, 1], 
            height_ratios=[0.8, 0.15, 0.8, 0.15, 0.8, 0.15],
            wspace=0.3,  
            hspace=0.5
        )

        print("Nids in plot_team:", nids)

        for i, nid in enumerate(nids):
            j, k = i // 2, i % 2
            print(nid)
            entry_stats = load_pkmn_stats(self.lipstick, nid)
            word_ll = self.lipstick.loc[nid, "word_ll"]

            # Main animated image
            ax = fig.add_subplot(gs[2 * j, k])
            impath = PATH_ANIM + str(nid).zfill(3) + ".png"
            print("impath: ", impath)
            anim = imread(impath)
            self.anim_list.append(anim)

            img = anim[:, :anim.shape[0], :]  # Initial frame (nframe=0)
            self.img_display.append(ax.imshow(img))
            self.nframes_list.append(0)  # Start frame counter at 0
            ax.set(title=word_ll)
            ax.title.set_color("yellow")
            ax.title.set_fontsize(20)

            # Create a button for this animation
            button = Button(size_hint=(0.4, 0.4))
            button.bind(on_press=self.on_animation_click)
            button.nid = nid  # Attach nid to the button for identification
            self.buttons.append(button)

            # Add the button to the Kivy layout
            self.box.add_widget(button)

            # Health bar subplot
            axbar = fig.add_subplot(gs[2 * j + 1, k])
            axbar.set_facecolor("black")
            axbar.set_xlim(0, 1)
            axbar.set_ylim(0, 1)

            draw_rounded_bar(axbar, width=0.8, color="lightgray", y_offset=0.25, bar_height=0.3)
            draw_rounded_bar(axbar, width=entry_stats["hp"] * 0.8, color="green", y_offset=0.25, bar_height=0.3)

            # Add text (level and HP)
            axbar.text(0.5, 0.6, f"Level: {entry_stats['level']}/100", size=14, ha="center", color="yellow")
            axbar.text(0.5, 0.2, f"HP = {int(entry_stats['hp'] * 100)}/100", size=14, ha="center", color="yellow")

        fig.tight_layout()
        return fig
    
    def on_animation_click(self, instance):
        nid = instance.nid  # Access the nid from the button
        print(f"Clicked on animation for Nid: {nid}")

        # Example: You can display more details, start a battle, or trigger other actions
        # Here we'll just log the nid
        self.show_message(f"Pokemon {nid} clicked!")  # Placeholder function


    def build(self):
        lb = Label(text= 'Current team:', size_hint=(1, 0.1) , pos_hint={"x": 0, "y": 0.9})
        self.box.add_widget(lb)
        self.nframe = 0

        self.lipstick.set_index('n_id', inplace=True, drop=False)

        self.nids = np.array(self.lipstick.n_id.values)
        self.fig = self.plot_team(self.nids)

        # Create FloatLayout for overlay
        float_layout = FloatLayout(size_hint=(1, 0.9))

        # Add Matplotlib Canvas
        self.canvas = FigureCanvasKivyAgg(self.fig)
        float_layout.add_widget(self.canvas)
        

        # Add Transparent Buttons
        for i, nid in enumerate(self.nids):
            row, col = divmod(i, 2)  # Get row and column index (2 columns)

            # Create a transparent button
            button = Button(
                background_normal="",  # Remove normal background
                background_color=(0, 0, 0, 0),  # Fully transparent
                size_hint=(0.5, 1 / 3),  # Button size (2 columns, 3 rows)
                pos_hint={
                    "x": col * 0.5,  # Horizontal position based on column
                    "y": 1 - (row + 1) / 3,  # Vertical position based on row
                },
            )

            button.nid = nid  # Attach the nid to the button for identification
            button.bind(on_press=self.on_animation_click)  # Bind click event
            float_layout.add_widget(button)

        # Add FloatLayout to the main layout
        self.box.add_widget(float_layout)
        
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