from kivy.app import App
from kivy.uix.gridlayout import GridLayout

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty, ObjectProperty

__all__ = ('EditableLabel', )

class LabelEditor(TextInput):
    def on_parent(self, widget, parent):
        self.focus = True
        self.multiline = False
        self.halign = 'center'
        self.padding_x = [self.center[0] - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0,
            0] if self.text else [self.center[0], 0]
        self.padding_y= [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]


class EditableLabel(Label):
    edit = BooleanProperty(False)
    textinput = ObjectProperty(None, allownone=True)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit:
            self.edit = True
        return super(EditableLabel, self).on_touch_down(touch)

    def on_edit(self, instance, value):
        if not value:
            if self.textinput:
                self.remove_widget(self.textinput)

            return
        self.textinput = t = LabelEditor(
            text = self.text[0],
            pos = self.pos,
            size = self.size)

        self.bind(pos=t.setter('pos'), size=t.setter('size'))
        self.add_widget(self.textinput)
        t.bind(on_text_validate=self.on_text_validate, focus=self.on_text_focus)

    def on_text_validate(self, instance):
        self.text = instance.text
        self.edit = False

    def on_text_focus(self, instance, focus):
        if focus is False:
            self.text = instance.text
            self.edit = False


class ManhattanMain(App):
    def __init__(self):
        App.__init__(self)
        self.grid = GridLayout(cols=2)

    def build(self):
        edLabel = EditableLabel(text='Write here')
        #edLabel = Label(text='Write here')
        self.grid.add_widget(edLabel)
        return self.grid

if __name__ == '__main__':
    MM = ManhattanMain()
    MM.run()
