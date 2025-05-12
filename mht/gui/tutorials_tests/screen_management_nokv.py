from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)


class testW(Screen):
    def __init__(self, **kwargs):
        super(testW, self).__init__()

class emotionRecog(Screen):
    def __init__(self, **kwargs):
        super(emotionRecog, self).__init__(**kwargs)
        self.button1 = Button(text="Next", size_hint=(1, .1))
        self.button1.bind(on_press=self.screenTransition)
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(self.button1)

    def screenTransition(self, *args):
        self.manager.current = 'test'


class CamApp(App):
    def build(self):
        sm = ScreenManagement()
        sm.add_widget(emotionRecog(name='emotion'))
        sm.add_widget(testW(name='test'))
        return sm


if __name__ == "__main__":
    CamApp().run()