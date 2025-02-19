from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.base import runTouchApp

from kivy.lang import Builder

class ClearApp(App):
    def build(self):

        self.box = BoxLayout(orientation='horizontal', spacing=20)
        self.txt = TextInput(hint_text='Write here', size_hint=(.5,.1))
        self.btn = Button(text='Clear all', on_press=self.clearText, size_hint=(.1,.1))

        self.box.add_widget(self.txt)
        self.box.add_widget(self.btn)
        return self.box

    def clearText(self, instance):
        print(self.txt.text)
        self.txt.text=''

ClearApp().run()
