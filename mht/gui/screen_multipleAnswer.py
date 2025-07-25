# --- Multiple Answer Screen (refactored from kivy_multipleAnswer.py) --- #
import time, threading
from bidi.algorithm import get_display

from mht import gui
from mht.gui.common import *
from mht.scripts.python_scripts.update_lipstick import update_all

class MultipleAnswerScreen(gui.BaseExerciseScreen):
    def __init__(self, lipstick_path, modality='rt', **kwargs):
        super(MultipleAnswerScreen, self).__init__(lipstick_path, modality, **kwargs)
        self.app = gui.App.get_running_app()
        self.app_start_time = time.time()
        self.teamlippath = lipstick_path

    def build_ui(self):
        self.box = gui.BoxLayout(orientation='vertical')
        self.upper_panel = gui.GridLayout(cols=3, size_hint_y=0.8)
        
        # Options panel (left column)
        self.optMenu = gui.GridLayout(cols=1, rows=3, size_hint_x=0.25,
                                      padding=20, spacing=20)
        exit_btn = gui.Button(text='Exit', background_color=(0.6, 0.5, 0.5, 1))
        exit_btn.bind(on_release=self.go_back)
        self.optMenu.add_widget(exit_btn)
        correction = gui.CorrectionDialog(self.answer, self.question)
        self.optMenu.add_widget(correction)
        self.upper_panel.add_widget(self.optMenu)
        self.box.add_widget(self.upper_panel)
        back_btn = gui.Button(text="Back to Menu", size_hint=(1, 0.1))
        back_btn.bind(on_release=self.go_back)

        # Animated panel (right column) from the base class
        self.upper_panel.add_widget(self.animated_container)
        
        # Answer buttons (center column)
        # options = rnd_options(self.lippath, iquest=self.iqu, modality=self.modality)
        options = sample_similar_options(self.lippath, self.iqu, self.modality)
        options[self.answer] = True
        shufOpts = shuffle_dic(options)
        self.load_answers(shufOpts)
        
        self.box.add_widget(back_btn)
        self.add_widget(self.box)
        
        gui.Clock.schedule_interval(self.update, 1/30)
        gui.Window.bind(on_key_down=self._on_keyboard_handler)
    
    def load_answers(self, answers: dict):
        self.listOp = []
        self.AnswerPanel = gui.GridLayout(cols=2, rows=2, padding=40, spacing=20)
        hints = ['A', 'B', 'C', 'D']
        for h, ans_text in zip(hints, answers):
            layout = gui.BoxLayout(orientation='vertical')
            hint_label = gui.Label(text=h, size_hint=(0.2, 0.2))
            layout.add_widget(hint_label)
            op = gui.EachOption(ans_text, answers[ans_text], self.rtl_flag, callback=self.process_answer)
            layout.add_widget(op)
            self.listOp.append(op)
            self.AnswerPanel.add_widget(layout)
        self.box.add_widget(self.AnswerPanel)
    
    def _on_keyboard_handler(self, instance, keyboard, keycode, *args):
        if keycode in range(30, 33):
            self.listOp[keycode - 30].on_release()
        elif keycode == 4:
            self.listOp[0].on_release()
        elif keycode == 5:
            self.listOp[1].on_release()
        elif keycode == 6:
            self.listOp[2].on_release()
        elif keycode == 7:
            self.listOp[3].on_release()

    def confirmation_popup(self, perf, *_):
        self.show_answer_popup(perf, on_continue=self.on_close)

    def process_answer(self, perf):
        print('In process_answer word_ul: ', self.word_ul)
        self.perf = perf
        elapsed_time = time.time() - self.app_start_time
        self.speed = 1 / elapsed_time
        self.confirmation_popup(self.perf)

    def on_close(self, *_):

        # Dismiss the popup if it exists
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        flag_rebag = update_all(self.lipstick, self.teamlippath, self.word_ul, self.perf, self.speed, mode='m' + self.modality)        

        if flag_rebag:
            print('Rebagging team...')
            self.app.init_rebag()
        else:
            current_name = self.name
            self.go_back(current_name)

    def on_leave(self, *args):
        self.built = False
        # Unschedule updates
        gui.Clock.unschedule(self.update)
        # Unbind keyboard
        gui.Window.unbind(on_key_down=self._on_keyboard_handler)
        # Dismiss popups
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None