# base_exercise_screen.py
from kivy.uix.screenmanager import Screen, SlideTransition
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
        # self.teamlippath = lipstick_path.replace('.lip', '_team.lip')
        self.modality = modality
        self.start_time = time.time()
        self.lipstick = load_lipstick(self.lippath, self.modality)
        self.rtl_flag = (self.lipstick.learning_language.iloc[0] == 'iw')
        
        self.question, self.answer, self._setup_based_on_modality()

        # prepare display
        self._prepare_display_texts()

        self.nframe = 0
        self.lipstick.set_index('n_id', inplace=True, drop=False)

        # stats animation
        stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig, self.img_display, self.anim = plot_combat_stats(stats, 0, self.nid, self.question_displ)
        self.figure_container = self._build_figure_container()

        # high-level layout
        self.root_layout = BoxLayout(orientation=self.root_orientation)
        self.root_layout.add_widget(self.figure_container)

        # child adds its own controls
        self.build_controls()

        # schedule animation update and keyboard
        Clock.schedule_interval(self._update_animation, 1/30)
        Window.bind(on_key_down=self._on_keyboard)
        
        self.add_widget(self.root_layout)
        
        # Build common animated stats panel
        entry_stats = load_pkmn_stats(self.lipstick, self.nid)
        self.fig, self.img_display, self.anim = plot_combat_stats(entry_stats, self.nframe, self.nid, self.question_displ)
        self.fig_canvas = FigureCanvasKivyAgg(self.fig)
        from kivy.uix.boxlayout import BoxLayout
        container = BoxLayout()
        container.add_widget(self.fig_canvas)
        self.animated_container = container

    def _setup_based_on_modality(self):
        # returns question, answer and sets checkEntry, nid, iqu
        low, up, iqu, nid = set_question(self.lippath, self.rtl_flag)
        self.iqu, self.nid = iqu, nid
        if self.modality == 'dt':
            self.question, self.answer = low, up
            self.checkEntry = 'word_ul'
        else:
            self.question, self.answer = up, low
            self.checkEntry = 'word_ll'

    def _prepare_display_texts(self):
        if self.rtl_flag:
            self.question_displ = get_display(self.question)
            self.answer_displ = get_display(self.answer)
        else:
            self.question_displ = self.question
            self.answer_displ = self.answer

    def _build_figure_container(self):
        
        fig_canvas = FigureCanvasKivyAgg(self.fig)
        box = BoxLayout()
        box.add_widget(fig_canvas)
        return box

    def _update_animation(self, dt):

        # Common animation update method
        self.nframe = (self.nframe + 1) % (self.anim.shape[1] // self.anim.shape[0])
        frame_width = self.anim.shape[0]
        new_img = self.anim[:, frame_width * self.nframe: frame_width * (self.nframe+1), :]
        self.img_display.set_data(new_img)
        self.fig_canvas.draw()
    
    @abstractmethod
    def build_controls(self):
        """Hook for child to build input or options panels"""
        pass

    def process_answer(self, perf):
        self.perf = perf
        elapsed = time.time() - self.start_time
        self.speed = 1 / elapsed
        self._show_confirmation()

    def _show_confirmation(self):
        # common popup layout with question, correction dialog, result
        layout = BoxLayout(orientation='vertical', spacing=10)
        # add labels, correction widget, result button...
        # child hook for post-confirm
        self._post_confirmation()

    def _post_confirmation(self):
        # default: continue -> go back
        return

    def on_continue(self, *args):
        # default: possibly rebag or go_back
        flag = self._update_lipstick()
        if flag:
            App.get_running_app().init_rebag()
        else:
            self.go_back()

    def _update_lipstick(self):
        from mht.scripts.python_scripts.update_lipstick import update_all
        return update_all(self.lipstick, self.lippath, self.word_ul, self.perf, self.speed, mode=self.mode_code)

    def go_back(self, *args):
        sm = self.manager
        new_screen = type(self)(self.lippath, self.modality, name=self.name)
        sm.remove_widget(self)
        sm.add_widget(new_screen)
        self.app.flag_refresh = True
        sm.transition = SlideTransition(direction='right')
        sm.current = 'main_menu'

    def _on_keyboard(self, instance, keyboard, keycode, *args):
        # child may override
        pass
