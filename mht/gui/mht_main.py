"""
ManHatTan_main.py
---------------
This file combines the functionality of the two separate Kivy apps (kivy_writeInput.py and kivy_multipleAnswer.py)
into one application with multiple screens. One screen handles free text input (“Write Input”) and the other provides
multiple choice options (“Multiple Answer”). A main menu lets the user choose which exercise to run.
"""
import os
import logging
from functools import partial
import random
import logging

from mht import gui

from mht.gui.common import *
from mht.scripts.ML_duolingo.duolingo_hlr import *
from mht.scripts.python_scripts.update_lipstick import rebag_team
from mht.gui.config_utils import set_logging_and_kivy_config
set_logging_and_kivy_config(verbose=False)

# mht_main.py
class MainMenuScreen(gui.Screen):
    def __init__(self, lipstick_path, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        self.lipstick_path = lipstick_path
        self.app = gui.App.get_running_app()
        self.layout = gui.BoxLayout(orientation='vertical', padding=20, spacing=20, minimum_width=1000)

        self._add_main_buttons()
        self._add_lower_panel()

        self.add_widget(self.layout)

    def _add_main_buttons(self):
        self.main_panel = gui.BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.7)

        # Change to GridLayout with 2 columns
        button_panel = gui.GridLayout(cols=2, spacing=20, size_hint_x=0.75)
        
        btn_book = gui.Button(
            text="[b]Add or update words[/b]\n[i][size=24]Process book or csv databases[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.9, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_team = gui.Button(
            text="[b]View team[/b]\n[i][size=20]See your current team[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.0, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        btn_write = gui.Button(
            text="[b]Write Input Exercise[/b]\n[i][size=20]Type your answer in free text[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.2, 0.5, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        btn_multi = gui.Button(
            text="[b]Multiple Answer Exercise[/b]\n[i][size=20]Choose the correct answer[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.9, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_conj = gui.Button(
            text="[b]Conjugation Exercise[/b]\n[i][size=20]Practice Hebrew verb conjugation[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.2, 0.8, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        btn_claw = gui.Button(
            text="[b]Cloze GPT Exercise[/b]\n[i][size=20]Fill in the blank using AI-generated sentences[/size][/i]",
            font_size=40,
            markup=True,
            background_color=(0.7, 0.3, 0.8, 1),  # Example: purple shade
            color=(1, 1, 1, 1)
        )

        btn_book.bind(on_release=self.go_to_process_book)
        btn_team.bind(on_release=self.view_team)
        btn_write.bind(on_release=partial(self.go_to_exercise, screen_name="write_input"))
        btn_multi.bind(on_release=partial(self.go_to_exercise, screen_name="multiple_answer"))
        btn_conj.bind(on_release=self.go_to_conjugation)
        btn_claw.bind(on_release=self.go_to_claw)

        # Add buttons to grid (order as you prefer)
        button_panel.add_widget(btn_book)
        button_panel.add_widget(btn_write)
        button_panel.add_widget(btn_multi)
        button_panel.add_widget(btn_conj)
        button_panel.add_widget(btn_team)
        button_panel.add_widget(btn_claw)

        logo = gui.Image(
            source="/Users/pabloherrero/Documents/ManHatTan/mht/gui/icons/mascott_v3.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=0.25,
            size_hint_y=1
        )

        self.main_panel.add_widget(button_panel)
        self.main_panel.add_widget(logo)

        self.layout.add_widget(self.main_panel)

    def _get_logo_widget(self, rowspan=3):
        return gui.Image(
            source="/Users/pabloherrero/Documents/ManHatTan/mht/gui/icons/mascott_v3.png",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.25, rowspan)
        )

    def _add_lower_panel(self):
        self.learning_language = self.app.lipstick['learning_language'].iloc[0]
        self.ui_language = self.app.lipstick['ui_language'].iloc[0]
        print(f'learning_language = {self.learning_language}, ui_language = {self.ui_language}')
        features = self.app.lipstick.columns
        print(f'Features: {features}')

        self.dropdown = gui.DropDown()
        item_dt = gui.Button(text=language_dict[self.ui_language], size_hint_y=None, height=84)
        item_rt = gui.Button(text=language_dict[self.learning_language], size_hint_y=None, height=84)
        item_random = gui.Button(text="Random", size_hint_y=None, height=84)
        item_dt.bind(on_release=partial(self.set_modality, modality='dt'))
        item_rt.bind(on_release=partial(self.set_modality, modality='rt'))
        item_random.bind(on_release=partial(self.set_modality, modality='random'))
        self.dropdown.add_widget(item_dt)
        self.dropdown.add_widget(item_rt)
        self.dropdown.add_widget(item_random)

        lower_panel = gui.GridLayout(cols=3, size_hint_y=0.2, minimum_width=5000)
        self.dropdown_button = gui.Button(
            text='Exercise Language: Random',
            size_hint=(0.75, 0.3), background_color=(0.5, 0.2, 0.7, 1), color=(1, 1, 1, 1)
        )
        self.dropdown_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.dropdown_button, 'text', x))
        lower_panel.add_widget(self.dropdown_button)

        settings_button = gui.Button(
            text='Settings', on_release=self.open_settings,
            size_hint=(0.75, 0.3), background_color=(0.3, 0.3, 0.8, 1), color=(1, 1, 1, 1),
        )
        lower_panel.add_widget(settings_button)

        exit_button = gui.Button(
            text='Exit', on_release=self.exit,
            size_hint=(0.75, 0.3), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1),
        )
        lower_panel.add_widget(exit_button)
        self.layout.add_widget(lower_panel)

    # Placeholder for settings callback
    def open_settings(self, instance):
        self.manager.transition = gui.SlideTransition(direction="left")
        self.manager.current = "settings"

    def go_to_exercise(self, instance, screen_name):
        modality = self.app.modality
        if modality == 'random':
            modality = random.choice(['dt', 'rt'])
        screen = self.manager.get_screen(screen_name)
        screen.modality = modality
        self.manager.transition = gui.SlideTransition(direction="left")
        self.manager.current = screen_name

    def go_to_conjugation(self, instance):
        self.manager.transition = gui.SlideTransition(direction="left")
        self.manager.current = "conjugation"

    def go_to_claw(self, instance):
        if not self.manager.has_screen("claw"):
            from mht.gui.screen_claw import ClawScreen  # Import here to avoid loading at startup
            claw_screen = ClawScreen(self.lipstick_path, modality='rt', name="claw")
            self.manager.add_widget(claw_screen)
        self.manager.transition = gui.SlideTransition(direction="left")
        self.manager.current = "claw"

    def go_to_process_book(self, instance):
        self.manager.transition = gui.SlideTransition(direction="left" )
        
        # Remove old choose_color screen if it exists
        if self.manager.has_screen('process_book'):
            self.manager.remove_widget(self.manager.get_screen('process_book'))

        self.manager.add_widget(
            gui.SelectBookScreen(name='process_book')
        )
        self.manager.current = "process_book"

    def view_team(self, instance):
        self.manager.transition = gui.SlideTransition(direction="left")
        self.manager.current = "team"
    
    def set_modality(self, instance, modality):
        self.app.modality = modality
        self.dropdown_button.text = 'Exercise Language: ' + instance.text
        self.dropdown_button.font_name = instance.font_name  # Use the same font as the selected item
        self.dropdown.dismiss()

    def exit(self, instance):
        print('Exiting')
        self.app.stop(self)

class MhtScreenManager(gui.ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shared_data = {}  # Dict to pass data between screens


class ManHatTan(gui.App):
    def __init__(self, lippath : str = LIPSTICK_PATH, modality : str = 'random'):
        self.flag_refresh = True
        self.modality = modality

        gui.App.__init__(self)

    def init_rebag(self):
        print('Init rebag...')
        new_team_screen = gui.TeamScreen(name='init_team', team_lip=self.team_lip, buttons_active=False)
        self.sm.add_widget(new_team_screen)
        self.sm.current = 'init_team'
        self.sm.transition = gui.SlideTransition(direction="right")

    def continue_rebag_team(self):
        self.team_lip = load_lipstick(self.teamlippath, self.modality)   # Reload the team_lip after updating eligibility
        print('Continue rebagging team...')
        print(f"Current team: {self.team_lip}")

        new_team = rebag_team(self.team_lip, self.teamlippath)
        self.team_lip = new_team
        print(f"New team: {new_team}")
        if new_team is 0:
            print('Rebagging is not needed yet')
            self.sm.current = 'main_menu'
            self.sm.remove_widget(self.sm.get_screen('new_team'))
        else:
            # Update the screen with the gui.new team
            self.team_lip.to_csv(self.tgui.eamlippath, index=False)
            new_team_screen = gui.TeamScreen(name='new_team', team_lip=new_team, buttons_active=False)
            self.sm.remove_widget(self.sm.get_screen('init_team'))
            self.sm.add_widget(new_team_screen)
            self.sm.current = 'new_team'
            self.sm.transition = gui.SlideTransition(direction="right")

    def build(self):
        self.teamlippath = TEAM_LIP_PATH
        self.lippath = LIPSTICK_PATH
        self.lipstick = load_lipstick(self.lippath, self.modality)
        self.team_lip = load_lipstick(self.teamlippath, self.modality)
        self.rtl_flag = (self.team_lip.learning_language.iloc[0] == 'iw')
        if self.flag_refresh:
            self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.teamlippath)
            self.flag_refresh = False
        
        self.sm = MhtScreenManager()
        self.sm.add_widget(MainMenuScreen(self.teamlippath, name="main_menu"))
        self.sm.add_widget(gui.WriteInputScreen(self.teamlippath, modality=self.modality, name="write_input"))
        self.sm.add_widget(gui.MultipleAnswerScreen(self.teamlippath, modality=self.modality, name="multiple_answer"))
        self.sm.add_widget(gui.ConjugationScreen(self.lippath, modality='dt', name="conjugation"))
        self.sm.add_widget(gui.TeamScreen(name='team', team_lip=self.team_lip, buttons_active=True))
        self.sm.add_widget(gui.SettingsScreen(name='settings', lipstick_path=self.lippath, team_lip_path=self.teamlippath))

        self.sm.current = "main_menu"
        return self.sm

    def run(self):
        super().run()

if __name__ == '__main__':
    ManHatTan().run()