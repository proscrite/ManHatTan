# base_exercise_screen.py
from kivy.uix.screenmanager import Screen, SlideTransition
import time
from common import *
from bidi.algorithm import get_display

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'
PATH_ANIM = ROOT_PATH + '/gui/Graphics/Battlers/'

class BaseExerciseScreen(Screen):
    def __init__(self, lipstick_path, modality, **kwargs):
        super(BaseExerciseScreen, self).__init__(**kwargs)
        self.lippath = lipstick_path
        # self.teamlippath = lipstick_path.replace('.lip', '_team.lip')
        self.modality = modality
        self.start_time = time.time()
        self.lipstick = load_lipstick(self.lippath, self.modality)
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        
        # Pick a question using your set_question function
        self.word_ll, self.word_ul, self.iqu, self.nid = set_question(self.lippath, self.rtl_flag, size_head=6)
        if self.modality == 'dt':
            self.question, self.answer = self.word_ll, self.word_ul
            self.checkEntry = 'word_ul'
        else:
            self.question, self.answer = self.word_ul, self.word_ll
            self.checkEntry = 'word_ll'
        
        self.nframe = 0
        self.lipstick.set_index('n_id', inplace=True, drop=False)
        
        # Prepare display texts (handling RTL)
        if self.rtl_flag:
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)
        else:
            self.question_displ = self.question
            self.answer_displ = self.answer
        
        # Build common animated stats panel
        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig, self.img_display, self.anim = plot_combat_stats(entry_stats, self.nframe, self.nid, self.question_displ)
        self.fig_canvas = FigureCanvasKivyAgg(self.fig)
        from kivy.uix.boxlayout import BoxLayout
        container = BoxLayout()
        container.add_widget(self.fig_canvas)
        self.animated_container = container

    def update(self, dt):
        # Common animation update method
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        frame_width = self.anim.shape[0]
        new_img = self.anim[:, frame_width * self.nframe: frame_width * (self.nframe+1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()
    
    def go_back(self, current_name, *args):
     # Get the ScreenManager
        sm = self.manager
        # Save the name of this screen so we can re-add it under the same name
        new_screen = type(self)(self.lippath, modality=self.modality, name=current_name)
        # Remove the old screen and add the new one.
        sm.remove_widget(self)
        sm.add_widget(new_screen)
        
        # Call set_question for new question and go back to main menu
        self.app.flag_refresh = True
        sm.transition = SlideTransition(direction="right")
        sm.current = "main_menu"