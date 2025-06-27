from functools import partial
import time
import matplotlib.pyplot as plt
from bidi.algorithm import get_display

from mht import gui
# Import common functionality and constants
from mht.gui.common import *
from mht.scripts.python_scripts.update_lipstick import update_all
from mht.gui.formats.format_text_input import FTextInput, RTLTextInput

class WriteInputScreen(gui.BaseExerciseScreen):
    def __init__(self, lipstick_path, modality='dt', **kwargs):
        super(WriteInputScreen, self).__init__(lipstick_path, modality, **kwargs)
        self.app = gui.App.get_running_app()

    def build_ui(self):
        self.clear_widgets()
        # Create a horizontal layout that splits the animated panel and the input/options
        self.box = gui.BoxLayout(orientation='horizontal')
        self.InputPanel = gui.GridLayout(cols=1, rows=2, size_hint=(0.8, 1), padding=20, spacing=20)
        self.optMenu = self.create_opt_menu()
        
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

        self.box.add_widget(self.InputPanel)
        self.box.add_widget(self.optMenu)
        self.add_widget(self.box)
        
        gui.Clock.schedule_interval(self.update, 1/30)
        gui.Window.bind(on_key_down=self._on_keyboard_handler)
        print('WriteInputScreen initialized with modality:', self.modality)
    
    def create_opt_menu(self, input_callback=None):
        """Create and return the standard option menu with Enter, Exit, and Back buttons."""
        optMenu = gui.GridLayout(cols=1, rows=3, size_hint=(0.2, 1), padding=20, spacing=20)

        if input_callback is None:
            input_callback = partial(self.checkAnswer)

        exit_btn = gui.Button(
            text='Exit', on_release=self.go_back,
            size_hint=(1, 1), font_size=28, background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1),
        )
        back_btn = gui.Button(
            text="Back to Menu", on_release=self.go_back,
            size_hint=(1, 1), font_size=28, background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1)
        )
        enter_btn = gui.Button(
            text='Enter', on_release=input_callback,
            size_hint=(1, 1), font_size=28, background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1)
        )
        optMenu.add_widget(exit_btn)
        optMenu.add_widget(back_btn)
        optMenu.add_widget(enter_btn)
        return optMenu
        
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

        if self.rtl_flag:
            input_answer = get_display(self.input.text)
        else:
            input_answer = strip_accents(self.input.text.lower())
            self.answer = strip_accents(self.answer.lower())

        if self.answer == input_answer:
            self.perf = 1
        else:
            self.perf = 0

        self.show_answer_popup(self.perf, user_input=self.input.text, on_continue=self.on_close)
    
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
        gui.Clock.unschedule(self.update)
        # Unbind keyboard
        gui.Window.unbind(on_key_down=self._on_keyboard_handler)
        # Dismiss popups
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None


