from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView

Builder.load_string("""

<ExampleRV>:

    viewclass : 'Button'
    RecycleBoxLayout:
        size_hint_y: None
        heigh: self.minimum_height
        orientation: 'vertical'

""")

class ExampleRV(RecycleView):
    def __init__(self, **kwargs):
        super(ExampleRV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(20)]

class RecycleApp(App):
    def build(self):
        return ExampleRV()

RecycleApp().run()
