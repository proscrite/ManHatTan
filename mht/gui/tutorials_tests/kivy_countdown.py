from kivy.app import App
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory as F

class Timer(F.BoxLayout):
    active = F.BooleanProperty(False)
    paused = F.BooleanProperty(False)
    complete = F.BooleanProperty(False)

    # Total time, and time remaining (in seconds)
    total = F.NumericProperty(0)
    remaining = F.NumericProperty(0)

    # Angle and color for progress indicator; these are used
    # in canvas instructions in kvlang to represent the timer
    # visually. Angle is progress from 0-360.
    angle = F.BoundedNumericProperty(0, min=0, max=360)
    color = F.ListProperty([0, 1, 0, 1])

    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)
        App.get_running_app().add_timer(self)
        self.remaining = self.total

    def set_total(self, total):
        self.stop()
        self.total = self.remaining = total

    def start(self):
        if self.total:
            self.angle = 0
            self.active = True
            self.complete = False

    def stop(self):
        self.active = self.paused = self.complete = False
        self.remaining = self.total
        self.angle = 0

    def pause(self):
        if self.active:
            self.paused = True

    def resume(self):
        if self.paused:
            self.paused = False

    # Called by App every 0.1 seconds (ish)
    def _tick(self, dt):
        if not self.active or self.paused:
            return
        if self.remaining <= dt:
            self.stop()
            self.complete = True
        else:
            self.remaining -= dt
            self.angle = ((self.total - self.remaining) / self.total) * 360


Builder.load_string('''
<Timer>:
    orientation: 'vertical'
    Label:
        text: '{:.2f} remaining / {:.2f}\\nAngle: {:.2f}'.format( \
                      root.remaining, root.total, root.angle)
        canvas.before:
            Color:
                rgba: int(not root.active), int(root.active), int(root.paused), 0.5
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 1, 1, 1, 1
            Line:
                width: 3
                circle: self.center_x, self.center_y, self.width / 6.
            Color:
                rgba: root.color
            Line:
                width: 5
                circle: (self.center_x, self.center_y, \
                         self.width / 6., 0, root.angle)
    Label:
        size_hint_y: None
        height: 50
        text: root.complete and 'COMPLETE' or '(not complete)'
        color: int(not root.complete), int(root.complete), 0, 1
    BoxLayout:
        size_hint_y: None
        height: 50
        orientation: 'horizontal'
        Button:
            text: 'Start'
            on_press: root.start()
            disabled: root.active
        Button:
            text: 'Stop'
            on_press: root.stop()
            disabled: not root.active
    BoxLayout:
        size_hint_y: None
        height: 50
        orientation: 'horizontal'
        Button:
            text: 'Pause'
            on_press: root.pause()
            disabled: not root.active or root.paused
        Button:
            text: 'Resume'
            on_press: root.resume()
            disabled: not root.paused
    BoxLayout:
        size_hint_y: None
        height: 50
        orientation: 'horizontal'
        TextInput:
            id: ti
        Button:
            text: 'Set time'
            on_press: root.set_total(int(ti.text))
''')

app_KV = '''
#:import F kivy.factory.Factory

BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        id: container
        orientation: 'horizontal'
        spacing: 5
    Button:
        size_hint_y: None
        height: 50
        text: 'Add timer'
        on_press: container.add_widget(F.Timer(total=30))
'''

class TimerApp(App):
    _timers = []
    _clock = None

    def build(self):
        return Builder.load_string(app_KV)

    def add_timer(self, timer):
        self._timers.append(timer)
        if not self._clock:
            self._clock = Clock.schedule_interval(self._progress_timers, 0.1)

    def remove_timer(self, timer):
        self._timers.remove(timer)
        if not self._timers:
            self._clock.cancel()
            del self._clock

    def _progress_timers(self, dt):
        for t in self._timers:
            t._tick(dt)

TimerApp().run()
