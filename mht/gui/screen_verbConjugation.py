import random

from mht import gui
from mht.scripts.python_scripts.pealim_scraper import get_random_conjugation
from mht.gui.screen_BaseExercise import plot_combat_stats, load_pkmn_animation, load_pkmn_stats
from mht.gui.formats.format_text_input import FTextInput, RTLTextInput
from mht.gui.common import *
from bidi.algorithm import get_display
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

class ConjugationScreen(gui.WriteInputScreen):
    def __init__(self, lipstick_path, modality='dt', **kwargs):
        # We'll set question/answer after verb input
        super().__init__(lipstick_path, modality, **kwargs)
        self.verb = None
        self.question = None
        self.answer = None
        self.nid = random.randint(1, 151)  # Use a random n_id for the pkmn panel
        self.rtl_flag = True

    def build_ui(self):
        # Only build UI after verb is set
        pass

    def show_verb_input_popup(self):
        layout = gui.BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = gui.Label(text="[b]Enter a Hebrew verb to conjugate: [/b]", font_size=30, markup=True, font_name=FONT_HEB)
        self.verb_input = RTLTextInput(
            hint_text="Hebrew verb", multiline=False, on_text_validate=self.on_verb_submit,
            font_size=32, font_name=FONT_HEB
        )
        submit_btn = gui.Button(text="Submit", size_hint=(1, 0.5), font_size=24)
        submit_btn.bind(on_release=self.on_verb_submit)
        layout.add_widget(label)
        layout.add_widget(self.verb_input)
        layout.add_widget(submit_btn)
        self.verb_popup = gui.Popup(title="Conjugation Exercise", content=layout, size_hint=(0.7, 0.5), auto_dismiss=False)
        self.verb_popup.open()

    def on_verb_submit(self, instance):
        verb = self.verb_input.text.strip()
        verb = get_display(verb)  # Ensure proper RTL display
        if not verb:
            self.verb_input.hint_text = "Please enter a verb!"
            return
        self.verb = verb
        self.init_exercise()

        parsed_english_key, parsed_hebrew_hint, conjugated_verb, infinitive_form = get_random_conjugation(self.verb)
        if not parsed_english_key or not conjugated_verb:
            self.verb_input.text = ""
            self.verb_input.hint_text = "No conjugation found, try another verb."
            return
        self.infinitive_form = infinitive_form if infinitive_form else self.verb
        self.question = f"{parsed_english_key}"
        self.answer = str(conjugated_verb)
        self.hint_answer = get_display(parsed_hebrew_hint) if parsed_hebrew_hint else 'Enter conjugation'
        self.answer = get_display(self.answer)  # Ensure proper RTL display
        print(f"Conjugation found: {self.question} -> {self.answer}")
        self.verb_popup.dismiss()
        self.build_conjugation_ui()

    def build_conjugation_ui(self):
        # Now build the UI as in WriteInputScreen, but with our question/answer
        self.box = gui.BoxLayout(orientation='horizontal')
        self.InputPanel = gui.BoxLayout(orientation='vertical', size_hint=(0.8, 1), padding=20, spacing=20)
        self.optMenu = self.create_opt_menu()
        
        # Animated panel (use random n_id)
        qentry = self.lipstick.iloc[0]
        entry_stats = load_pkmn_stats(qentry)

        fig, img_display, anim = plot_combat_stats(entry_stats, 0, self.nid, self.question, n_cracks=0)
        ax_im = fig.get_axes()[-1]
        ax_im.set_title(f"Conjugate $\\bf{{{get_display(self.infinitive_form)}}}$", color='yellow', fontsize=30)

        qxlabel = self.question.replace(' - ', '\n')
        ax_im.set_xlabel(f"{qxlabel}")

        fig.subplots_adjust(top=0.85, wspace=0.7)  # Increase horizontal space between subplots
        fig_canvas = FigureCanvasKivyAgg(fig)
        fig_canvas.draw_idle()
        container = gui.BoxLayout()
        container.add_widget(fig_canvas)
        self.animated_container = container
        self.InputPanel.add_widget(self.animated_container)

        input_callback = lambda instance: self.checkAnswer(instance)
        self.input = RTLTextInput(
            hint_text=self.hint_answer, multiline=False, font_name=FONT_HEB,
            on_text_validate=input_callback, font_size=40, background_color=(0.9,0.9,0.9,1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}, center_y=0.5, halign="center"
        )
        
        self.InputPanel.add_widget(self.input)

        self.box.add_widget(self.InputPanel)
        self.box.add_widget(self.optMenu)
        self.add_widget(self.box)

        gui.Window.bind(on_key_down=self._on_keyboard_handler)
        gui.Clock.schedule_interval(self.update, 1/30)

    def checkAnswer(self, instance):
        # Dismiss an existing popup if it exists.
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        layout = gui.GridLayout(cols=1, padding=10)
        label = gui.Label(
            text=f'[b]Question:  {get_display(self.infinitive_form)}, {self.question}[/b]',
            markup=True, font_name=FONT_HEB, font_size=40, bold=True, size_hint=(1, 0.5)
        )
        layout.add_widget(label)

        user_input = self.input.text.strip()
        user_input_stripped = strip_accents(user_input)
        answer_stripped = strip_accents(self.answer)

        if user_input_stripped == answer_stripped:
            result_btn = gui.Button(
                text=f"[b]Correct! {self.answer}[/b]", markup=True, font_name=FONT_HEB,
                font_size=40, size_hint=(1, 0.5), background_color=(0, 1, 0, 1)
            )
        else:
            result_btn = gui.Button(
                text=f"Incorrect! Your answer: {user_input} \n[b]Correct answer: {self.answer}[/b]",
                markup=True, font_name=FONT_HEB, font_size=40, size_hint=(1, 0.5), background_color=(1, 0, 0, 1)
            )
        layout.add_widget(result_btn)

        cont_btn = gui.Button(
            text='Continue', on_release=self.go_back, size_hint=(1, 0.5), background_color=(1, 1, 0, 1)
        )
        layout.add_widget(cont_btn)

        self.answer_popup = gui.Popup(content=layout)
        self.answer_popup.open()

    def start_random_conjugation(self):
        """Start a random conjugation exercise by selecting a verb from lipstick."""

        verb = sample_random_verb(self.lipstick)
        if verb:
            self.verb = verb
            self.init_exercise()
            print(f"Initialized exercise with verb: {get_display(self.verb)}")
            parsed_english_key, parsed_hebrew_hint, conjugated_verb, infinitive_form = get_random_conjugation(self.verb)
            if not parsed_english_key or not conjugated_verb:
                print("No conjugation found, try another verb.")
                return
            self.infinitive_form = infinitive_form if infinitive_form else verb
            self.question = f"{parsed_english_key}"
            self.answer = get_display(str(conjugated_verb))
            self.hint_answer = get_display(parsed_hebrew_hint) if parsed_hebrew_hint else 'Enter conjugation'
            print(f"Conjugation found: {self.question} -> {self.answer}")
            self.build_conjugation_ui()
        else:
            print("No verbs found in lipstick.")
            # Optionally, fall back to popup:
            self.show_verb_input_popup()

    def on_enter(self, *args):
        self.init_exercise()
        self.start_random_conjugation()

# Uncomment this section to test the ConjugationScreen in a standalone app

# class TestConjugationApp(App):
#     def build(self):
#         sm = ScreenManager()
#         # You can change modality if needed
#         conj_screen = ConjugationScreen(LIPSTICK_PATH, modality='dt', name='conjugation')
#         sm.add_widget(conj_screen)
#         return sm

# if __name__ == "__main__":
#     TestConjugationApp().run()