from kivy import Config
# MUST come before any other kivy import:
Config.set('kivy', 'text', 'pango')
# use the “mock” window so we don’t hit sdl2/GL at all
Config.set('kivy', 'window', 'mock')

from kivy.core.text import Label as CoreLabel

# this should exercise only the pango plugin and then exit cleanly
lbl = CoreLabel(text='שלום', font_size=72)
lbl.refresh()
print('Got texture size:', lbl.texture.size)