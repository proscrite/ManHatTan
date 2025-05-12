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
from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from functools import partial
from time import sleep

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import sys
sys.path.append('../python_scripts/')
sys.path.append('../ML')

from update_lipstick import *
from duolingo_hlr import *
from kivy_multipleAnswer import *

root = Builder.load_string(r"""
<OrangeWidget>


<OrangeGraphicWidget>

    canvas:
        Color:
            rgba: 1, .5, 0, 1

        Rectangle:
            pos: self.center_x - 15, 20
            size: 30, self.height - (self.height / 10)

    Button:
        text: "Button 1"
        pos: root.pos
        size_hint: (None, None)

    Button:
        text: "Button 2"
        pos_hint: {'center_x': .5, 'center_y': .95}
        size_hint: (None, None)
""")

class OrangeWidget(Screen):
    def __init__(self, **kwargs):
        super(OrangeWidget, self).__init__(**kwargs)


        scrollView = ScrollView(size_hint=(1, 1))


        # add custom widget into that layout
        customWidget = OrangeGraphicWidget(height=1200, size_hint_y=None)


        scrollView.add_widget(customWidget)

        self.add_widget(scrollView)

class OrangeGraphicWidget(RelativeLayout):
    pass

class ProgressChart(App):
    def build(self):
        return OrangeWidget()
#runTouchApp(root)
ProgressChart().run()
