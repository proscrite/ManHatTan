from mht import gui
from bidi.algorithm import get_display
from functools import partial
import sys

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'

from mht.scripts.python_scripts.update_lipstick import *
from mht.gui.formats.format_text_input import FTextInput, RTLTextInput

class CorrectionDialog(gui.Button):
    def __init__(self, word_ll, word_ul):
        self.text: str = 'Correct \ntranslation'
        self.background_color = (0.6, 0, 1, 1)
        self.word_ul: str = word_ul
        self.word_ll: str = word_ll
        self.app = gui.App.get_running_app()
        self.lipstick = self.app.lipstick
        self.lippath = self.app.lippath
        if self.lipstick.learning_language.iloc[0] == 'iw':
            self.rtl_flag = True
        else:
            self.rtl_flag = False

        super().__init__()

    def on_press(self, *args):
        layoutPop = gui.GridLayout(cols=1, padding=10)
        label = gui.Label(text='Enter corrected translation for: ' + self.word_ll, font_name=FONT_HEB)

        enter_callback = partial(self.updateCorrectedWord)

        if self.rtl_flag:
            self.word_ul_displ = get_display(self.word_ul)
            self.input = RTLTextInput(hint_text=self.word_ul_displ, multiline=False, font_name=FONT_HEB,
                                      on_text_validate=enter_callback)
        else:
            self.input = FTextInput(hint_text=self.word_ul, multiline=False, font_name=FONT_HEB,
                                    on_text_validate=enter_callback)
        enter = gui.Button(text='Enter')
        enter.bind(on_press=enter_callback)

        layoutPop.add_widget(label)
        layoutPop.add_widget(self.input)
        layoutPop.add_widget(enter)

        popCorrect = gui.Popup(content=layoutPop)
        popCorrect.open()

    def updateCorrectedWord(self, instance):
        print('Enter self.updateCorrectedWord...')
        self.lipstick.set_index('word_ll', inplace=True, drop=False)
        self.lipstick.loc[self.word_ll, 'word_ul'] = self.input.text
        print(self.lipstick.loc[self.word_ll, 'word_ul'])

        confirmPop = gui.GridLayout(cols=1, padding=10)
        twoCols1 = gui.GridLayout(cols=2)
        twoCols2 = gui.GridLayout(cols=2)

        label1 = gui.Label(text='You are about to modify the following translation:')
        lbWordLearn = gui.Button(text=self.word_ll, background_color=(0, 0, 1, 1))
        lbWordInput = gui.Button(text=self.input.text, background_color=(0, 0, 1, 1))
        twoCols1.add_widget(lbWordLearn)
        twoCols1.add_widget(lbWordInput)

        writeLip_callback = partial(self.writeLip)
        label2 = gui.Label(text='Are you sure you want to continue?')
        confirm = gui.Button(text='Confirm', on_release=self.writeLip, background_color=(0, 1, 0, 1))
        cancel = gui.Button(text='Cancel', on_release=self.app.on_close, background_color=(1, 0, 0, 1))
        twoCols2.add_widget(cancel)
        twoCols2.add_widget(confirm)

        confirmPop.add_widget(label1)
        confirmPop.add_widget(twoCols1)
        confirmPop.add_widget(label2)
        confirmPop.add_widget(twoCols2)

        popConfirm = gui.Popup(content=confirmPop)
        popConfirm.open()

    def writeLip(self, instance):
        print('Now overwriting LIPSTICK with corrected word')
        print(self.lipstick.loc[self.word_ll])
        self.lipstick.to_csv(self.lippath, index=False)
        self.app.on_close()

if __name__ == "__main__":
    lipstick_path = sys.argv[1]
    # lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    import pandas as pd
    lipstick = pd.read_csv(lipstick_path)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    qu, answ, iqu = set_question(lipstick_path, size_head=10)
    # print(lipstick.loc[qu])

    opts = rnd_options(lipstick_path, iquest=iqu, modality='rt')
    opts[answ] = True
    shufOpts = shuffle_dic(opts)

    MA = MultipleAnswer()
    MA.load_question(qu)
    MA.load_options(qu, answ)
    MA.load_answers(shufOpts)

    perf = MA.run()
    print(perf)
