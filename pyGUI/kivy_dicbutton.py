from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import sys
from time import sleep

class Option(Button):
    app= App.get_running_app()

    def __init__(self, text, val):
        self.text : str = text
        self.val : bool = val
        self.perf : bool
        super().__init__()

    def on_release(self, app, *args):
        self.disable = True
        if self.val:
            self.text = "Correct!"
            self.background_color = (0, 1,0, 1)
            self.perf = 1
        else:
            self.text = "Incorrect!"
            self.background_color = (1, 0,0, 1)
            self.perf = 0
        app.close()
        #return {self.text: self.perf}


class MultipleAnswer(App):

    def __init__(self):
        App.__init__(self)
        self.grid = GridLayout(cols=2)

    def load_option(self, answers: dict):
        for el in answers:
            op = Option(el, answers[el])
            self.grid.add_widget(op)

    def build(self):
       lb = Label(text='Translate: Melopea', size_hint=(1,1))
       self.grid.add_widget(lb)
       #self.load_option(answers)

       return self.grid

    def on_stop():
        App.stop()

answers = {'drunk': True, 'dog': False, 'cat': False}

MA = MultipleAnswer()
MA.load_option(answers)

perf = MA.run()
print(perf)
