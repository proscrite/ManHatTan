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

def main(*args):
    SB = SelectBook()
    SB.load_books()

    lippath = SB.run()

    rmin = int(sys.argv[1])

    BREAK = True
    while BREAK:
        sleep(rmin * 1)  # * 60 for minutes, 1 for testing
        ### Here goes modality shuffler, keep it fix for now
        reset()
        modality = madte_main
        print('BREAK before exercise = ', BREAK)

        modality(lippath)
        print('BREAK after exercise = ', BREAK)

if __name__ == "__main__":
    init()
    main(sys.argv[1])
