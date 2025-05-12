"""
ManHatTan_main.py
---------------
This file combines the functionality of the two separate Kivy apps (kivy_writeInput.py and kivy_multipleAnswer.py)
into one application with multiple screens. One screen handles free text input (“Write Input”) and the other provides
multiple choice options (“Multiple Answer”). A main menu lets the user choose which exercise to run.
"""
import os
os.environ["KIVY_NO_FILELOG"] = "1"

from kivy.config import Config
# Increase window width by 20%
orig_width = Config.getint('graphics', 'width')
print('Orig_width = ', orig_width)
# new_width = int(orig_width * 1.9)
Config.set('graphics', 'width', str(800))

# Set window position to custom and force it to the upper left
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', '0')
Config.set('graphics', 'top', '0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.logger import Logger as kvLogger
import logging
kvLogger.setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Import dependencies from your modules (adjust the paths if necessary)

from mht.gui.common import set_question, load_lipstick
from mht.gui.screen_writeInput import WriteInputScreen
from mht.gui.screen_multipleAnswer import MultipleAnswerScreen
from mht.gui.team_manager import ShowTeamScreen
from mht.gui.add_correctButton import CorrectionDialog

from mht.scripts.ML_duolingo.duolingo_hlr import *
from mht.scripts.python_scripts.update_lipstick import update_all
from bidi.algorithm import get_display

# Define common constants (adjust as needed)
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
LIPSTICK_PATH = ROOT_PATH + '/data/processed/LIPSTICK/hebrew_db.lip'
TEAM_LIP_PATH = LIPSTICK_PATH.replace('.lip', '_team.lip')

font_path = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
print(f"[DEBUG] Looking for font at: {font_path!r}")
print(f"[DEBUG] Exists? {os.path.exists(font_path)}")

# mht_main.py
class MainMenuScreen(Screen):
    def __init__(self, lipstick_path, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        self.lipstick_path = lipstick_path
        self.app = App.get_running_app()
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20, minimum_width = 1000)
        btn_write = Button(text="Write Input Exercise", font_size=40)
        btn_multi = Button(text="Multiple Answer Exercise", font_size=40)
        btn_write.bind(on_release=self.go_to_write)
        btn_multi.bind(on_release=self.go_to_multi)

        self.layout.add_widget(btn_write)
        self.layout.add_widget(btn_multi)
                
        self.learning_language = self.app.lipstick['learning_language'][0]
        self.ui_language = self.app.lipstick['ui_language'][0]
        print(f'learning_language = {self.learning_language}, ui_language = {self.ui_language}')
        features = self.app.lipstick.columns
        print(f'Features: {features}')

        # Create the dropdown and keep a reference
        self.dropdown = DropDown()
        item_dt = Button(text=self.ui_language, size_hint_y=None, height=84)
        item_rt = Button(text=self.learning_language, size_hint_y=None, height=84)
        item_dt.bind(on_release=self.set_modality_dt)
        item_rt.bind(on_release=self.set_modality_rt)
        self.dropdown.add_widget(item_dt)
        self.dropdown.add_widget(item_rt)

        lower_panel = GridLayout(cols=3, size_hint_y=0.2, minimum_width = 5000)
        self.dropdown_button = Button(text='Exercise Language', size_hint=(0.5, 0.3))
        self.dropdown_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.dropdown_button, 'text', x))
        lower_panel.add_widget(self.dropdown_button)

        team_button = Button(text='View team', size_hint=(0.5, 0.3), on_release=self.view_team)
        lower_panel.add_widget(team_button)
        exit_button = Button(text='Exit', size_hint=(0.5, 0.3), on_release=self.exit)
        lower_panel.add_widget(exit_button)
        self.layout.add_widget(lower_panel)
        self.add_widget(self.layout)
    
    def go_to_write(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "write_input"
    
    def go_to_multi(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "multiple_answer"

    def view_team(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "view_team"

    def set_modality_dt(self, instance):
        self.app.modality = 'dt'
        setattr(self.dropdown_button, 'text', 'Exercise Language: ' + instance.text)

    def set_modality_rt(self, instance):
        self.app.modality = 'rt'
        setattr(self.dropdown_button, 'text', 'Exercise Language: ' + instance.text)

    def exit(self, instance):
        print('Exiting')
        self.app.stop(self)

class ManHatTan(App):
    def __init__(self, lippath : str = LIPSTICK_PATH, modality : str = 'dt'):
        self.flag_refresh = True
        self.modality = modality

        App.__init__(self)

    def build(self):
        self.teamlippath = TEAM_LIP_PATH
        self.lippath = LIPSTICK_PATH
        self.lipstick = load_lipstick(self.teamlippath, self.modality)
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        if self.flag_refresh:
            self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.teamlippath, self.rtl_flag, size_head=6)
            self.flag_refresh = False
        
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(self.teamlippath, name="main_menu"))
        sm.add_widget(WriteInputScreen(self.teamlippath, modality='dt', name="write_input"))
        sm.add_widget(MultipleAnswerScreen(self.teamlippath, modality='rt', name="multiple_answer"))
        sm.add_widget(ShowTeamScreen(name="view_team", team_lip=self.lipstick, end_flag=True) )

        sm.current = "main_menu"
        return sm

    def run(self):
        super().run()

if __name__ == '__main__':
    ManHatTan().run()