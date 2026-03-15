from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button

from functools import partial

class FirstKivy(App):
    def disable(self, instance, *args):
        instance.disable = True

    def update(self, instance, *args):
        instance.text = "I am disabled!"

    def build(self):

        mybtn = Button(text="[u][color=ff0066][b]Click[/b][/color] me [i][color=ff9933]to[/i] disable[/color][/u]",
        markup=True,
        font_size='30', pos=(300,350),
        size_hint=(.25,.18))

        mybtn.bind(on_press=partial(self.disable, mybtn))
        mybtn.bind(on_press=partial(self.update, mybtn))
        return mybtn

FirstKivy().run()
