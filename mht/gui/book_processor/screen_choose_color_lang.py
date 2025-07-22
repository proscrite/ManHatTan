from mht import gui
import pandas as pd
import asyncio
from mht.gui.book_processor.kivy_cadera_DfWidget import DfguiWidget, HoverBehavior
from mht.scripts.python_scripts.bulkTranslate import find_language

from mht.gui.common import COLOR_MAP, DEFAULT_COLOR


class LangButton(gui.Button):
    def __init__(self, ulang, ulang_short, callback, **kwargs):
        super().__init__(text=ulang, **kwargs)
        self.ulang_short = ulang_short
        self.callback = callback

    def on_release(self):
        if self.callback:
            self.callback(self.ulang_short)


class ColorOption(gui.Button, HoverBehavior):
    hover_scale = gui.NumericProperty(1.0)
    bg_color = gui.ListProperty([1, 1, 1, 1])
    hover_color = gui.ListProperty([1, 1, 1, 1])
    down_color = gui.ListProperty([1, 1, 1, 1])
    hover_enabled = gui.BooleanProperty(True)
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
        self.hover_enabled = True

    def on_hover(self, instance, value):
        if not self.hover_enabled:
            return
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

class ChooseColorLangScreen(gui.Screen):
    def __init__(self, cder_path, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = None
        self.selected_lang = None
        self.cder_path = cder_path
        self.learn_lang = None
        self.user_lang = None

        self.main_layout = gui.BoxLayout(orientation='horizontal', spacing=30, padding=30)
        self.left_panel = self._build_left_panel()
        self.right_panel = self._build_right_panel()

        self.main_layout.add_widget(self.left_panel)
        self.main_layout.add_widget(self.right_panel)
        self.add_widget(self.main_layout)

    def on_pre_enter(self):
        # Run language detection when entering the screen
        self.detect_language_async()

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
        df_widget = DfguiWidget(cadera, col_width=250, header_callback=self.select_color)
        scroll.add_widget(df_widget)
        # Collect header cells for later use
        self.header_cells = []
        try:
            table = df_widget.panel1.children[0]  # Table
            header = table.header.header.children  # List of HeaderCell widgets
            self.header_cells = header
        except Exception:
            pass

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
        panel.add_widget(gui.Widget(size_hint_y=None, height=20))  # Spacer between color and lang sections
        self.lang_grid_added = False
        # Reserve a container for the language section
        self.lang_section = gui.BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=3 * 70 + 60,  # Enough for label + 3 buttons
            spacing=10
        )
        panel.add_widget(self.lang_section)

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
        self.color_buttons = []  # Store references to color buttons
        for color_name in color_names:
            color_value = COLOR_MAP.get(color_name.lower(), DEFAULT_COLOR)
            color_value = tuple(list(color_value[:3]) + [1])
            btn = ColorOption(color_name, color_value, callback=self.select_color, width=180)
            self.color_buttons.append(btn)
            grid.add_widget(btn)
        return grid

    def _build_lang_grid(self):
        lang_grid = gui.BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=3 * 70 + 10,
            spacing=10
        )
        
        lang_grid.add_widget(gui.Widget(size_hint_y=None, height=10))  # Spacer at the top
        # Add a label at the top of the language selection grid
        lang_grid.add_widget(gui.Label(
            text="[b]Select user language:[/b]",
            font_size=28,
            size_hint_y=None,
            height=40,
            markup=True
        ))
        ulangs = {'Spanish': 'es', 'English': 'en', 'French': 'fr'}
        for name, code in ulangs.items():
            btn = LangButton(
                name, code, callback=self.select_lang,
                size_hint=(1, None),
                height=70,
                font_size=30,
                background_color=(0.2, 0.5, 0.9, 1),
            )
            lang_grid.add_widget(btn)
        return lang_grid

    def _build_back_button(self):
        back_btn = gui.Button(
            text="Back",
            size_hint=(1, None),
            height=60,
            font_size=30,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_release=self.go_back)
        return back_btn

    def select_color(self, color_name):
        self.selected_color = color_name
        self.manager.shared_data['word_color'] = color_name
        print(f"self.manager.shared_data = {self.manager.shared_data}")
        # Disable all color buttons and their hover effect
        for btn in getattr(self, 'color_buttons', []):
            btn.disabled = True
            btn.hover_enabled = False 
        if hasattr(self, 'header_cells'):
            for cell in self.header_cells:
                cell.hover_enabled = False
        # Show language grid if not already shown
        if not self.lang_grid_added:
            self.lang_section.clear_widgets()
            self.lang_section.add_widget(gui.Label(
                text="[b]Select user language:[/b]",
                font_size=28,
                size_hint_y=None,
                height=40,
                markup=True
            ))
            ulangs = {'Spanish': 'es', 'English': 'en', 'French': 'fr'}
            for name, code in ulangs.items():
                btn = LangButton(
                    name, code, callback=self.select_lang,
                    size_hint=(1, None),
                    height=70,
                    font_size=30,
                    background_color=(0.2, 0.5, 0.9, 1),
                )
                self.lang_section.add_widget(btn)
            self.lang_grid_added = True

    def select_lang(self, ulang_short):
        self.user_lang = ulang_short
        self.manager.shared_data['user_lang'] = ulang_short
        # Proceed to next step or screen

    def detect_language_async(self):
        # Run language detection in a thread to avoid blocking UI
        import threading
        def detect():
            words_ll = pd.read_csv(self.cder_path, index_col=0, nrows=10)[self.manager.shared_data['word_color']]
            wordll_list = words_ll.dropna().to_list()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(find_language(wordll_list, min_confidence=4.0))
            loop.close()
            self.learn_lang = result
            self.manager.shared_data['learn_lang'] = result
        threading.Thread(target=detect, daemon=True).start()

    def go_back(self, instance):
        if self.lang_grid_added:
            for btn in getattr(self, 'color_buttons', []):
                btn.disabled = False
                btn.hover_enabled = True
            # Re-enable header cell hover
            if hasattr(self, 'header_cells'):
                for cell in self.header_cells:
                    cell.hover_enabled = True
            self.lang_section.clear_widgets()
            self.lang_grid_added = False
        else:
            self.manager.current = 'select_book'
