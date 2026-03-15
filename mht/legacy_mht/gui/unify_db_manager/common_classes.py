from kivy.lang import Builder
from kivy.properties import BooleanProperty,\
                            ObjectProperty,\
                            NumericProperty,\
                            StringProperty

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput



Builder.load_string("""

<HeaderCell>
    size_hint: (None, None)
    text_size: self.size
    halign: "center"
    valign: "middle"
    height: '30dp'
    background_disabled_normal: ''
    disabled_color: (1, 1, 1, 1)
    canvas.before:
        Color:
            #rgba: 0.165, 0.165, 0.165, 1
            rgba: root.color

        Rectangle:
            pos: self.pos
            size: self.size
    on_release: root.parent.parent.parent.parent._generate_table(self.text)

<TableHeader>:
    header: header
    bar_width: 0
    do_scroll: False
    size_hint: (1, None)
    effect_cls: "ScrollEffect"
    height: '30dp'
    GridLayout:
        id: header
        rows: 1
        size_hint: (None, None)
        width: self.minimum_width
        height: self.minimum_height

<ColumnSelectionPanel>:
    col_list: col_list
    orientation: 'vertical'
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        size_hint: 1, 1
        scroll_timeout: 150
        GridLayout:
            id: col_list
            padding: "10sp"
            spacing: "5sp"
            cols:1
            row_default_height: '55dp'
            row_force_default: True
            size_hint_y: None

<FilterPanel>:
    filter_list: filter_list
    orientation: 'vertical'
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        size_hint: 1, 1
        scroll_timeout: 150
        GridLayout:
            id: filter_list
            padding: "10sp"
            spacing: "5sp"
            cols:1
            row_default_height: '55dp'
            row_force_default: True
            size_hint_y: None

""")

class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, list_dicts=None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        titles = list_dicts[0].keys()

        for title in titles:
            self.header.add_widget(HeaderCell(text=title))

class HeaderCell(Button):
    def __init__(self, *args, **kwargs):
        super(HeaderCell, self).__init__(*args, **kwargs)
        if self.text == 'blue':
            color = [0, 0, 0.8, 1]
        else:
            color = [0.165, 0.165, 0.165, 1]


class ColumnSelectionPanel(BoxLayout):
    """
    Panel for selecting and re-arranging columns.
    """

    def populate_columns(self, columns):
        """
        When DataFrame is initialized, fill the columns selection panel.
        """
        default_cols = ['user_id', 'learning_language', 'ui_language', 'word_ll', 'word_ul', 'p_pred']
        self.col_list.bind(minimum_height=self.col_list.setter('height'))
        for col in columns:
            if col in default_cols:
                self.col_list.add_widget(ToggleButton(text=col, state='down'))
            else:
                self.col_list.add_widget(ToggleButton(text=col, state='normal'))

    def get_disabled_columns(self):
        return [x.text for x in self.col_list.children if x.state != 'down']


class FilterPanel(BoxLayout):

    def populate(self, columns):
        self.filter_list.bind(minimum_height=self.filter_list.setter('height'))
        for col in columns:
            self.filter_list.add_widget(FilterOption(columns, col))

    def get_filters(self):
        result=[]
        for opt_widget in self.filter_list.children:
            if opt_widget.is_option_set():
                result.append(opt_widget.get_filter())
        return [x.get_filter() for x in self.filter_list.children
                if x.is_option_set]

class FilterOption(BoxLayout):

    def __init__(self, columns, col, **kwargs):
        super(FilterOption, self).__init__(**kwargs)
        self.height="30sp"
        self.size_hint=(0.9, None)
        self.spacing=10
        """options = ["Select Column"]
        options.extend(columns)
        self.spinner = Spinner(text='Select Column',
                               values= options,
                               size_hint=(0.25, None),
                               height="30sp",
                               pos_hint={'center_x': .5, 'center_y': .5})"""

        self.spinner = Label(text=col, size_hint=(0.25, None),\
                            height="30sp", pos_hint={'center_x': .5, 'center_y': .5})
        self.txt = TextInput(multiline=False, size_hint=(0.75, None),\
                             font_size="15sp")
        self.txt.bind(minimum_height=self.txt.setter('height'))
        self.add_widget(self.spinner)
        self.add_widget(self.txt)

    def is_option_set(self):
        return self.spinner.text != 'Select Column'

    def get_filter(self):
        return (self.spinner.text, self.txt.text)
