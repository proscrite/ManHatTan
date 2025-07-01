from mht import gui
import pandas as pd
from mht.gui.book_processor.kivy_cadera_DfWidget import DfguiWidget, HoverBehavior
from mht.gui.common import COLOR_MAP, DEFAULT_COLOR


class ColorOption(gui.Button, HoverBehavior):
    hover_scale = gui.NumericProperty(1.0)
    bg_color = gui.ListProperty([1, 1, 1, 1])
    hover_color = gui.ListProperty([1, 1, 1, 1])
    down_color = gui.ListProperty([1, 1, 1, 1])

    def __init__(self, color_name, color_value, callback, **kwargs):
        color_value = tuple(list(color_value[:3]) + [1])
        super().__init__(
            text=color_name.capitalize(),
            background_normal='',
            background_color=(1, 1, 1, 0),
            font_size=28,
            size_hint=(1, None),
            height=80,
            **kwargs
        )
        self.color_name = color_name
        self.callback = callback
        self.bg_color = color_value
        self.hover_color = [min(1, c + 0.15) for c in color_value[:3]] + [1]
        self.down_color = [max(0, c - 0.15) for c in color_value[:3]] + [1]
        self.bind(hovered=self.on_hover)
        self.bind(state=self.on_state)

    def on_hover(self, instance, value):
        if value:
            self.bg_color = self.hover_color
            self.hover_scale = 1.08
        else:
            self.bg_color = self.original_color if hasattr(self, 'original_color') else self.bg_color
            self.hover_scale = 1.0

    def on_state(self, instance, value):
        if value == 'down':
            self.bg_color = self.down_color
        elif self.hovered:
            self.bg_color = self.hover_color
        else:
            self.bg_color = self.original_color if hasattr(self, 'original_color') else self.bg_color

    def on_bg_color(self, instance, value):
        if not hasattr(self, 'original_color'):
            self.original_color = value[:]

    def on_release(self):
        if self.callback:
            self.callback(self.color_name)


gui.Builder.load_string("""
<ColorOption>
    canvas.before:
        PushMatrix
        Scale:
            origin: self.center
            x: root.hover_scale
            y: root.hover_scale
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
        PopMatrix
""")

class ChooseColorScreen(gui.Screen):
    def __init__(self, cder_path, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = None
        self.cder_path = cder_path

        main_layout = gui.BoxLayout(orientation='horizontal', spacing=30, padding=30)
        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        main_layout.add_widget(left_panel)
        main_layout.add_widget(right_panel)
        self.add_widget(main_layout)

    def _build_left_panel(self):
        cadera = pd.read_csv(self.cder_path, index_col=0, nrows=20)
        panel = gui.BoxLayout(orientation='vertical', size_hint_x=0.7, spacing=10)
        panel.add_widget(gui.Label(
            text="[b]Preview of highlights[/b]",
            font_size=22,
            size_hint_y=None,
            height=40,
            markup=True
        ))
        scroll = gui.ScrollView(size_hint=(1, 1))
        scroll.add_widget(DfguiWidget(cadera, col_width=250))
        panel.add_widget(scroll)
        self.cadera = cadera  # Store for use in right panel
        return panel

    def _build_right_panel(self):
        panel = gui.BoxLayout(
            orientation='vertical',
            size_hint_x=0.3,
            spacing=24,
            padding=[20, 60, 20, 60]
        )
        panel.add_widget(gui.Label(
            text="[b]Select highlight color used:[/b]",
            font_size=32,
            size_hint_y=None,
            height=60,
            markup=True
        ))
        panel.add_widget(self._build_color_grid())
        panel.add_widget(gui.Widget())  # Spacer
        panel.add_widget(self._build_back_button())
        return panel

    def _build_color_grid(self):
        color_names = list(self.cadera.columns[:4])
        grid = gui.GridLayout(
            cols=2,
            rows=2,
            spacing=20,
            size_hint=(1, None),
            height=180
        )
        for color_name in color_names:
            color_value = COLOR_MAP.get(color_name.lower(), DEFAULT_COLOR)
            color_value = tuple(list(color_value[:3]) + [1])
            btn = ColorOption(color_name, color_value, callback=self.select_color, width=180)
            grid.add_widget(btn)
        return grid

    def _build_back_button(self):
        back_btn = gui.Button(
            text="Back",
            size_hint=(1, None),
            height=60,
            font_size=22,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_release=self.go_back)
        return back_btn

    def select_color(self, color_name):
        self.selected_color = color_name
        self.manager.shared_data['word_color'] = color_name
        self.manager.current = 'choose_lang'

    def go_back(self, instance):
        self.manager.current = 'select_book'
