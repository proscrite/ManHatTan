# common.py
import time, sys, unicodedata, pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
from skimage.io import imread
from bidi.algorithm import get_display

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


matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")

matplotlib.use("Agg")

# --- Constants ---
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'
LIPSTICK_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db.lip'

# --- Utility Functions ---
def strip_accents(s):
    """Strip accents from a string."""
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def load_lipstick(lippath, modality):
    """
    Load the lipstick CSV file.
    The index is chosen based on modality: use 'word_ul' for direct translation (dt)
    and 'word_ll' for reverse translation (rt).
    """
    index = 'word_ul' if modality == 'dt' else 'word_ll'
    lipstick = pd.read_csv(lippath)
    lipstick.set_index(index, inplace=True, drop=False)
    return lipstick

def set_question(lipstick_path : str, rtl_flag = False, size_head : int = 10):
    """Read lipstick head (least practiced words) and select a random question and translation
        size_head : number of options to shuffle from
        return:
          word_ll : word in learning language from random head entry
          word_ul : word in user language from random head entry
          rndi : index number from random entry (to avoid option repetition in MA)
    """
    lips_head = pd.read_csv(lipstick_path, nrows = size_head)

    rndi = np.random.randint(0, size_head)
    qentry = lips_head.loc[rndi]
    # print(qentry)

    while qentry.rebag:
        print('You have practiced this word enough')
        print(qentry)
        rndi = np.random.randint(0, size_head)
        qentry = lips_head.iloc[rndi]
        
    nid = qentry.n_id
    word_ll, word_ul = qentry.word_ll, qentry.word_ul

    print(f'word_ll = {word_ll}, word_ul = {word_ul}, iqu = {rndi}, nid = {nid}')
    return word_ll, word_ul, rndi, nid

def rnd_options(lipstick_path : str, iquest : int, modality : str, n_options : int = 3, size_head : int = 0):
    """Pick at random n_options to set as false answers from lipstick head
        (full if size_head == 0)
        modality :
            'dt' for Direct Translation (Learning -> User)
            'rt' for Reverse Translation (User -> Learning)
        Return dict options {'word' : False}"""
    from random import sample

    if modality == 'dt': word_lang = 'word_ul'
    elif modality == 'rt': word_lang = 'word_ll'
    else: print('Incorrect modality in rnd_options function')

    if size_head == 0:
        lips_head = pd.read_csv(lipstick_path)
        size_head = len(lips_head)
    else:
        lips_head = pd.read_csv(lipstick_path, nrows = size_head)

    options = {}
    list_head = list(range(size_head))
    if iquest in list_head:
        list_head.remove(iquest)  # Remove question from possible answers (else only N-1 answers are offered)
    else:
        print('iquest:', iquest)#, lips_head.iloc[iquest].word_id)

    rndi = sample(list_head, n_options)
    for i in range(n_options):
        rndOp = lips_head.iloc[rndi[i]][word_lang]
        print(rndOp)
        options[rndOp] = False
    return options

def shuffle_dic(opts : dict):
    """Shuffle option dictionary to diplay in grid"""
    from random import shuffle
    from collections import OrderedDict
    b = list(opts.items())
    shuffle(b)
    shufOpt = OrderedDict(b)
    return  shufOpt

# --- Pokemon plotting functions ---- 
def plot_combat_stats(entry_stats, nframe, nid, question_displ):
    """
    Create a matplotlib figure showing combat stats and an animated image.
    Returns the figure, the image object, and the full animation array.
    """
    positions = [(0.125, 0.75), (0.25, 0.75), (0.375, 0.75),
                 (0.175, 0.4), (0.325, 0.4)]
    fig = plt.figure(figsize=(12, 4))
    fig.patch.set_facecolor("black")
    gs = GridSpec(3, 4, width_ratios=[0.3, 0.3, 0.3, 0.9],
                  height_ratios=[1, 1, 1])
    colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange']
    
    # Example: draw pie charts for each stat (assuming entry_stats is a dict)
    for (x, y), (k, v) in zip(positions, entry_stats.items()):
        ax = fig.add_axes([x - 0.1, y - 0.1, 0.3, 0.3])
        ax.pie([v, 10 - v], wedgeprops=dict(width=0.5),
               startangle=270, colors=[colors.pop(0), '0.9'])
        ax.set_xlabel(k, fontsize=16)
        ax.xaxis.label.set_color('yellow')
    
    # Dummy health bar (customize as needed)
    ax_health = fig.add_subplot(gs[2, :3])
    ax_health.set_xlim(0, 1)
    ax_health.set_title("Health Bar", color='yellow')
    
    # Animated image: load sprite sheet and display current frame
    ax_im = fig.add_subplot(gs[:, 3])
    impath = PATH_ANIM + str(nid).zfill(3) + '.png'
    anim = imread(impath)
    frame_width = anim.shape[0]
    img = anim[:, frame_width * nframe: frame_width * (nframe + 1), :]
    im_obj = ax_im.imshow(img)
    ax_im.set_xlabel(f'Translate: {question_displ}', color='yellow',
                     fontsize=26)
    
    return fig, im_obj, anim

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

