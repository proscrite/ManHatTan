from mht import gui
from mht.gui.book_processor.screen_choose_color import ChooseColorScreen
from mht.gui.common import PATH_KINDLES, PATH_PLAYBOOKS, PATH_GOOGLE_TRANSL
from glob import glob
import os

from mht.scripts import krahtos_main, rashib_main, gost_main


class BookButton(gui.Button):
    def __init__(self, filename, path, callback, **kwargs):
        ext = os.path.splitext(path)[1].lower()
        color = self._get_color_by_extension(ext)
        super().__init__(
            text=filename,
            size_hint_y=None,
            height=100,
            font_size=32,
            background_normal='',
            background_color=(0, 0, 0, 0),
            halign='center',
            valign='middle',
            markup=True,
            **kwargs
        )
        self.path = path
        self.callback = callback
        self.bind(size=self._update_text_size)
        with self.canvas.before:
            self.bg_color = gui.Color(*color)
            self.bg_rect = gui.RoundedRectangle(size=self.size, pos=self.pos, radius=[18])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def _get_color_by_extension(self, ext):
        if ext == '.docx':
            color = (0.2, 0.4, 0.8, 1)   # Blue
        elif ext == '.html':
            color = (1, 0.5, 0.1, 1)     # Orange
        elif ext == '.csv':
            color = (0.2, 0.7, 0.3, 1)   # Green
        else:
            color = (0.25, 0.25, 0.25, 1)  # Default gray
        return color

    def _update_text_size(self, *args):
        self.text_size = (self.width - 20, None)

    def update_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_release(self, *args):
        self.bg_color.rgba = (0.1, 0.5, 0.1, 1)
        self.disabled = True
        self.text = f"[b]{self.text}[/b]"
        self.markup = True
        if self.callback:
            self.callback(self.path)

class LegendItem(gui.BoxLayout):
    def __init__(self, color, label_text, **kwargs):
        super().__init__(
            orientation='horizontal',
            spacing=10,
            size_hint_x=None,
            width=240,  # Increased width for larger font/box
            height=36,
            **kwargs
        )
        color_box = gui.Widget(size_hint=(None, None), size=(32, 32))
        with color_box.canvas:
            gui.Color(*color)
            self.rect = gui.RoundedRectangle(pos=color_box.pos, size=color_box.size, radius=[6])
        color_box.bind(pos=self.update_rect, size=self.update_rect)
        self.add_widget(color_box)
        label = gui.Label(
            text=label_text,
            font_size=24,
            size_hint_x=None,
            width=220,
            color=(1,1,1,1),
            halign='left',
            valign='middle'
        )
        label.bind(size=lambda inst, _: setattr(inst, 'text_size', inst.size))
        self.add_widget(label)

    def update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SelectBookScreen(gui.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = gui.BoxLayout(orientation='vertical', padding=20, spacing=10)
        main_layout.add_widget(self._build_header())
        main_layout.add_widget(self._build_book_grid())
        main_layout.add_widget(self._build_footer())
        self.add_widget(main_layout)
        self.selected_path = None

    def _build_header(self):
        return gui.Label(
            text="[b]Select book to process[/b]",
            font_size=36,
            size_hint_y=None,
            height=100,
            markup=True
        )

    def _build_book_grid(self):
        scroll = gui.ScrollView(size_hint=(1, 1))
        self.grid = gui.GridLayout(cols=2, spacing=14, size_hint_y=None, padding=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        return scroll

    def _build_footer(self):
        footer = gui.BoxLayout(size_hint_y=None, height=90, spacing=10, padding=[0, 0, 20, 0])
        # Change orientation to 'vertical' for the legend
        legend = gui.BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=240,  # Match LegendItem width
            spacing=10,
            padding=[10, 0, 0, 0]
        )
        legend_items = [
            ((0.2, 0.4, 0.8, 1), 'PlayBook'),      # Blue
            ((1, 0.5, 0.1, 1), 'Kindle'),          # Orange
            ((0.2, 0.7, 0.3, 1), 'Google Translate DB'),  # Green
        ]
        for color, label_text in legend_items:
            legend.add_widget(LegendItem(color, label_text))
        footer.add_widget(legend)
        footer.add_widget(gui.Label())  # Spacer
        exit_btn = gui.Button(
            text="Exit",
            size_hint_x=None,
            width=120,
            size_hint_y=None,
            height=90,
            background_color=(0.3, 0.2, 0.2, 1),
            font_size=24
        )
        exit_btn.bind(on_release=self.exit_app)
        footer.add_widget(exit_btn)
        return footer

    def on_pre_enter(self):
        self.grid.clear_widgets()
        books_full = glob(PATH_KINDLES) + glob(PATH_PLAYBOOKS) + glob(PATH_GOOGLE_TRANSL)
        for b in books_full:
            filename = os.path.splitext(os.path.basename(b))[0]
            btn = BookButton(filename, b, callback=self.select_book)
            self.grid.add_widget(btn)

    def select_book(self, path):

        self.manager.shared_data['filename'] = path
        filepath, basename = os.path.split(path)
        flag_needs_processing = True

        if '.html' in basename:
            print('Amazon Kindle file detected')
            cder_path = krahtos_main(path)
        elif '.docx' in basename:
            print('Google Books file detected')
            cder_path = rashib_main(path)
        elif '.csv' in basename:
            print('Google Saved Translations detected')
            flag_needs_processing = False
            # You may need to get dest_lang and src_lang from user or config
            gota_df = gost_main(path, dest_lang, src_lang)
            print("Done! Now you can start practicing")
            # Optionally, jump to practice screen here
            return

        if flag_needs_processing:
            assert '.cder' in cder_path, "Wrong CADERA extension"
            self.manager.shared_data['cder_path'] = cder_path

            # Remove old choose_color screen if it exists
            if self.manager.has_screen('choose_color'):
                self.manager.remove_widget(self.manager.get_screen('choose_color'))
            print(f"Selected CADERA book path: {cder_path}")
            self.manager.add_widget(
                ChooseColorScreen(name='choose_color', cder_path=cder_path)
            )
            self.manager.current = 'choose_color'

    def exit_app(self, instance):
        gui.App.get_running_app().stop()


class BookProcessorScreenManager(gui.ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shared_data = {}  # Dict to pass data between screens

class BookProcessorApp(gui.App):
    def build(self):
        self.sm = BookProcessorScreenManager()
        self.sm.add_widget(SelectBookScreen(name='select_book'))
        # self.sm.add_widget(ChooseColorScreen(name='choose_color', cder_path=self.sm.shared_data.get('cder_path', '')))
        # self.sm.add_widget(ChooseLangScreen(name='choose_lang'))
        # Add more screens as needed
        self.sm.current = 'select_book'
        return self.sm
    
if __name__ == '__main__':
    BookProcessorApp().run()