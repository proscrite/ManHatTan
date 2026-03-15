from kivy import Config
Config.set('kivy', 'text', 'pango')
from kivy.app import App
from kivy.uix.label import Label

class T(App):
    def build(self):
        return Label(text="שלום", font_size=72)
T().run()