
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

# matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")

# matplotlib.use("Agg")
import pandas as pd
import numpy as np

import sys
PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

sys.path.append('../scripts/python_scripts/')
sys.path.append('../scripts/ML_duolingo')

import io
from skimage import img_as_ubyte
from skimage.io import imread

"""
# def create_health_bar_figure():
#     # Create the figure and gridspec
#     fig = plt.figure(figsize=(12, 6))
#     gs = GridSpec(2, 4, height_ratios=[4, 1], figure=fig)  # 2 rows, 4 columns

#     # Create the top subplots (4 subplots in a row)
#     axes = [fig.add_subplot(gs[0, i]) for i in range(4)]
#     for i, ax in enumerate(axes):
#         ax.plot([0, 1, 2], [i, i + 1, i + 2])  # Example plot
#         ax.set_title(f"Plot {i + 1}")

#     # Create the bottom subplot for the health bar
#     health_ax = fig.add_subplot(gs[1, :])  # Span all 4 columns in the second row
#     health_ax.set_xlim(0, 1)
#     health_ax.set_ylim(0, 1)

#     # Draw the background bar (full width)
#     draw_health_bar(health_ax, width=0.8, color='lightgray', y_offset=0.25, bar_height=0.5)

#     # Draw the health bar (proportional width)
#     hp = 0.4  # Current health (fraction of max)
#     draw_health_bar(health_ax, width=0.4 * 0.8, color='green', y_offset=0.25, bar_height=0.5)

#     # Add text in the center of the bars
#     health_ax.text(0.5, 0.5, f'{int(hp * 100)}/100', size=20, ha='center', va='center', transform=health_ax.transAxes)

#     # Remove axes from the health bar subplot
#     health_ax.axis('off')

#     # Adjust spacing between subplots
#     plt.subplots_adjust(hspace=0.5)

#     return fig
"""
def draw_rounded_bar(ax, width, color, y_offset=0.25, bar_height=0.5, corner_radius=0.07):
    """
    Draws a health bar with rounded corners.
    
    Args:
        ax: The matplotlib axis to draw the bar on.
        width (float): The width of the bar (0 to 1).
        color (str): The color of the bar.
        y_offset (float): The vertical offset for the bar (default is 0.25).
        bar_height (float): The height of the bar (default is 0.5).
        corner_radius (float): The corner radius for the bar (default is 0.07).
    """
    # Create a fancy box with rounded corners
    p_fancy = FancyBboxPatch((0.1, y_offset),  # Start position
                              width,           # Width of the bar
                              bar_height,      # Height of the bar
                              boxstyle=f"round,pad={corner_radius}",
                              fc=color,        # Face color
                              ec=(0, 0, 0))    # Edge color
    ax.add_patch(p_fancy)

def draw_health_bar(entry_stats, ax):
    hp = entry_stats['hp']
    level = entry_stats['level']
    draw_rounded_bar(ax, width=0.8, color='lightgray', y_offset=0.05, bar_height=0.3)
    draw_rounded_bar(ax, width=hp * 0.8, color='green', y_offset=0.05, bar_height=0.3)
    ax.text(0.5, -0.2, f'HP = {int(hp * 100)}/100       Level: {level}/100', size=20, ha='center', va='center', color='yellow', transform=ax.transAxes)
    # Hide the axis
    ax.axis('off')

def plot_combat_modalities(entry_stats, ax = None):
    positions = [(0.25, 0.6), (0.5, 0.6),  (0.75, 0.6), (0.375, 0.3), (0.625, 0.3) ]
    fig = plt.gcf()
    colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange',]
    for i, ((x, y), (k, v) )in enumerate(zip(positions, entry_stats.items()) ):
        ax = fig.add_axes([x - 0.1, y - 0.1, 0.2, 0.2])  # [x, y, width, height]
        ax.pie([v, 10-v], wedgeprops=dict(width=0.5), startangle=270, colors=[colors[i], '0.9'])
        ax.set_xlabel(k, fontsize=20)

def show_pkm():
    # nid = 94
    nid = np.random.randint(900)
    
    impath = PATH_ANIM+str(nid).zfill(3)+'.png'
    anim = imread(impath)
    nframe = 0
    frame = anim[:, anim.shape[0] * nframe: anim.shape[0] * (nframe+1) , :]
    return frame


def plot_stats(entry_stats, hp):
    fig = plt.figure(figsize=(12, 4))
    fig.patch.set_facecolor("black")

    gs = GridSpec(2, 5, width_ratios=[0.3, 0.3, 0.3, 0.3, 0.9], height_ratios=[2, 1])

    axes = [fig.add_subplot(gs[0, i]) for i in range(4)]
    health_ax = fig.add_subplot(gs[1, :4])  # Span all 4 columns in the second row
    axim = fig.add_subplot(gs[:, 4])

    plot_combat_stats(entry_stats, axes)

    # Create the bottom subplot for the health bar
    health_ax.set_xlim(0, 1)
    health_ax.set_ylim(0, 1)

    draw_health_bar(hp, health_ax)

    img = show_pkm()
    axim.imshow(img)
    for ax in axes + [health_ax, axim]:
        ax.set_facecolor("black")

    plt.axis('off')
    plt.subplots_adjust(hspace=0.)
    plt.subplots_adjust(wspace=0.)
    plt.tight_layout()

    return fig

def load_pkmn_stats(lipstick, nid):
    
    qentry = lipstick.loc[nid].copy()
    
    dict_stats = {'mrt': 'Attack',
                'mdt': 'Defense', 
                'wrt': 'Sp. Attack',
                'wdt': 'Sp. Defense',
                }
    entry_stats = {}
    entry_stats['Speed'] = qentry['speed'] * 10 + 5
    for k, v in dict_stats.items():
        entry_stats[v] = (0.5 + qentry[k+'_correct'] ) / (1 + qentry[k+'_history']) * 10

    entry_stats['hp'] = qentry['p_recall'] / 100 + 0.09
    entry_stats['level'] = qentry['history_correct'] + 10
    return entry_stats

#########################################################
root = Builder.load_string(r"""
<OrangeWidget>
<OrangeGraphicWidget>
    canvas:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.center_x - 15, 20
            size: 30, 90
        
    BoxLayout:
        id: destination
""")
class Plots(Widget):
    def __init__(self):
        super(Plots, self).__init__()
        self.number_of_plots = 3
        
class OrangeWidget(Screen):
    def __init__(self, fig, **kwargs):
        super(OrangeWidget, self).__init__(**kwargs)
        self.app = App.get_running_app()
        # floatLayout = FloatLayout(size_hint_x=1)
        # scrollView = ScrollView(size_hint=(1, 1))
        self.figure = fig
        # figure = self.app.load_pkmn_stats(self.nid)

        # add custom widget into that layout
        customWidget = OrangeGraphicWidget(height=400, size_hint_x=1, size_hint_y=0.7)
        customWidget.ids.destination.add_widget(FigureCanvasKivyAgg(fig))

        #customWidget.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        # floatLayout.add_widget(customWidget)

        self.add_widget(customWidget)

class OrangeGraphicWidget(RelativeLayout):
    pass

class ProgressChart(App):
    def __init__(self, lipstick: pd.DataFrame):
        App.__init__(self)
        self.lipstick = lipstick
        random_nid = np.random.randint(len(lipstick['n_id']))
        entry_stats, hp = load_pkmn_stats(lipstick, random_nid)
        self.fig = plot_stats(entry_stats, hp)
    def build(self):
        return OrangeWidget(self.fig)


if __name__ == "__main__":
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db.lip'

    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Il_castello_dei_destini_incrociati.lip'
    lipstick = pd.read_csv(lipstick_path, index_col=False)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    PC = ProgressChart(lipstick)#, lipstick_path)

    # PC.build()
    PC.run()
