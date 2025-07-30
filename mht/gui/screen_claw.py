from mht import gui
from mht.gui.common import *
from mht.scripts.LLM_scripts.claw import claw_exercise

class ClawScreen(gui.MultipleAnswerScreen):
    def __init__(self, lipstick_path, modality='rt', **kwargs):
        super().__init__(lipstick_path, modality=modality, **kwargs)
        self.is_egg_screen = True
        print('Initializing ClawScreen with lipstick path:', lipstick_path)
        # This needs to run in a separate thread to avoid blocking the UI
        
        self.lipstick = pd.read_csv(lipstick_path)
        self.lipstick = self.lipstick.set_index('word_ul', drop=False)
        self.lipstick_path = lipstick_path
        
        self.cloze_sentence = None
        self.translation = None 
        
    def init_exercise(self):
        super().init_exercise()  # Sets self.word_ll, self.word_ul, etc.
        print(f"ClawScreen: self.word_ll after super().init_exercise() = {self.word_ll}")
        # Generate cloze sentence for the sampled word
        result = claw_exercise(self.lipstick_path, word_ll=self.word_ll, word_ul=self.word_ul)
        if result:
            self.cloze_sentence, self.translation = result
            self.cloze_sentence = get_display(self.cloze_sentence) if self.rtl_flag else self.cloze_sentence
        else:
            self.cloze_sentence, self.translation = "(No cloze sentence generated)", None

    def build_ui(self):
        self.cloze_label = gui.Label(
            text=self.cloze_sentence,
            font_name=FONT_HEB,
            font_size=70,
            halign='center',
            valign='middle',
            size_hint_y=0.18,
        )
        super().build_ui()

        hallucinate_btn = gui.Button(text='Hallucination', background_color=(0.8, 0.5, 0.2, 1))
        hallucinate_btn.bind(on_release=self.bypass_sentence)
        self.optMenu.add_widget(hallucinate_btn)

    def bypass_sentence(self, instance):
        """Bypass the current word: remove from egg db and reload EggScreen."""
        print(f"Bypassing word: {self.word_ul}")
        self._reload_claw_screen()

    def _reload_claw_screen(self):
        """Reload the ClawScreen to refresh the current word."""
        manager = self.manager
        temp_screen = None

        # Add a temporary blank screen if not present
        if not manager.has_screen('temp_blank'):
            temp_screen = gui.Screen(name='temp_blank')
            manager.add_widget(temp_screen)
        manager.current = 'temp_blank'

        if manager.has_screen(self.name):
            manager.remove_widget(self)  # Remove the current EggScreen
        
        new_claw_screen = ClawScreen(self.teamlippath, modality=self.modality, name=self.name)
        manager.add_widget(new_claw_screen)   # Add the new EggScreen with the same name
        manager.current = self.name     # Switch to the new EggScreen

        if temp_screen:
            manager.remove_widget(temp_screen)

    def get_right_panel_widget(self): # type: ignore
        return self.cloze_label

    def update(self, dt):
        # No animation for ClawScreen
        pass