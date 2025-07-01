from mht import gui
import pandas as pd
from mht.gui.book_processor.kivy_choose_word_color import DfguiWidget

class ColorOption(gui.Button):
    def __init__(self, color_name, color_value, callback, **kwargs):
        color_value = tuple(list(color_value[:3]) + [1])
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

        # Main vertical layout
        main_layout = gui.BoxLayout(orientation='vertical', spacing=30, padding=30)

        # --- Top: DataFrame Preview in ScrollView ---
        cadera = pd.read_csv(self.cder_path, index_col=0, nrows=20)
        top_panel = gui.BoxLayout(orientation='vertical', size_hint_y=0.65, spacing=10)
        top_panel.add_widget(gui.Label(
            text="[b]Preview of highlights[/b]",
            font_size=22,
            size_hint_y=None,
            height=40,
            markup=True
        ))
        scroll = gui.ScrollView(size_hint=(1, 1))
        scroll.add_widget(DfguiWidget(cadera, col_width=250))
        top_panel.add_widget(scroll)
        main_layout.add_widget(top_panel)

        # --- Bottom: Color Selection ---
        bottom_panel = gui.BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=10)
        bottom_panel.add_widget(gui.Label(
            text="[b]Select highlight color used:[/b]",
            font_size=26,
            size_hint_y=None,
            height=60,
            markup=True
        ))

        # Center the grid horizontally
        grid_container = gui.BoxLayout(orientation='horizontal', size_hint_y=None, height=200)
        grid = gui.GridLayout(cols=2, rows=2, spacing=20, size_hint=(None, None), width=400, height=180)
        color_options = {
            'blue': (0.13, 0.19, 0.34, 1),
            'red': (0.32, 0.13, 0.13, 1),
            'green': (0.13, 0.27, 0.17, 1),
            'yellow': (0.36, 0.33, 0.13, 1)
        }
        for color_name, color_value in color_options.items():
            btn = ColorOption(color_name, color_value, callback=self.select_color, width=180)
            grid.add_widget(btn)
        grid_container.add_widget(gui.Label(size_hint_x=0.5))  # Spacer left
        grid_container.add_widget(grid)
        grid_container.add_widget(gui.Label(size_hint_x=0.5))  # Spacer right

        bottom_panel.add_widget(grid_container)
        main_layout.add_widget(bottom_panel)

        self.add_widget(main_layout)

    def select_color(self, color_name):
        self.selected_color = color_name
        self.manager.shared_data['word_color'] = color_name
        self.manager.current = 'choose_lang'  # or the next screen in your flow
