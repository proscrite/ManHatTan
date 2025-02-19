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
from kivy.uix.screenmanager import Screen

from kivy.clock import Clock

from functools import partial
from time import sleep
import sys
import datetime
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import FTextInput


class AddNewEntry(Screen):
    def __init__(self, **kwargs):
        #self.background_color = (0.6, 0, 1, 1)
        self.word_ul : str
        self.word_ll : str
        self.app= App.get_running_app()
        self.lipstick = self.app.lipstick
        self.lippath = self.app.lippath
        super(Screen, self).__init__()
        self.children[0].add_widget(self.build())

    def build(self, *args):
        print('entering add_dbEntry build...')
        self.layoutPop = GridLayout(cols=1, size_hint_y=None)
        grid2 = GridLayout(cols=2, size_hint_y=None)

        enter_callback = partial(self._add_entry)

        self.input_ll = FTextInput(hint_text='Enter word to learn', multiline=False,)
            #on_text_validate=enter_callback)
        self.input_ul = FTextInput(hint_text='Enter translation', multiline=False,
            on_text_validate=enter_callback)
        enter = Button(text='Enter')

        enter.bind(on_press=enter_callback)

        grid2.add_widget(self.input_ll)
        grid2.add_widget(self.input_ul)
        self.layoutPop.add_widget(grid2)

        self.layoutPop.add_widget(enter)
        return self.layoutPop

    def on_press(self, *args):
        """Deprecated, for use as popup only"""
        self.popCorrect = Popup(content=self.layoutPop, title='Enter new entry')
        self.popCorrect.open()

    def _add_entry(self, instance):
        print('Enter self.updateCorrectedWord...')
        self.lipstick = self.lipstick.append(pd.Series(0, index=self.lipstick.columns),
            ignore_index=True)

        today = int(datetime.datetime.timestamp(datetime.datetime.today()))
        self.lipstick.loc[0, 'timestamp'] = today
        self.lipstick.loc[0, 'word_ll'] = self.input_ll.text
        self.lipstick.loc[0, 'word_ul'] = self.input_ul.text

        print(self.lipstick.loc[0])
        self._confirmPop()

    def _confirmPop(self):
        confirmPop = GridLayout(cols=1, padding=10)
        twoCols1 = GridLayout(cols=2)
        twoCols2 = GridLayout(cols=2)

        label1 = Label(text='You are about to add the following translation:')
        lbWordLearn = Button(text=self.input_ll.text, background_color=(0, 0, 1, 1))
        lbWordInput = Button(text=self.input_ul.text, background_color=(0, 0, 1, 1))
        twoCols1.add_widget(lbWordLearn)
        twoCols1.add_widget(lbWordInput)

        writeLip_callback = partial(self.writeLip)
        label2 = Label(text='Are you sure you want to continue?')
        confirm = Button(text='Confirm', on_release=self.writeLip, background_color=(0,1,0,1))
        cancel = Button(text='Cancel', on_release=lambda x: self.popConfirm.dismiss(), background_color=(1,0,0,1))
        twoCols2.add_widget(cancel)
        twoCols2.add_widget(confirm)

        confirmPop.add_widget(label1)
        confirmPop.add_widget(twoCols1)
        confirmPop.add_widget(label2)
        confirmPop.add_widget(twoCols2)

        self.popConfirm = Popup(content=confirmPop)
        self.popConfirm.open()

    def writeLip(self,instance):
        print('Now overwriting LIPSTICK with corrected word')

        #self.lipstick.to_csv(self.lippath, index=False)
        self.popConfirm.dismiss()
        self.popCorrect.dismiss()

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    MA = AddNewEntry(lipstick, lipstick_path)
    MA.load_question(qu)
    MA.load_options(qu, answ, modality='rt  ')
    MA.load_answers(shufOpts)

    perf = MA.run()
    print(perf)
