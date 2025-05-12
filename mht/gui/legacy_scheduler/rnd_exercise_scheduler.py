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
from copy import deepcopy

import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from kivy_select_book import *
from madte import *
from kivy_multipleAnswer import *

#from marte import marte_main
#...

def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}

def init():
    global BREAK
    BREAK = True
    return BREAK


class DaemonScheduler(App):

    def __init__(self, rmin: int, lippath: str):
        App.__init__(self)
        self.lippath : str = lippath
        self.BREAK = True
        self.rmin = rmin

    def build(self):
        i = 1
        box = BoxLayout()
        #while self.BREAK:
        lipstick = pd.read_csv(self.lippath)
        lipstick.set_index('word_ul', inplace=True, drop=False)
        qu, answ, iqu = set_question(self.lippath, size_head=10)
        opts = rnd_options(self.lippath, iquest=iqu, modality='dt')
        opts[answ] = True
        shufOpts = shuffle_dic(opts)

        MA = MultipleAnswer(lipstick, self.lippath)
        MA.load_question(qu)
        MA.load_options(qu, answ, modality='dt')
        MA.load_answers(shufOpts)

        #trigger = Clock.create_trigger(MA.run(), 5)
        modality = madte_main
        #while i < 3:
            #trigger()
        schedule = Clock.schedule_once(partial(modality, self.lippath), 5)#self.rmin * 1)  # * 60 for minutes, 1 for testing
            ### Here goes modality shuffler, keep it fix for now
        i += 1
        print('Loop nr', i)
        reset()
        return box

    """def build(self):
        lippath = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
        BREAK = True
        while BREAK:
            modality = madte_main
            print('BREAK before exercise = ', BREAK)

            BREAK = modality(lippath)
            print('BREAK after exercise = ', BREAK)
            reset()
            self.on_pause()"""

    def on_pause(self):
        return True

    def clock_callback(self, dt):
        modality = madte_main
        print('BREAK before exercise = ', self.BREAK)

        self.BREAK = modality(self.lippath)
        print('BREAK after exercise = ', self.BREAK)
        reset()

def main(*args):
    rmin = int(sys.argv[1])
    SB = SelectBook()
    SB.load_books()
    lippath = SB.run()
    reset()

    DS = DaemonScheduler(rmin=rmin, lippath=lippath)
    DS.run()

if __name__ == "__main__":
    init()
    main(sys.argv[1])
