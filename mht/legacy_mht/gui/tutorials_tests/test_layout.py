from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

from skimage.io import imread
from skimage import color, img_as_ubyte
from skimage.transform import resize
from gui.kivy_multipleAnswer import show_pkm, image_to_texture

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Upper panel
        upper_panel = GridLayout(cols=3, size_hint_y=0.5)

        # Left: Label (Translate)
        upper_panel.add_widget(Label(text="Label: translate", size_hint_x=0.3))

        frame = show_pkm(nid=4)
        texture = image_to_texture(frame, )
        kivy_image = Image(texture=texture, size_hint_x=0.6)
        # kivy_image.size_hint = (1, 1) 
        upper_panel.add_widget(kivy_image,)

        # Right: Option Panel (Settings and Exit buttons)
        options_panel = GridLayout(cols=1, rows=2, size_hint_x=0.1)
        options_panel.add_widget(Button(text="Settings", background_color=(0, 1, 0, 1)))
        options_panel.add_widget(Button(text="Exit", background_color=(0, 0, 1, 1)))
        upper_panel.add_widget(options_panel, )

        self.add_widget(upper_panel)

        # Lower panel: Answers panel
        answers_panel = GridLayout(cols=2, rows=2, spacing=10, padding=10)

        for i, label_text in enumerate(['A', 'B', 'C', 'D'], start=1):
            answer_button_layout = FloatLayout()

            # Small label in the top-left corner
            small_label = Label(text=f"Label: {label_text}", size_hint=(0.2, 0.2), pos_hint={"x": 0, "y": 0.8})
            answer_button_layout.add_widget(small_label)

            # Large button filling most of the cell
            large_button = Button(text=f"Button: {label_text}", size_hint=(1, 0.8), pos_hint={"x": 0, "y": 0})
            answer_button_layout.add_widget(large_button)

            answers_panel.add_widget(answer_button_layout)

        self.add_widget(answers_panel)

class MyApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    MyApp().run()
