from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.base import runTouchApp, stopTouchApp

from kivy.clock import Clock

from glob import glob
from time import sleep
import os
import sys

class BookButton(Button):

    def __init__(self, filename, path):
        self.text : str = filename
        self.path : str = path
        self.app = App.get_running_app()
        super().__init__()

    def on_release(self, *args):
        self.disable = True
        self.text = 'Selected'
        self.app.set_path(self.path)
        print(self.app.path)
        stopTouchApp()
        return self.path

class SelectBook(App):

    def __init__(self):
        App.__init__(self)
        self.grid = GridLayout(cols=2)
        self.path : str

    def load_books(self):
        lipsticks = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/*'
        books_full = glob(lipsticks)
        books = {}
        for b in books_full:
            dirpath, filename = os.path.split(b)
            filename = os.path.splitext(filename)[0]
            books[filename] = b

            op = BookButton(filename, b)
            #op = Button(text=filename, on_release=self.return_path(b))
            self.grid.add_widget(op)

    def set_path(self, path):
        self.path = path

    def build(self):
        lb = Label(text='Select book to practice:', size_hint=(1,1))
        self.giveup = Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        self.giveup.bind(on_release=self.exit)
        self.grid.add_widget(lb)
        self.grid.add_widget(self.giveup)
        return self.grid

    def run(self):
        super().run()
        return self.path

    def exit(self, instance):
        print("break")
        App.stop(self)

if __name__ == "__main__":
    #lipstick_path = sys.argv[1]

    SB = SelectBook()
    SB.load_books()

    path = SB.run()
