from mht import gui
import pandas as pd
from mht.gui.book_processor.kivy_choose_word_color import DfguiWidget

class ColorOption(gui.Button):
    def __init__(self, color_name, color_value, callback, **kwargs):
        super().__init__(
            text=color_name.capitalize(),
            background_color=color_value,
            font_size=28,
            size_hint=(1, None),
            height=80,
            **kwargs
        )
        self.color_name = color_name
        self.callback = callback

    def on_release(self):
        if self.callback:
            self.callback(self.color_name)

class ChooseColorScreen(gui.Screen):
    def __init__(self, cder_path, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = None
        self.cder_path = cder_path

        main_grid = gui.GridLayout(cols=2, spacing=20, padding=20)

        # --- Left: DataFrame Preview ---
        cadera = pd.read_csv(self.cder_path, index_col=0, nrows=10)
        boxDf = gui.BoxLayout(orientation='vertical')
        boxDf.add_widget(DfguiWidget(cadera))
        main_grid.add_widget(boxDf)

        # --- Right: Color Selection ---
        color_box = gui.BoxLayout(orientation='vertical', spacing=20, padding=[0, 40, 0, 40])
        color_box.add_widget(gui.Label(
            text="[b]Select highlight color used:[/b]",
            font_size=28,
            size_hint_y=None,
            height=60,
            markup=True
        ))

        color_options = {
            'blue': (0.2, 0.4, 0.8, 1),
            'red': (0.8, 0.2, 0.2, 1),
            'green': (0.2, 0.7, 0.3, 1),
            'yellow': (0.9, 0.8, 0.2, 1)
        }
        for color_name, color_value in color_options.items():
            btn = ColorOption(color_name, color_value, callback=self.select_color)
            color_box.add_widget(btn)

        main_grid.add_widget(color_box)
        self.add_widget(main_grid)

    def select_color(self, color_name):
        self.selected_color = color_name
        self.manager.shared_data['word_color'] = color_name
        self.manager.current = 'choose_lang'  # or the next screen in your flow
