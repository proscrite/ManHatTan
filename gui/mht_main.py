"""
ManHatTan_main.py
---------------
This file combines the functionality of the two separate Kivy apps (kivy_writeInput.py and kivy_multipleAnswer.py)
into one application with multiple screens. One screen handles free text input (“Write Input”) and the other provides
multiple choice options (“Multiple Answer”). A main menu lets the user choose which exercise to run.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Import dependencies from your modules (adjust the paths if necessary)

from screen_multipleAnswer import MultipleAnswerScreen
from screen_writeInput import WriteInputScreen
from add_correctButton import CorrectionDialog
from plot_pkmn_panel import FigureCanvasKivyAgg, draw_health_bar, load_pkmn_stats
from duolingo_hlr import *            # your module
from update_lipstick import update_all
from kivy_multipleAnswer import set_question, rnd_options, shuffle_dic
from bidi.algorithm import get_display

# Define common constants (adjust as needed)
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
LIPSTICK_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db_team.lip'


# --- Main Menu Screen ---
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        btn_write = Button(text="Write Input Exercise", font_size=40)
        btn_multi = Button(text="Multiple Answer Exercise", font_size=40)
        
        btn_write.bind(on_release=self.go_to_write_input)
        btn_multi.bind(on_release=self.go_to_multiple_answer)
        
        layout.add_widget(btn_write)
        layout.add_widget(btn_multi)
        self.add_widget(layout)

    def go_to_write_input(self, instance):
        self.manager.current = "write_input"

    def go_to_multiple_answer(self, instance):
        self.manager.current = "multiple_answer"

# --- Unified App with ScreenManager ---
class ManHatTan(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main_menu"))
        sm.add_widget(WriteInputScreen(name="write_input", lipstick_path=LIPSTICK_PATH))
        sm.add_widget(MultipleAnswerScreen(name="multiple_answer", lipstick_path=LIPSTICK_PATH))
        return sm


if __name__ == '__main__':
    ManHatTan().run()
