from kivy.app import App
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner

from kivy_multipleAnswer import FTextInput
from kivy_select_book import BookButton

from glob import glob
import os

Builder.load_string("""
<ColDropDown>:
    #on_parent: self.dismiss()
    #on_select: btn.text = '{}'.format(args[1])
""")

class ManhattanMain(App):
    def __init__(self, rootdir: str):
        App.__init__(self)
        self.grid = GridLayout(cols=2)
        self.currentBook: str
        self.rootdir = rootdir

    def load_books(self):
        books_full = glob(self.rootdir)
        books = {}
        for b in books_full:
            dirpath, filename = os.path.split(b)
            filename = os.path.splitext(filename)[0]
            books[filename] = b
        books['Add new book'] = self.rootdir
        return books

    def build(self):
        books = self.load_books()
        practiceNow = Button(text='Practice Now!', background_color=(0, 1, 0,1), font_size= "20dp")
        manageWords = Button(text='Manage entries', background_color=(0, 0.2, 0.8,1), font_size= "15dp")
        self.selectBook  = Spinner(text='Current book:',
                               values= books,
                               size_hint=(1, None),
                               height="100sp",
                               pos_hint={'center_x': .5, 'center_y': .5})
        remainderSett = Button(text='Remainder settings', background_color=(0.1, 0.1, 0.1, 1), font_size="15dp")

        box1 = BoxLayout()
        box1.add_widget(practiceNow)

        grid2 = GridLayout(cols=1)
        for wg in [self.selectBook, manageWords, remainderSett]:
            grid2.add_widget(wg)

        self.grid.add_widget(box1)
        self.grid.add_widget(grid2)
        return self.grid


if __name__ == '__main__':
    rootdir = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/*'
    MM = ManhattanMain(rootdir)
    MM.run()
