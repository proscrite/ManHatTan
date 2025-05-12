from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.base import runTouchApp

from kivy.lang import Builder
from functools import partial
from dataclasses import dataclass

class Answer(App):
    def __init__(txt, correct):
        txt : str
        correct : bool
    def buildBtn(self):
        return Button(text=self.txt)


class MultipleAnswer(App, Answer):

    def select(self, instance, *args):
        instance.disable = True

    def correct(self, instance, *args):
        instance.text = "Correct!"

    def incorrect(self, instance, *args):
        instance.text = "Incorrect!"

    def build(self):

        self.grid = GridLayout(cols=2)
        self.lb = Label(text='Translate: Melopea', size_hint=(1,1))

        answers = {}
        #answer1 = Button(text='Drunkness')
        answer1 = Answer('Drunkness', True).btn
        answer2 = Button(text='Dog')
        answer3 = Button(text='Cat')
        answer4 = Button(text='Bord')

        self.grid.add_widget(answer1)
        self.grid.add_widget(answer2)
        self.grid.add_widget(answer3)
        self.grid.add_widget(answer4)
        self.grid.add_widget(self.lb)

        answer1.bind(on_release=partial(self.select, answer1))
        answer1.bind(on_release=partial(self.correct, answer1))

        answer2.bind(on_release=partial(self.select, answer2))
        answer2.bind(on_release=partial(self.incorrect, answer2))
        answer3.bind(on_release=partial(self.select, answer3))
        answer3.bind(on_release=partial(self.incorrect, answer3))
        answer4.bind(on_release=partial(self.select, answer4))
        answer4.bind(on_release=partial(self.incorrect, answer4))

        return self.grid



MultipleAnswer().run()
