from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.clock import Clock

from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *

def set_question(lipstick_path : str, size_head : int = 10):
    """Read lipstick head (least practiced words) and select a random question and translation
        size_head : number of options to shuffle from"""
    lips_head = pd.read_csv(lipstick_path, nrows = size_head)

    rndi = np.random.randint(0, size_head)
    qentry = lips_head.iloc[rndi]
    question, answer = qentry.lexeme_id, qentry.word_id
    return question, answer

def rnd_options(lipstick_path : str, n_options : int = 3, size_head : int = 0):
    """Pick at random n_options to set as false answers from lipstick head
        (full if size_head == 0)
        Return dict options {'word' : False}"""
    if size_head == 0:
        lips_head = pd.read_csv(lipstick_path)
        size_head = len(lips_head)
    else:
        lips_head = pd.read_csv(lipstick_path, nrows = size_head)

    options = {}
    for i in range(n_options):
        rndi = np.random.randint(0, size_head)
        rndOp = lips_head.iloc[rndi].word_id
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

def train_model():
    trainset, testset = read_data(lipstick_path, method='hlr', omit_lexemes=False)

    trainset += testset # Ignore the separation for the update

    model = SpacedRepetitionModel(method='hlr', omit_h_term=False, )
    model.train(trainset)

    print('HLR Model updated, sorting by recall probability')

    prob = pd.Series({i.index: model.predict(i)[0] for i in trainset})
    lipstick.p_pred.update(prob)

    lipstick.sort_values('p_recall', inplace=True)
    lipstick.to_csv(lipstick_path, index=False)

def update_all(word, perform):
    """Call all update functions and train hlr model"""

    print(lipstick.loc[word])
    update_performance(lipstick, word, perform)
    update_timedelta(lipstick, word)
    print('Performance and timedelta updated')
    lipstick.to_csv(lipstick_path, index=False)
    train_model()

class Option(Button):

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
        update_all(self.iw, self.perf)
        self.app.on_close()
        return self.perf


class MultipleAnswer(App):

    def __init__(self):
        App.__init__(self)
        #self.box = BoxLayout(orientation = 'vertical') # Used this to nest grid into box
        self.grid = GridLayout(cols=2)

    def load_question(self, question : str):
        lb = Label(text='Translate: %s'%question, size_hint=(1,1), )
        #span.add_widget(lb)
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        self.giveup.bind(on_release=self.exit)
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)

    def load_option(self, answers: dict):
        for el in answers:
            op = Option(el, answers[el])
            self.grid.add_widget(op)

    def exit(self, instance):
        print("break")
        App.stop(self)

    def on_close(self):
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
    lipstick.set_index('word_id', inplace=True, drop=False)

    qu, answ = set_question(lipstick_path)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path)
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer()
    MA.load_question(qu)
    MA.load_option(shufOpts)

    perf = MA.run()
    print(perf)
