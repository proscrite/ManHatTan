# USE_PANGO=1 ~/dev/kivy_venv/bin/python3 -m pip install --no-cache-dir . > /Users/pabloherrero/Documents/ManHatTan/mht/gui/scrapbox/logging.txt 2>&1

from kivy import Config
# must match how you launched your app:
Config.set('kivy', 'text', 'pango')    # your config key is “text” not “text_provider”

from kivy.core.text import Text

# 1) Print the configured provider name
print("Config says text provider =", Config.get('kivy', 'text'))

# 2) Inspect the actual class that was loaded
#    LabelPango → pango,  LabelSDL2 → sdl2
print("Loaded provider class  =", Text.__name__)

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/mht'
FONT_HEB = ROOT_PATH + '/data/fonts/NotoSansHebrew.ttf'

class RTLTestApp(App):
    def build(self):
        hebrew_text = "זה משפט בעברית עם כיוון ימין לשמאל. האם זה מוצג נכון?"
        box = BoxLayout()
        label = Label(
            text=hebrew_text,
            font_name=FONT_HEB,
            font_size=48,
            halign='center',
            valign='middle',
            base_direction='rtl',
            text_language='he',
            size_hint=(1, 1)
        )
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        box.add_widget(label)
        return box

if __name__ == "__main__":
    RTLTestApp().run()