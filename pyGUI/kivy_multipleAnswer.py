from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

from kivy.clock import Clock

from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from add_correctButton import *
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
    lipstick.p_pred.update(prob)

    lipstick.sort_values('p_recall', inplace=True)
    lipstick.to_csv(lipstick_path, index=False)

def update_all(lipstick : pd.DataFrame, lipstick_path : str, word : str, perform):
    """Call all update functions and train hlr model"""

    update_performance(lipstick, word, perform)
    update_timedelta(lipstick, word)

    print('Performance and timedelta updated')
    print(lipstick.loc[word])
    lipstick.to_csv(lipstick_path, index=False)
    train_model(lipstick, lipstick_path)

class EachOption(Button):

    def __init__(self, text, val):
        self.text : str = text
        self.val : bool = val
        self.perf : bool
        self.iw : str = text # Store variable for processing
        self.app= App.get_running_app()
        super().__init__()

    def on_release(self, *args):
        self.disable = True
        if self.val:
            self.text = "Correct!"
            self.background_color = (0, 1,0, 1)
            self.perf = 1
        else:
            self.text = "Incorrect!"
            self.background_color = (1, 0,0, 1)
            self.perf = 0
        print('Performance: ', self.perf)
        update_all(self.app.lipstick, self.app.lippath, self.iw, self.perf)
        self.app.on_close()
        return self.perf

class MultipleAnswer(App):

    def __init__(self, lipstick : pd.DataFrame, lippath : str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath
        #self.box = BoxLayout(orientation = 'vertical') # Used this to nest grid into box
        self.grid = GridLayout(cols=2)

    def load_question(self, question : str):
        lb = Label(text='Translate: %s'%question, size_hint=(1,1), )
        #span.add_widget(lb)
        self.grid.add_widget(lb)

    def load_options(self, question : str, answer : str, modality : str):
        self.optMenu = GridLayout(cols=2)
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        if modality == 'dt': correction = CorrectionDialog(question, answer)
        elif modality == 'rt': correction = CorrectionDialog(answer, question)

        self.giveup.bind(on_release=self.exit)

        self.optMenu.add_widget(self.giveup)
        self.optMenu.add_widget(correction)

        self.grid.add_widget(self.optMenu)

    def load_answers(self, answers: dict):
        self.listOp = []
        for el in answers:
            op = EachOption(el, answers[el])
            self.grid.add_widget(op)
            self.listOp.append(op)
        Window.bind(on_key_down=self._on_keyboard_handler)


    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        if keycode in range(30, 33):
            print("Keyboard pressed! {}".format(keycode))
            print('Firing option %i' %(keycode-29))
            self.listOp[keycode - 30].on_release()
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

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    qu, answ, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu)
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer(lipstick, lipstick_path)
    MA.load_question(qu)
    MA.load_options(qu, answ)
    MA.load_answers(shufOpts)

    perf = MA.run()
    print(perf)
