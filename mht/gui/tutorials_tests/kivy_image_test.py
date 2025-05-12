from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from functools import partial

Builder.load_string("""

<KivyButton>:
    Button:
        test: "Hello Button!"
        size_hint: .5, .5

        Image:
            source: 'third.png'
            center_x: self.parent.center_x
            center_y: self.parent.center_y

""")

class KivyButton(App, BoxLayout):
    def build(self):
        return self

KivyButton().run()
