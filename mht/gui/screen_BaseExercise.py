# base_exercise_screen.py
from mht import gui

import time
from mht.gui.common import *
from bidi.algorithm import get_display

class BaseExerciseScreen(gui.Screen):
    def __init__(self, lipstick_path, modality, **kwargs):
        super(gui.BaseExerciseScreen, self).__init__(**kwargs)
        self.lippath = lipstick_path
        self.modality = modality
        self.lipstick = load_lipstick(self.lippath, self.modality)  # <-- Load here!
        self.built = False  # Add this flag

    def on_enter(self, *args):
        self.reload_lipstick()
        if not self.built:
            self.init_exercise()
            self.build_ui()
            self.built = True

    def on_leave(self, *args):
        self.clear_widgets()  # Remove all widgets immediately on leave
        self.built = False
        # Unschedule updates
        gui.Clock.unschedule(self.update)

    def init_exercise(self):
        """Initialize the exercise by setting up the question and answer."""
        # All the logic that was in __init__ before:
        self.start_time = time.time()
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath)
        
        print(f"After set_question, selected word_ll: {self.word_ll}, word_ul: {self.word_ul}, iqu: {self.iqu}, nid: {self.nid}")
        if self.modality == 'dt':
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        else:
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'
        self.nframe = 0
        self.lipstick.set_index('word_ul', inplace=True, drop=False)
        if self.rtl_flag:
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)
        else:
            self.question_displ = self.question
            self.answer_displ = self.answer
        qentry = self.lipstick.loc[self.word_ul].copy()
        print(f"Initializing BaseExerciseScreen with question: {self.question_displ}, answer: {self.answer_displ}, nid: {self.nid}")
        entry_stats = load_pkmn_stats(qentry)
        n_cracks = qentry.get('history_correct', 0) % 6

        # Only create animated_container if not ClawScreen
        if self.__class__.__name__ != "ClawScreen":
            self.fig, self.img_display, self.anim = plot_combat_stats(entry_stats, self.nframe, self.nid, self.question_displ, n_cracks = n_cracks)
            self.fig_canvas = FigureCanvasKivyAgg(self.fig)
            from kivy.uix.boxlayout import BoxLayout
            container = BoxLayout()
            container.add_widget(self.fig_canvas)
            self.animated_container = container
        else:
            self.animated_container = None

    def build_ui(self):
        # This remains as before, but is only called from on_enter
        pass  # (leave as is, or move your UI code here)

    def show_answer_popup(self, perf, user_input=None, on_continue=None):
        """Show a popup with the result of the answer.

        Args:
            perf (int): 1 if correct, 0 if incorrect.
            user_input (str, optional): The user's answer (for display if incorrect).
            on_continue (callable, optional): Callback for the Continue button.
        """

        layout = gui.GridLayout(cols=2, padding=10)
        label = gui.Button(
            text='Exercise: ' + self.question_displ,
            font_name=FONT_HEB,
            font_size=40, bold=True, size_hint=(2, 1)
        )
        layout.add_widget(label)

        correction = gui.CorrectionDialog(self.question_displ, self.answer)
        if correction.parent:
            correction.parent.remove_widget(correction)
        layout.add_widget(correction)

        if perf == 1:
            result_text = 'Correct! ' + self.answer_displ
            bg_color = (0, 1, 0, 1)
        else:
            if user_input:
                result_text = f"{user_input}: Incorrect! {self.answer_displ}"
            else:
                result_text = 'Incorrect! ' + self.answer_displ
            bg_color = (1, 0, 0, 1)

        result_btn = gui.Button(
            text=result_text,
            font_name=FONT_HEB,
            font_size=40, size_hint=(2, 1),
            background_color=bg_color
        )
        layout.add_widget(result_btn)

        cont_btn = gui.Button(
            text='Continue',
            on_release=on_continue if on_continue else self.on_close,
            size_hint=(0.5, 1), background_color=(1, 1, 0, 1)
        )
        layout.add_widget(cont_btn)

        screen_name = getattr(self, "name", None)
        if screen_name:
            popup_title = screen_name.replace("_", " ").title()
        else:
            popup_title = "Exercise"

        self.answer_popup = gui.Popup(title=popup_title, content=layout)
        self.answer_popup.open()

    def update(self, dt):
        # Common animation update method
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        frame_width = self.anim.shape[0]
        new_img = self.anim[:, frame_width * self.nframe: frame_width * (self.nframe+1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()
    
    def reload_lipstick(self):
        self.lipstick = load_lipstick(self.lippath, self.modality)
    
    def go_back(self, current_name, *args):
        self.manager.transition = gui.SlideTransition(direction="right")
        self.manager.current = "main_menu"