from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
import logging
from kivy.logger import Logger as kvLogger
kvLogger.setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

import threading
import time
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatch
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

from io import BytesIO
from skimage.io import imread

from time import sleep
from bidi.algorithm import get_display
import sys
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH+'/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = '/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Battlers/'

sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
sys.path.append(ROOT_PATH+'/scripts/ML_duolingo')
from duolingo_hlr import *
from update_lipstick import *
from add_correctButton import CorrectionDialog

import rnd_exercise_scheduler as daemon

def set_question(lipstick_path : str, size_head : int = 10):
    """Read lipstick head (least practiced words) and select a random question and translation
        size_head : number of options to shuffle from
        return:
          word_ll : word in learning language from random head entry
          word_ul : word in user language from random head entry
          rndi : index number from random entry (to avoid option repetition in MA)
    """
    lips_head = pd.read_csv(lipstick_path, nrows = size_head)

    rndi = np.random.randint(0, size_head)
    qentry = lips_head.iloc[rndi]
    word_ll, word_ul = qentry.word_ll, qentry.word_ul
    return word_ll, word_ul, rndi

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


class EachOption(Button):
    def __init__(self, text, val, rtl_flag=False):
        super().__init__(size_hint=(1, 0.8))
        self.app = App.get_running_app()

        # Remove the default button background
        self.background_normal = ''  # Disable default background
        self.background_down = ''  # Disable pressed background
        self.background_color = (0, 0, 0, 0)  # Fully transparent
        # self.size_hint=(1, 0.8),
        self.pos_hint={"x": 0, "y": 0}

        # Add a persistent color instruction to canvas.before
        with self.canvas.before:
            self.color_instruction = Color(0.4, 0.2, 0, 1)  # Default color (brownish)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])

        # Bind size and position changes
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Handle RTL text if needed
        if rtl_flag:
            text_displ = get_display(text)
        else:
            text_displ = text

        # Set properties
        self.text = text_displ
        self.val = val
        self.iw : str = text # Store variable for processing
        self.word_ul = self.app.word_ul
        self.font_name = FONT_HEB  # Replace with your font path
        self.font_size = 40
        self.bold = True
        self.app = App.get_running_app()

    def update_rect(self, *args):
        """Update the size and position of the rounded rectangle."""
        self.bg.size = self.size
        self.bg.pos = self.pos

    
    def update_color(self):
        """Update the color of the button immediately."""
        with self.canvas.before:
            if self.val:
                self.color_instruction.rgba = (0, 1, 0, 0.3)  # Green
                self.text = "Correct! %s" % self.text
                self.perf = 1
            else:
                self.color_instruction.rgba = (1, 0, 0, 0.3)  # Red
                self.text = "Incorrect! %s" % self.text
                self.perf = 0
        self.canvas.ask_update()  # Refresh canvas immediately

    def on_release(self, *args):
        """Custom behavior on button release."""
        self.disabled = True  # Disable the button after clicking

        # Instantly update the color
        self.update_color()
        elapsed_time = time.time() - self.app_start_time
        self.speed = 1/elapsed_time
        print('Mode:', 'm' + self.app.modality)

        # Run in a background thread
        threading.Thread(
            target=self.background_update_all,
            daemon=True
        ).start()

        # Close the app after triggering the background update
        self.app.on_close()

    def background_update_all(self):
        """Run update_all() in the background to avoid blocking the UI."""
        update_all(
            self.app.lipstick,
            self.app.lippath,
            self.word_ul,
            self.perf,
            self.speed,
            mode='m' + self.app.modality
        )

class MultipleAnswer(App):

    def __init__(self, lipstick : pd.DataFrame, lippath : str, modality : str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath
        self.modality = modality
        self.lipstick = self.load_lipstick()
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
        if self.modality == 'dt': 
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        elif self.modality == 'rt':
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'

        self.box = BoxLayout(orientation = 'vertical') # Used this to nest grid into box
        self.upper_panel = GridLayout(cols=3, size_hint_y=0.8)


    def load_lipstick(self):
        if self.modality == 'rt': index = 'word_ll'
        elif self.modality == 'dt': index = 'word_ul'

        lipstick = pd.read_csv(self.lippath)
        lipstick.set_index(index, inplace=True, drop=False)
        return lipstick

    def load_options(self, question : str, answer : str, modality = ['dt', 'rt']):
        # options_panel = GridLayout(cols=1, rows=2, size_hint_x=0.1)
        self.optMenu = GridLayout(cols=1, rows=2, size_hint_x=0.25, padding=20, spacing=20)
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        if modality == 'dt': correction = CorrectionDialog(question, answer)
        elif modality == 'rt': correction = CorrectionDialog(answer, question)

        self.giveup.bind(on_release=self.exit)

        self.optMenu.add_widget(self.giveup)
        self.optMenu.add_widget(correction)

        self.upper_panel.add_widget(self.optMenu)
        # self.grid.add_widget(self.upperPanel)
        self.box.add_widget(self.upper_panel)

    def load_answers(self, answers: dict):
        self.listOp = []
        self.AnswerPanel = GridLayout(cols=2, rows=2, padding=40, spacing=20)
        
        hints = ['A', 'B', 'C', 'D']
        for h, el in zip(hints, answers):
            answer_button_layout = FloatLayout()
            small_label = Label(text=h, size_hint=(0.2, 0.2), pos_hint={"x": 0, "y": 0.8})
            answer_button_layout.add_widget(small_label)

            op = EachOption(el, answers[el], self.rtl_flag, )
            answer_button_layout.add_widget(op)
            self.listOp.append(op)

            self.AnswerPanel.add_widget(answer_button_layout)
        Window.bind(on_key_down=self._on_keyboard_handler)
        self.box.add_widget(self.AnswerPanel)

    def plot_combat_stats(self, entry_stats, ax = None):
        
        positions = [(0.125, 0.75), (0.25, 0.75), (0.375, 0.75), (0.175, 0.4), (0.325, 0.4)]
        fig = plt.figure(figsize=(12, 4))
        fig.patch.set_facecolor("black")
        gs = GridSpec(3, 4, width_ratios=[0.3, 0.3, 0.3, 0.9], height_ratios=[1, 1, 1])

        colors = ['gold', 'maroon', 'magenta', 'navy', 'darkorange']
        
        for i, ((x, y), (k, v) )in enumerate(zip(positions, entry_stats.items()) ):
            print(k, v)
            ax = fig.add_axes([x - 0.1, y - 0.1, 0.3, 0.3])  # [x, y, width, height]
            ax.pie([v, 10-v], wedgeprops=dict(width=0.5), startangle=270, colors=[colors[i], '0.9'])
            ax.set_xlabel(k, fontsize=16)
            ax.xaxis.label.set_color('yellow')

        health_ax = fig.add_subplot(gs[2, :3])  # Spans the second row, columns 2-3
        health_ax.set_xlim(0, 1)
        # health_ax.set_ylim(0, 1)
        draw_health_bar(entry_stats, health_ax)

        axim = fig.add_subplot(gs[:, 3])         # Spans all rows, last column
        impath = PATH_ANIM+str(self.nid).zfill(3)+'.png'
        self.anim = imread(impath)
        
        img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe+1) , :]        
        self.img_display = axim.imshow(img)  # Store reference to imshow
        axim.set(xlabel=f'Translate: {self.question}',)
        axim.xaxis.label.set_color('yellow')
        axim.xaxis.label.set_fontsize(26)

        return fig
     
    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        if keycode in range(30, 33):
            print("Keyboard pressed! {}".format(keycode))
            print('Firing option %i' %(keycode-29))
            self.listOp[keycode - 30].on_release()
        if keycode == 4:  # 'a' key
            self.listOp[0].on_release()
        elif keycode == 5:  # 'b' key
            self.listOp[1].on_release()
        elif keycode == 6:  # 'c' key
            self.listOp[2].on_release()
        elif keycode == 7:  # 'd' key
            self.listOp[3].on_release()
        #else:
        #    print("Keyboard pressed! {}".format(keycode))

    def exit(self, instance):
        print("break: ", daemon.BREAK)
        print('Exiting')
        daemon.BREAK = False
        print('Break changed to: ', daemon.BREAK)
        App.stop(self)

    def on_close(self, *args):
        self.giveup.text='Giving up in 2s'
        Clock.schedule_interval(self.clock_callback, 2)
        return self.giveup

    def clock_callback(self, dt):
        self.giveup.text = "Giving callback up in 2s"
        App.stop(self)

    def build(self):

        opts = rnd_options(self.lippath, iquest=self.iqu, modality=self.modality)
        opts[self.answer] = True
        print('opts', opts)
        shufOpts = shuffle_dic(opts)   # Shuffle order to show the buttons
        
        self.load_options(self.question, self.answer, modality=self.modality)
        self.load_answers(shufOpts)

        if self.rtl_flag:
            self.question = get_display(self.question)

        self.nframe = 0

        # Until here lip.index is word_ul for madte and word_ll for madte
        self.lipstick.set_index('n_id', inplace=True, drop=False)

        print(self.lipstick.loc[self.nid])
        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        print(entry_stats)
        self.fig = self.plot_combat_stats(entry_stats)
        self.canvas = FigureCanvasKivyAgg(self.fig)

        self.upper_panel.add_widget(self.canvas)
        # self.lipstick.set_index(self.checkEntry, inplace=True, drop=False)
        
        Clock.schedule_interval(self.update, 1 / 30)  # 30 FPS
        return self.box

    def update(self, dt):
        """Update function for animation"""
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])  # Loop through frames

        new_img = self.anim[:, self.anim.shape[0] * self.nframe: self.anim.shape[0] * (self.nframe+1), :]
        self.img_display.set_data(new_img)  # Update image data

        self.canvas.draw()  # Redraw the canvas

    def run(self):
        super().run()
        # return daemon.BREAK
    
if __name__ == "__main__":
    """Only for testing purposes. Manually assign modality"""

    lipstick_path = sys.argv[1]
    
    modality = 'rt'

    MA = MultipleAnswer(lipstick, lipstick_path, modality='rt')

    rtl = False
    if lipstick.learning_language.iloc[0] == 'iw':
        rtl = True

    MA.load_question(qu, rtl)
    MA.load_options(qu, answ, modality='dt')
    MA.load_answers(shufOpts, rtl)

    perf = MA.run()
    print(perf)
