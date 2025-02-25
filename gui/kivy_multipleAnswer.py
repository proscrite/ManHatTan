from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock

from skimage.io import imread
from skimage import color, img_as_ubyte
from skimage.transform import resize


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

def train_model(lipstick : pd.DataFrame, lipstick_path : str):
    trainset, testset = read_data(lipstick_path, method='hlr', omit_lexemes=False)

    trainset += testset # Ignore the separation for the update

    model = SpacedRepetitionModel(method='hlr', omit_h_term=False, )
    model.train(trainset)

    print('HLR Model updated, sorting by recall probability')

    prob = pd.Series({i.index: model.predict(i)[0] for i in trainset})
    lipstick.loc['p_pred'] = prob

    lipstick.sort_values('p_recall', inplace=True)
    lipstick.to_csv(lipstick_path, index=False)

def update_all(lipstick : pd.DataFrame, lipstick_path : str, word : str, perform, mode = ['mdt', 'mrt', 'wdt', 'wrt']):
    """Call all update functions and train hlr model"""

    print('Calling update_all in kivy_multiAnswer')
    update_performance(lipstick, word, perform, mode=mode)
    update_timedelta(lipstick, word)

    print('Performance and timedelta updated')
    print(lipstick.loc[word])
    lipstick.to_csv(lipstick_path, index=False)
    sleep(1)
    print('Done writing lipstick:', lipstick_path)
    train_model(lipstick, lipstick_path)

def show_pkm(nid):
    # nid = 94
    nid = np.random.randint(900)
    print('NID: ', nid)
    impath = PATH_ANIM+str(nid).zfill(3)+'.png'
    anim = imread(impath)
    nframe = 3
    frame = anim[:, anim.shape[0] * nframe: anim.shape[0] * (nframe+1) , :]

    return frame

def image_to_texture(frame):
    """
    Convert a NumPy array (frame) to a Kivy Texture using skimage.
    """
    # Ensure the frame is in RGBA format
    if frame.shape[2] == 3:  # If the image has 3 channels (RGB)
        alpha_channel = np.ones((frame.shape[0], frame.shape[1], 1), dtype=np.uint8) * 255  # Fully opaque
        frame_rgba = np.concatenate((frame, alpha_channel), axis=-1)
    elif frame.shape[2] == 4:  # If the image has an alpha channel
        frame_rgb = frame[:, :, :3]  # Keep only RGB channels
        alpha_channel = np.ones((frame_rgb.shape[0], frame_rgb.shape[1], 1), dtype=np.uint8) * 255  # Fully opaque
        frame_rgba = np.concatenate((frame_rgb, alpha_channel), axis=-1)
        if (alpha_channel < 255).any():
            print("The image contains transparency.")
        else:
            print("The alpha channel exists but does not contain transparency.")

    else:
        print('Shape: ', frame.shape[2])

    upscaled_image = resize(frame_rgba, (400, 400, 4), anti_aliasing=True)

    # Convert image to 8-bit unsigned integers
    frame_ubyte = img_as_ubyte(upscaled_image)

    # Create a texture and upload data
    texture = Texture.create(size=(frame_ubyte.shape[1], frame_ubyte.shape[0]))
    texture.blit_buffer(frame_ubyte.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
    texture.flip_vertical()
    return texture

class EachOption(Button):
    def __init__(self, text, val, rtl_flag=False):
        super().__init__()

        # Remove the default button background
        self.background_normal = ''  # Disable default background
        self.background_down = ''  # Disable pressed background
        self.background_color = (0, 0, 0, 0)  # Fully transparent

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
        self.font_name = FONT_HEB  # Replace with your font path
        self.font_size = 40
        self.bold = True
        self.app = App.get_running_app()

    def update_rect(self, *args):
        """Update the size and position of the rounded rectangle."""
        self.bg.size = self.size
        self.bg.pos = self.pos

    def on_release(self, *args):
        """Custom behavior on button release."""
        self.disabled = True  # Disable the button after clicking
        self.color = (0, 0, 0, 1)  # Set text color to black

        # Update the color of the persistent color instruction
        with self.canvas.before:
            if self.val:
                self.color_instruction.rgba = (0, 1, 0, 0.3)  # Green
                self.text = "Correct! %s" % self.text
                self.perf = 1
            else:
                self.color_instruction.rgba = (1, 0, 0, 0.3)  # Red
                self.text = "Incorrect! %s" % self.text
                self.perf = 0

        # Refresh the canvas
        self.canvas.ask_update()

        print('Performance:', self.perf)
        print('Mode: ', 'm'+self.app.modality)
        update_all(self.app.lipstick, self.app.lippath, self.iw, self.perf, mode='m'+self.app.modality)
        self.app.on_close()
        return self.perf

class MultipleAnswer(App):

    def __init__(self, lipstick : pd.DataFrame, lippath : str, modality : str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath
        self.modality = modality
        #self.box = BoxLayout(orientation = 'vertical') # Used this to nest grid into box
        self.grid = GridLayout(rows=2, padding=60, spacing=40,)# row_force_default=True, row_default_height=200)
        self.upperPanel = GridLayout(cols=3, padding=60, spacing=40, row_force_default=True, row_default_height=200)

    def load_question(self, question : str, rtl_flag = False):
        if rtl_flag: question = get_display(question)

        lb = Label(text='Translate: %s'%question, size_hint=(1,1), font_name=FONT_HEB, font_size=40)
        #span.add_widget(lb)
        self.grid.add_widget(lb)

        frame = show_pkm(nid=4)
        texture = image_to_texture(frame, )
        kivy_image = Image(texture=texture)#, size_hint=(0.9, 0.9))
        # kivy_image.size_hint = (1, 1) 
        self.upperPanel.add_widget(kivy_image)


    def load_options(self, question : str, answer : str, modality = ['dt', 'rt']):
        self.optMenu = GridLayout(cols=2, padding=20, spacing=10)
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        if modality == 'dt': correction = CorrectionDialog(question, answer)
        elif modality == 'rt': correction = CorrectionDialog(answer, question)

        self.giveup.bind(on_release=self.exit)

        self.optMenu.add_widget(self.giveup)
        self.optMenu.add_widget(correction)

        self.upperPanel.add_widget(self.optMenu)
        self.grid.add_widget(self.upperPanel)

    def load_answers(self, answers: dict, rtl_flag = False):
        self.listOp = []
        self.AnswerPanel = GridLayout(cols=2, padding=20, spacing=10)#, row_force_default=True, row_default_height=400)
        
        for el in answers:
            op = EachOption(el, answers[el], rtl_flag)
            self.AnswerPanel.add_widget(op)
            self.listOp.append(op)
        Window.bind(on_key_down=self._on_keyboard_handler)
        self.grid.add_widget(self.AnswerPanel)
        # self.AnswerPanel.size_hint_x = 1
        # self.AnswerPanel.size_hint_y = None
        # self.AnswerPanel.height = 100  # Optional fixed height for AnswerPanel


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
        #self.box.add_widget(self.grid)
        return self.grid

    def run(self):
        super().run()
        return daemon.BREAK

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ll', inplace=True, drop=False)

    qu, answ, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu, modality='rt')
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer(lipstick, lipstick_path, modality='rt')

    rtl = False
    if lipstick.learning_language.iloc[0] == 'iw':
        rtl = True

    MA.load_question(qu, rtl)
    MA.load_options(qu, answ, modality='dt')
    MA.load_answers(shufOpts, rtl)

    perf = MA.run()
    print(perf)
