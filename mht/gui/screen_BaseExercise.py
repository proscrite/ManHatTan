# base_exercise_screen.py
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
import time
from mht.gui.common import *
from bidi.algorithm import get_display

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

class BaseExerciseScreen(Screen):
    def __init__(self, lipstick_path, modality, **kwargs):
        super(BaseExerciseScreen, self).__init__(**kwargs)
        self.lippath = lipstick_path
        self.modality = modality
        self.built = False  # Add this flag

    def on_enter(self, *args):
        if not self.built:
            self.init_exercise()
            self.build_ui()
            self.built = True

    def on_leave(self, *args):
        self.clear_widgets()  # Remove all widgets immediately on leave
        self.built = False
        # Unschedule updates
        Clock.unschedule(self.update)

    def init_exercise(self):
        
        # All the logic that was in __init__ before:
        self.start_time = time.time()
        self.lipstick = load_lipstick(self.lippath, self.modality)
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag)
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
        
        entry_stats = load_pkmn_stats(qentry)
        n_cracks = qentry.get('history_correct', 0) % 6
        self.fig, self.img_display, self.anim = plot_combat_stats(entry_stats, self.nframe, self.nid, self.question_displ, n_cracks = n_cracks)
        self.fig_canvas = FigureCanvasKivyAgg(self.fig)
        from kivy.uix.boxlayout import BoxLayout
        container = BoxLayout()
        container.add_widget(self.fig_canvas)
        self.animated_container = container

    def build_ui(self):
        # This remains as before, but is only called from on_enter
        pass  # (leave as is, or move your UI code here)

    def update(self, dt):
        # Common animation update method
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        frame_width = self.anim.shape[0]
        new_img = self.anim[:, frame_width * self.nframe: frame_width * (self.nframe+1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()
    
    def go_back(self, current_name, *args):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "main_menu"