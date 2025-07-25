# common.py
import time, sys, unicodedata, pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
from skimage.io import imread
from bidi.algorithm import get_display
from random import sample
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
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
matplotlib.use("Agg")

# --- Constants ---
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
PATH_KINDLES = ROOT_PATH + '/data/raw/kindle_raw/*.html'
PATH_PLAYBOOKS = ROOT_PATH + '/data/raw/playbooks_raw/*.docx'
PATH_GOOGLE_TRANSL = ROOT_PATH + '/data/raw/googletranslate_csv/*.csv'

LIPSTICK_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db.lip'
TEAM_LIP_PATH = LIPSTICK_PATH.replace('.lip', '_team.lip')
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

COLOR_MAP = {
    'blue':   (0.13, 0.19, 0.34, 1),
    'red':    (0.32, 0.13, 0.13, 1),
    'green':  (0.13, 0.27, 0.17, 1),
    'yellow': (0.85, 0.65, 0.13, 1),
    'pink':   (0.8, 0.4, 0.6, 1),
    'orange': (0.9, 0.5, 0.1, 1),
    'gold':   (0.85, 0.65, 0.13, 1),
}
DEFAULT_COLOR = (0.7, 0.7, 0.7, 1)

# --- Language Dictionary ---
# This dictionary maps language codes to their names.
language_dict = {
    'en': 'English',
    'iw': 'Hebrew',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ru': 'Русский',
    'pt': 'Português',
    'it': 'Italiano',
    'ar': 'Arabic',
}

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

def load_similar_words(pathout, target_word):
    word_vectors = np.load(pathout)
    tokens = word_vectors['tokens']
    vectors = word_vectors['vectors']
    token_to_vector = {token: vector for token, vector in zip(tokens, vectors)}
    try:
        target_vector = token_to_vector[target_word]
    except IndexError as e:
        print(e, f' with {target_word}')
        return
    similarities = []

    norm = np.dot(target_vector, target_vector)
    for word in tokens:
        token = token_to_vector[word]
        sim = np.dot(target_vector, token) / norm
        similarities.append((word, sim))
    similarities.sort(key=lambda x: x[1], reverse=True)
    # return the top 3 most similar words
    return [word for word, _ in similarities[1:10]]

def load_similar_words_nlp(lip, target_word, nlp):
    """Load options for multiple answer  by comparing similarity with a target word."""

    # Define the target word and process it to get its token (make sure it has a vector)
    target_token = nlp(target_word)[0]

    other_words = lip.word_ll.values.tolist()  # List of words to compare with the target word
    # Compute similarity for each word in the list
    similarities = []
    for word in other_words:
        token = nlp(word)[0]
        # Check if both tokens have vectors
        if target_token.has_vector and token.has_vector:
            sim = target_token.similarity(token)
            similarities.append((word, sim))
        else:
            similarities.append((word, 0.0))

    # Sort words by similarity in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Print the top 10 most similar words
    for word, score in similarities[:10]:
        print(f"{word}: {score:.3f}, {lip.loc[word, 'word_ul']}")
    return similarities[:3]

def set_question(lipstick_path : str):
    """Read lipstick head (least practiced words) and select a random question and translation
        size_head : number of options to shuffle from
        return:
          word_ll : word in learning language from random head entry
          word_ul : word in user language from random head entry
          rndi : index number from random entry (to avoid option repetition in MA)
    """
    print(f'In set_question, lipstick_path: {lipstick_path}')
    lipstick = pd.read_csv(lipstick_path)

    eligible = lipstick[lipstick['rebag'] == False]
    if eligible.empty:
        raise ValueError("No eligible entries found in lipstick.")
    qentry = eligible.sample(1).iloc[0]
    nid = qentry.n_id
    word_ll, word_ul = qentry.word_ll, qentry.word_ul
    iqu = qentry.name
    word_ll, word_ul = qentry.word_ll, qentry.word_ul

    print(f'word_ll = {word_ll}, word_ul = {word_ul}, iqu = {iqu}, nid = {nid}')
    return word_ll, word_ul, iqu, nid

def sample_similar_options(lipstick_path : str, iquest : int, modality : str, n_options : int = 3):
    """ Pick at random n_options to set as false answers from lipstick head"""
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/mht/data/processed/LIPSTICK/hebrew_db.lip'
    if modality == 'dt': word_lang = 'word_ul'
    elif modality == 'rt': word_lang = 'word_ll'
    else: print('Incorrect modality in sample_similar_options function')
    lip = pd.read_csv(lipstick_path)
    target_word = lip.iloc[iquest]['word_ll']
    lip = lip.set_index('word_ll', drop=False)
    options = {}
    #### Change this: to be extracted from lipstick_path:
    vector_path = '/Users/pabloherrero/Documents/ManHatTan/mht/data/processed/vectors_lip/vectors_heb_lip.npz'
    similar_words = load_similar_words(vector_path, target_word=target_word)
    # similar_words = [get_display(w) for w in similar_words]
    rnd_similar_words = sample(similar_words, n_options)
    for i, rnd_w in enumerate(rnd_similar_words):
        rndOp = lip.loc[rnd_w][word_lang]

        options[rndOp] = False
    return options

def rnd_options(lipstick_path : str, iquest : int, modality : str, n_options : int = 3, size_head : int = 0):
    """Pick at random n_options to set as false answers from lipstick head
        (full if size_head == 0)
        modality :
            'dt' for Direct Translation (Learning -> User)
            'rt' for Reverse Translation (User -> Learning)
        Return dict options {'word' : False}"""

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

# --- Filtering functions ---

def search_verbs(lipstick):
    """Return a DataFrame of rows where 'lexeme_string' contains '<VERB>'."""
    return lipstick[lipstick['lexeme_string'].str.contains('<VERB>', na=False)]

def sample_random_verb(lipstick):
    """Return a random verb (word_ll) from the verbs in lipstick."""
    verbs_df = search_verbs(lipstick)
    if verbs_df.empty:
        return None
    return verbs_df.sample(1).iloc[0]['word_ll']

def filter_sofits(word):
    # Filter out final letters (sofit) from the word
    # and replace them with their regular counterparts for comparison and filtering
    from hebrew import FINAL_MINOR_LETTER_MAPPINGS as sofit_dict
    final_letter = word[-1]
    if final_letter in sofit_dict.keys():
        filtered_word = word[:-1] + sofit_dict[final_letter]
        return filtered_word
    else:
        return word
    
def filter_contained(words, reference_word):
    # Filter out words that contain the reference word
    filtered_words = []
    for w in words:
        wf = filter_sofits(w)
        if reference_word in wf:
            print('Contained in original: ', w)
            continue
        filtered_words.append(w)
    return filtered_words

# --- Similar words functions ---

def calculate_similar_words(selected_word, nlp):
    # Process the selected word with the NLP model
    print('Calculating similar words')
    selected_word = get_display(selected_word)
    selected_filtered = filter_sofits(selected_word)
    word_id = nlp.vocab.strings[selected_word]
    word_vec = nlp.vocab.vectors[word_id]
    most_similar_words = nlp.vocab.vectors.most_similar(np.asarray([word_vec]), n=25)
    words = [nlp.vocab.strings[w] for w in most_similar_words[0][0]]

    filtered_words1 = filter_contained(words, selected_filtered)
    filtered_words = filtered_words1[:16]
    filtered_words = [get_display(w) for w in filtered_words]
    print('Calculated similar words:', filtered_words)
    return filtered_words


# --- Pokemon plotting functions ---- 
def plot_combat_stats(entry_stats, nframe, nid, question_displ, n_cracks: int = 0, width_ratios=None):
    """
    Create a matplotlib figure showing combat stats and an animated image.
    Returns the figure, the image object, and the full animation array.
    """
    if width_ratios is None:
        width_ratios = [0.3, 0.3, 0.3, 0.9]
    fig = plt.figure(figsize=(12, 4))
    fig.patch.set_facecolor("black")
    gs = GridSpec(3, 4, width_ratios=width_ratios, height_ratios=[1, 1, 1])
    colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange']
    
    # Example: draw pie charts for each stat (assuming entry_stats is a dict)
    positions = [(0.125, 0.75), (0.25, 0.75), (0.375, 0.75),
                 (0.175, 0.4), (0.325, 0.4)]
    for (x, y), (k, v) in zip(positions, entry_stats.items()):
        ax = fig.add_axes([x - 0.1, y - 0.1, 0.3, 0.3])
        ax.pie([v, 10 - v], wedgeprops=dict(width=0.5),
               startangle=270, colors=[colors.pop(0), '0.9'])
        ax.set_xlabel(k, fontsize=16)
        ax.xaxis.label.set_color('yellow')
    
    # Dummy health bar (customize as needed)
    ax_health = fig.add_subplot(gs[2, :3])
    ax_health.set_xlim(0, 1)
    draw_health_bar(entry_stats, ax_health)
    
    # Animated image: load sprite sheet and display current frame
    ax_im = fig.add_subplot(gs[:, 3])
    
    im_obj, anim = load_pkmn_animation(ax_im, nframe, nid, n_cracks)
    ax_im.set_xlabel(f'Translate: {question_displ}', color='yellow',
                    fontsize=26)

    return fig, im_obj, anim

def load_pkmn_animation(ax_im, nframe, nid, n_cracks=0):
    """
    Load a Pokemon animation frame into the given axis.
    Args:  
        ax_im: The matplotlib axis to load the image into.
        nframe: The frame number to display.
        nid: The Pokemon ID (0 for special case of EGGs).
        n_cracks: Number of cracks for special animations (default is 0, maximum is 5).
    """
    if nid == 0:
        impath = PATH_ANIM + str(nid).zfill(3) + '_c' + str(n_cracks) + '.png'
    else:
        impath = PATH_ANIM + str(nid).zfill(3) + '.png'
    print(f'Loading animation from: {impath}')
    anim = imread(impath)
    frame_width = anim.shape[0]
    img = anim[:, frame_width * nframe: frame_width * (nframe + 1), :]
    im_obj = ax_im.imshow(img)
    return im_obj, anim

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

def load_pkmn_stats(qentry):
    """Load the stats of a Pokemon from the lipstick DataFrame.
       Returns a dictionary with the stats to be displayed in the combat panel."""
    
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

