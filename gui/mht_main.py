"""
ManHatTan_main.py
---------------
This file combines the functionality of the two separate Kivy apps (kivy_writeInput.py and kivy_multipleAnswer.py)
into one application with multiple screens. One screen handles free text input (“Write Input”) and the other provides
multiple choice options (“Multiple Answer”). A main menu lets the user choose which exercise to run.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Import dependencies from your modules (adjust the paths if necessary)

from common import set_question, load_lipstick
from screen_multipleAnswer import MultipleAnswerScreen
from screen_writeInput import WriteInputScreen
from add_correctButton import CorrectionDialog
from duolingo_hlr import *            # your module
from update_lipstick import update_all
from bidi.algorithm import get_display

# Define common constants (adjust as needed)
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
LIPSTICK_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db_team.lip'
# mht_main.py

class MainMenuScreen(Screen):
    def __init__(self, lipstick_path, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        self.lipstick_path = lipstick_path
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        btn_write = Button(text="Write Input Exercise", font_size=40)
        btn_multi = Button(text="Multiple Answer Exercise", font_size=40)
        btn_write.bind(on_release=self.go_to_write)
        btn_multi.bind(on_release=self.go_to_multi)
        layout.add_widget(btn_write)
        layout.add_widget(btn_multi)
        self.add_widget(layout)
    
    def go_to_write(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "write_input"
    
    def go_to_multi(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "multiple_answer"

class ManHatTan(App):
    def __init__(self, lippath : str = LIPSTICK_PATH, modality : str = 'dt'):
        self.flag_refresh = True
        App.__init__(self)

    def build(self):
        self.lippath = LIPSTICK_PATH
        self.modality = 'dt'
        self.lipstick = load_lipstick(self.lippath, self.modality)
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        if self.flag_refresh:
            self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
            self.flag_refresh = False
        
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(self.lippath, name="main_menu"))
        sm.add_widget(WriteInputScreen(self.lippath, modality='dt', name="write_input"))
        sm.add_widget(MultipleAnswerScreen(self.lippath, modality='rt', name="multiple_answer"))
        sm.current = "main_menu"
        return sm

    def run(self):
        super().run()

if __name__ == '__main__':
    ManHatTan().run()
