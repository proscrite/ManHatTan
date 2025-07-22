from mht import gui
from mht.gui.book_processor.kivy_cadera_DfWidget import DfguiWidget
from mht.scripts import init_lipstick_main
import pandas as pd
import os

class ShowDBScreen(gui.Screen):
    """
    Screen to display a .got file as a table (first two columns only).
    Right panel: Continue and Back buttons.
    """
    def __init__(self, got_path, back_callback, **kwargs):
        super().__init__(**kwargs)
        self.got_path = got_path
        self.back_callback = back_callback

        self.main_layout = gui.BoxLayout(orientation='horizontal', spacing=30, padding=30)
        self.left_panel = self._build_left_panel()
        self.right_panel = self._build_right_panel()

        self.main_layout.add_widget(self.left_panel)
        self.main_layout.add_widget(self.right_panel)
        self.add_widget(self.main_layout)

    def _build_left_panel(self):
        # Load .got file, skip index column, show only first two columns
        gota = pd.read_csv(self.got_path)
        # Remove index column if present (first column is unnamed or numeric)
        if gota.columns[0].startswith('Unnamed') or gota.columns[0] == '' or gota.columns[0] == gota.index.name:
            gota = gota.iloc[:, 1:]
        # Only keep first two columns
        gota = gota.iloc[:, :2]

        panel = gui.BoxLayout(orientation='vertical', size_hint_x=0.7, spacing=10)
        panel.add_widget(gui.Label(
            text="[b]Preview of word pairs[/b]",
            font_size=22,
            size_hint_y=None,
            height=40,
            markup=True
        ))
        scroll = gui.ScrollView(size_hint=(1, 1))

        gota_widget = DfguiWidget(gota, col_width=250, header_callback=None)
        scroll.add_widget(gota_widget)
        # grid = gui.GridLayout(cols=2, size_hint_y=None, spacing=8, padding=8)
        # grid.bind(minimum_height=grid.setter('height'))

        # # Add header
        # for col in gota.columns:
        #     grid.add_widget(gui.Label(text=f"[b]{col}[/b]", font_size=20, markup=True, size_hint_y=None, height=32))

        # # Add rows
        # for idx, row in gota.iterrows():
        #     grid.add_widget(gui.Label(text=str(row.iloc[0]), font_size=18, size_hint_y=None, height=28))
        #     grid.add_widget(gui.Label(text=str(row.iloc[1]), font_size=18, size_hint_y=None, height=28))

        # scroll.add_widget(grid)
        panel.add_widget(scroll)
        return panel

    def _build_right_panel(self):
        panel = gui.BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=20, padding=[0, 80, 0, 80])
        btn_continue = gui.Button(
            text="Continue",
            font_size=26,
            size_hint=(1, None),
            height=70,
            on_release=self.on_continue
        )
        btn_back = gui.Button(
            text="Back",
            font_size=26,
            size_hint=(1, None),
            height=70,
            on_release=self.on_back
        )
        panel.add_widget(btn_continue)
        panel.add_widget(btn_back)
        return panel

    def on_continue(self, instance):
        init_lipstick_main(self.got_path)
        self.manager.transition = gui.SlideTransition(direction="right")
        self.manager.current = "main_menu"

    def on_back(self, instance):
        if self.manager.has_screen('choose_color_lang'):
            self.manager.current = 'choose_color_lang'
        else:
            self.manager.current = 'process_book'