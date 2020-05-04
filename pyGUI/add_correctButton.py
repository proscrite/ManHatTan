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
from kivy.clock import Clock

from functools import partial
from time import sleep
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import FTextInput


class CorrectionDialog(Button):
    def __init__(self, word_ll, word_ul):
        self.text : str = 'Correct translation'
        self.background_color = (0.6, 0, 1, 1)
        self.word_ul : str = word_ul
        self.word_ll : str = word_ll
        self.app= App.get_running_app()
        self.lipstick = self.app.lipstick
        self.lippath = self.app.lippath
        super().__init__()

    def on_press(self, *args):
        layoutPop = GridLayout(cols=1, padding = 10)
        label = Label(text='Enter corrected translation for: '+self.word_ll)

        enter_callback = partial(self.updateCorrectedWord)

        self.input = FTextInput(hint_text=self.word_ul, multiline=False,
            on_text_validate=enter_callback)
        enter = Button(text='Enter')

        enter.bind(on_press=enter_callback)

        layoutPop.add_widget(label)
        layoutPop.add_widget(self.input)
        layoutPop.add_widget(enter)

        popCorrect = Popup(content=layoutPop)
        popCorrect.open()

    def updateCorrectedWord(self, instance):
        print('Enter self.updateCorrectedWord...')

        #for k,v in dictCorrect.items():
        #    print('k: {}, v:{}'.format(k,v))
        self.lipstick.set_index('word_ll', inplace=True, drop=False)
        self.lipstick.loc[self.word_ll, 'word_ul'] = self.input.text
        print(self.lipstick.loc[self.word_ll, 'word_ul'])

        confirmPop = GridLayout(cols=1, padding=10)
        twoCols1 = GridLayout(cols=2)
        twoCols2 = GridLayout(cols=2)

        label1 = Label(text='You are about to modify the following translation:')
        lbWordLearn = Button(text=self.word_ll, background_color=(0, 0, 1, 1))
        lbWordInput = Button(text=self.input.text, background_color=(0, 0, 1, 1))
        twoCols1.add_widget(lbWordLearn)
        twoCols1.add_widget(lbWordInput)

        writeLip_callback = partial(self.writeLip)
        label2 = Label(text='Are you sure you want to continue?')
        confirm = Button(text='Confirm', on_release=self.writeLip, background_color=(0,1,0,1))
        cancel = Button(text='Cancel', on_release=self.app.on_close, background_color=(1,0,0,1))
        twoCols2.add_widget(cancel)
        twoCols2.add_widget(confirm)

        confirmPop.add_widget(label1)
        confirmPop.add_widget(twoCols1)
        confirmPop.add_widget(label2)
        confirmPop.add_widget(twoCols2)

        popConfirm = Popup(content=confirmPop)
        popConfirm.open()

    def writeLip(self,instance):
        print('Now overwriting LIPSTICK with corrected word')
        print(self.lipstick.loc[self.word_ll])
        self.lipstick.to_csv(self.lippath, index=False)
        self.app.on_close()

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    qu, answ, iqu = set_question(lipstick_path, size_head=10)
    #print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu, modality='rt')
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer()
    MA.load_question(qu)
    MA.load_options(qu, answ)
    MA.load_answers(shufOpts)

    perf = MA.run()
    print(perf)
