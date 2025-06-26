# --- Write Input Screen (refactored from kivy_writeInput.py) --- #
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from functools import partial
import time

import matplotlib.pyplot as plt
from bidi.algorithm import get_display

# Import common functionality and constants
from mht.gui.common import *
from mht.scripts.python_scripts.update_lipstick import update_all

from mht.gui.formats.format_text_input import FTextInput, RTLTextInput
from mht.gui.screen_BaseExercise import BaseExerciseScreen
from mht.gui.add_correctButton import CorrectionDialog

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'


class WriteInputScreen(BaseExerciseScreen):
    def __init__(self, lipstick_path, modality='dt', **kwargs):
        super(WriteInputScreen, self).__init__(lipstick_path, modality, **kwargs)
        self.app = App.get_running_app()

    def build_ui(self):
        self.clear_widgets()
        # Create a horizontal layout that splits the animated panel and the input/options
        self.box = BoxLayout(orientation='horizontal')
        self.InputPanel = GridLayout(cols=1, rows=2, size_hint=(0.8, 1),
                                       padding=20, spacing=20)
        self.optMenu = GridLayout(cols=1, rows=3, size_hint=(0.2, 1),
                                  padding=20, spacing=20)
        
        # Now animated_container is guaranteed to exist
        self.InputPanel.add_widget(self.animated_container)
        
        input_callback = partial(self.checkAnswer)
        # Add text input
        if self.rtl_flag:
            self.input = RTLTextInput(hint_text='Write here', multiline=False, font_name = FONT_HEB,
                                       on_text_validate=input_callback, font_size=40, background_color=(0.9,0.9,0.9,1),
                                       pos_hint={"center_x": 0.5, "center_y": 0.5}, center_y=0.5, halign="center",)
        else:
            self.input = FTextInput(hint_text='Write here', multiline=False, font_name = FONT_HEB, 
                                    on_text_validate=input_callback, font_size=40, background_color=(0.9,0.9,0.9,1),
                                    pos_hint={"center_x": 0.5, "center_y": 0.5}, center_y=0.5, halign="center",)
        
        self.InputPanel.add_widget(self.input)
        
        # Create buttons for the options menu
        input_callback = partial(self.checkAnswer)
        enter_btn = Button(text='Enter', on_release=input_callback,
                           size_hint=(0.5, 1))
        self.optMenu.add_widget(enter_btn)
        exit_btn = Button(text='Exit', on_release=self.go_back,
                          size_hint=(0.5, 1))
        self.optMenu.add_widget(exit_btn)
        back_btn = Button(text="Back to Menu", on_release=self.go_back,
                          size_hint=(0.5, 1))
        self.optMenu.add_widget(back_btn)
        
        self.box.add_widget(self.InputPanel)
        self.box.add_widget(self.optMenu)
        self.add_widget(self.box)
        
        Clock.schedule_interval(self.update, 1/30)
        Window.bind(on_key_down=self._on_keyboard_handler)
        print('WriteInputScreen initialized with modality:', self.modality)
    
    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        if keycode == 40:  # Enter key
            self.checkAnswer(None)
    
    def checkAnswer(self, instance):
        # Dismiss an existing popup if it exists.
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        elapsed_time = time.time() - self.start_time
        self.speed = 1 / elapsed_time

        # Create a fresh layout for the popup.
        layout = GridLayout(cols=2, padding=10)
        label = Button(text='Exercise: ' + self.question_displ, font_name=FONT_HEB, 
                    font_size=40, bold=True, size_hint=(2, 1))
        layout.add_widget(label)

        # Always create a new CorrectionDialog instance.
        correction = CorrectionDialog(self.question_displ, self.answer)
        # If by any chance correction already has a parent, remove it.
        if correction.parent:
            correction.parent.remove_widget(correction)
        layout.add_widget(correction)
        
        if self.rtl_flag:
            input_answer = get_display(self.input.text)
        else:
            input_answer = strip_accents(self.input.text.lower())
            self.answer = strip_accents(self.answer.lower())
        
        if self.answer == input_answer:
            result_btn = Button(text='Correct! ' + self.answer_displ,
                                font_size=40, size_hint=(2, 1),
                                background_color=(0, 1, 0, 1))
            self.perf = 1
        else:
            result_btn = Button(text=self.input.text + ': Incorrect! ' + self.answer_displ,
                                font_size=40, size_hint=(2, 1),
                                background_color=(1, 0, 0, 1))
            self.perf = 0
        layout.add_widget(result_btn)
        
        cont_btn = Button(text='Continue', on_release=self.on_close,
                          size_hint=(0.5, 1), background_color=(1, 1, 0, 1))
        layout.add_widget(cont_btn)
        
        self.answer_popup = Popup(content=layout)
        self.answer_popup.open()
    
    def on_close(self, *args):
        flag_rebag = update_all(self.lipstick, self.lippath, self.word_ul, self.perf,
                   self.speed, mode='w' + self.modality)
        
        if hasattr(self, 'answer_popup'):
            self.answer_popup.dismiss()
            
        if flag_rebag:
            print('Rebagging team...')
            self.app.init_rebag()
        else:
            current_name = self.name
            self.go_back(current_name)
    
    def on_leave(self, *args):
        self.clear_widgets()
        self.built = False
        # Unschedule updates
        Clock.unschedule(self.update)
        # Unbind keyboard
        Window.unbind(on_key_down=self._on_keyboard_handler)
        # Dismiss popups
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

