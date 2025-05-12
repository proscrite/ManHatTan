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

import kivy.core.window as window
from kivy.base import EventLoop
from kivy.cache import Cache

from functools import partial
from time import sleep
from copy import deepcopy

import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from kivy_select_book import *
from madte import *
#from marte import marte_main
#...

def reset():
    if not EventLoop.event_listeners:
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
        trigger = Clock.create_trigger(self.clock_callback, 5)

        while i < 3:
            trigger()
            #schedule = Clock.schedule_once(self.clock_callback, 5)#self.rmin * 1)  # * 60 for minutes, 1 for testing
            ### Here goes modality shuffler, keep it fix for now
            i += 1
            print('Loop nr', i)

        return box

    def clock_callback(self, dt):
        modality = madte_main
        print('BREAK before exercise = ', self.BREAK)

        self.BREAK = modality(self.lippath)
        print('BREAK after exercise = ', self.BREAK)
        reset()

def main(*args):
    rmin = int(sys.argv[1])
    """SB = SelectBook()
    SB.load_books()
    lippath = SB.run()
    reset()"""
    lippath = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
    BREAK = True
    while BREAK:
        modality = madte_main
        print('BREAK before exercise = ', BREAK)

        BREAK = modality(lippath)
        print('BREAK after exercise = ', BREAK)
        reset()
        sleep(rmin)

if __name__ == "__main__":
    init()
    main(sys.argv[1])
