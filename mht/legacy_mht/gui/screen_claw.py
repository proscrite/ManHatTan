from mht.legacy_mht import gui
from mht.legacy_mht.gui.common import *
from mht.legacy_mht.scripts.LLM_scripts.claw import claw_exercise
from kivy import Config
Config.set('kivy', 'text_provider', 'pango')

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
        # result = claw_exercise(self.lipstick_path, word_ll=self.word_ll, word_ul=self.word_ul)
        # This is a placeholder for the actual cloze sentence generation logic
        result = ('זה משפט הוא דוגמה ארוך מאוד שלוקח הרבה מקום ואפילו שלוש שורות לתרגיל קלוזה עם ____ מילה ', 'This sentence is an example of a very long sentence taking a lot of space even three lines of a Cloze exercise')  # Example result 
        if result:
            self.cloze_sentence, self.translation = result
            # self.cloze_sentence = get_display(self.cloze_sentence) if self.rtl_flag else self.cloze_sentence
            print(f"Translated sentence: {self.translation}")
        else:
            self.cloze_sentence, self.translation = "(No cloze sentence generated)", None

        self.fig_canvas, self.img_display, self.anim = plot_pkmn_animation(self.nid, self.nframe, n_cracks=0)

    def build_ui(self):
        """Build the UI components for the ClawScreen."""
        
        self.build_labels()
        super().build_ui() # Here the option Buttons are built
        
        self.optMenu.remove_widget(self.correction)
        # self.upper_panel.remove_widget(self.get_right_panel_widget())
        
        self.build_opt_menu()
        

    def build_labels(self):
        # Create a vertical BoxLayout for the labels
        label_box = gui.BoxLayout(orientation='vertical', size_hint=(1, None))
        label_box.bind(minimum_height=label_box.setter('height'))

        self.cloze_label = gui.Label(
            text=self.cloze_sentence,
            font_name=FONT_HEB,
            font_size=60,
            halign='center',
            valign='middle',
            base_direction='rtl',# if self.rtl_flag else 'ltr',
            text_language='he', 
            size_hint_y=None,
            height=300,  # Adjust as needed for default height
            shorten=False
        )
        self.translation_label = gui.Label(
            text='',
            font_name=FONT_HEB,
            font_size=45,
            halign='center',
            valign='bottom',
            size_hint_y=None,
            height=100,
            shorten=False,
            color=(0.8, 0.8, 0.2, 1)
        )
        self.translation_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        self.cloze_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))

        # Spacer widget for vertical space
        spacer = gui.Label(text='', size_hint_y=None, height=100)

        # Bind text_size for wrapping

        label_box.add_widget(self.cloze_label)
        label_box.add_widget(spacer)
        label_box.add_widget(self.translation_label)

        # Put the label_box inside a ScrollView
        scroll = gui.ScrollView(size_hint=(0.7, 1))
        scroll.add_widget(label_box)

        # Create the right_box with horizontal layout
        self.right_box = gui.BoxLayout(orientation='horizontal')
        self.right_box.add_widget(scroll)
        self.fig_canvas.size_hint = (0.3, 1)
        self.right_box.add_widget(self.fig_canvas)


    def build_opt_menu(self):
        hallucinate_btn = gui.Button(text='Hallucination', background_color=(0.8, 0.5, 0.2, 1))
        hallucinate_btn.bind(on_release=self.bypass_sentence)
        self.optMenu.add_widget(hallucinate_btn)

        self.show_translation_btn = gui.Button(text='Show translation', background_color=(0.3, 0.5, 0.8, 1))
        self.show_translation_btn.bind(on_release=self.show_translation)
        self.optMenu.add_widget(self.show_translation_btn)

        self.hint_btn = gui.Button(text='Hint', background_color=(0.2, 0.7, 0.4, 1))
        self.hint_btn.bind(on_release=self.show_hint)
        self.optMenu.add_widget(self.hint_btn)

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
        return self.right_box

    def show_translation(self, instance):
        self.translation_label.text = self.translation if self.translation else "(No translation available)"
        self.show_translation_btn.disabled = True

    def show_hint(self, instance):
        # For now, just append a test string
        self.cloze_sentence += "\n(Hint: This is a test hint sentence.)"
        self.cloze_label.text = self.cloze_sentence
        self.hint_btn.disabled = True
        

    # def update(self, dt):
        # No animation for ClawScreen
        # pass