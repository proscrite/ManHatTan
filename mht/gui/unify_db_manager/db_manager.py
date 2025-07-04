import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.actionbar import ActionDropDown
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.base import runTouchApp, stopTouchApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty,\
                            ObjectProperty,\
                            NumericProperty,\
                            StringProperty


import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                   NavigationToolbar2Kivy
import matplotlib.pyplot as plt

from collections import OrderedDict
import numpy as np
import pandas as pd
from googletrans import Translator
import sys
sys.path.append('../../python_scripts/')
from add_dbEntry import AddNewEntry
from common_classes import TableHeader, HeaderCell, ColumnSelectionPanel, FilterPanel
from rm_entry import RemoveEntryScreen


import datetime
from datetime import date

Builder.load_string("""

<EditableLabel>:
    canvas.before:
        Color:
            ###rgba: root.colorEven if root.is_even else root.colorOdd
            rgba: [0.23, 0.23, 0.83, 1] if root.is_even else [0.2, 0.2, 0.2, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    font_size: "12dp"
    halign: "center"
    valign: "middle"
    text_size: self.size
    size_hint: 1, 1
    height: 60
    width: 400

<ScrollCell>:
    canvas.before:
        Color:
            ###rgba: root.colorEven if root.is_even else root.colorOdd
            rgba: [0.83, 0.23, 0.23, 1] if root.is_even else [0.2, 0.2, 0.2, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    text: root.text
    font_size: "12dp"
    halign: "center"
    valign: "middle"
    text_size: self.size
    size_hint: 1, 1
    height: 60
    width: 400

<TableData>:
    rgrid: rgrid
    scroll_type: ['bars', 'content']
    bar_color: [0.2, 0.7, 0.9, 1]
    bar_inactive_color: [0.2, 0.7, 0.9, .5]
    do_scroll_x: True
    do_scroll_y: True
    effect_cls: "ScrollEffect"
    viewclass: "EditableLabel"
    RecycleGridLayout:
        id: rgrid
        rows: root.nrows
        cols: root.ncols
        size_hint: (None, None)
        width: self.minimum_width
        height: self.minimum_height


<DfguiWidget>:
    panel1: data_frame_panel
    panel2: col_select_panel
    panel3: fil_select_panel


    do_default_tab: False

    TabbedPanelItem:
        text: 'Data Frame'
        on_release: root.open_panel1()
        DataframePanel:
            id: data_frame_panel
    TabbedPanelItem:
        text: 'Columns'
        ColumnSelectionPanel:
            id: col_select_panel

    TabbedPanelItem:
        text: 'Filters'
        FilterPanel:
            id: fil_select_panel


<DataframePanel>:
    orientation: 'vertical'


<Screen1>:
    name: 'db_manager'
    RelativeLayout:
        BoxLayout:
            orientation:'vertical'
            pos_hint:{"left":0,"top":0.8}
            size:self.size
            #width: "200dp"
            #height: "200dp"

        Button:
            pos_hint:{"right":1,"top":1}
            text: 'Add new entry'
            size_hint: [0.2, 0.1]

            background_color:  [0, 0, 1,1]
            on_press: root.manager.current = 'add_dbEntry'
        Button:
            pos_hint:{"right":0.8,"top":1}
            size_hint: [0.2, 0.1]
            text: 'Back'
            on_press: root.manager.current = 'add_dbEntry' # Change to main_mht

        Button:
            text: 'Remove entry'
            pos_hint:{"right":0.6,"top":1}
            size_hint: [0.2, 0.1]
            height: 20
            background_color:  [1, 0, 0,1]
            on_press: root.manager.current = 'rm_dbEntry'

<AddNewEntry>:
    name: 'add_dbEntry'
    BoxLayout:

<RemoveEntryScreen>:
    name: 'rm_dbEntry'
    BoxLayout:
""")

class LabelEditor(TextInput):
    def on_parent(self, widget, parent):
        self.foreground_color = (255,255,192,5)
        self.background_color = (0.1, 0.1, 0.1, 1)

        self.focus = True
        self.multiline = False
        self.halign = 'center'
"""
    def none():
        self.padding_x = [self.center[0] - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0,
            0] if self.text else [self.center[0], 0]
        self.padding_y= [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
        """

class EditableLabel(Label):
    edit = BooleanProperty(False)
    is_even = BooleanProperty(None)
    is_editable = BooleanProperty(None)
    textinput = ObjectProperty(None, allownone=False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.edit and self.is_editable:
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

### Legacy: uneditable label
class ScrollCell(Label):
    text = StringProperty(None)
    is_even = BooleanProperty(None)
#    colorEven = [0, 0, 0.8, 1]
#    colorOdd = [0.2, 0.2, 0.82, 1]


class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(list_dicts[0])

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        editable_cols = ['word_ul', 'word_ll']
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            row_vals = ord_dict.values()
            cols = ord_dict.keys()

            for key, text in zip(cols, row_vals):
                is_editable = key in editable_cols
                self.data.append({'text': text, 'is_even': is_even, 'is_editable': is_editable})

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass

class Table(BoxLayout):

    def __init__(self, list_dicts=[], *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = TableHeader(list_dicts=list_dicts)
        self.table_data = TableData(list_dicts=list_dicts)
        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

class DataframePanel(BoxLayout):
    """
    Panel providing the main data frame table view.
    """
    def __init__(self, **kwargs):
        super(DataframePanel, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def populate_data(self, df):
        self.df_orig = df
        self.original_columns = self.df_orig.columns[:2]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = ['session_correct', 'session_seen', 'history_correct',
            'history_seen', 'lexeme_string', 'delta', 'timestamp']
        self.sort_key = None
        self._reset_mask()
        self._generate_table(disabled=self._disabled)

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        print('disabled = ', disabled)
        data = []
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        print('keys = ', keys)
        if sort_key is not None:
            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]
        for i1 in range(len(df.iloc[:, 0])):
            row = OrderedDict.fromkeys(keys)
            for i2, k in enumerate(keys):
                row[keys[i2]] = str(df.iloc[i1].loc[k])
            data.append(row)
        data = sorted(data, key=lambda k: k[self.sort_key])
        #print(data)
        self.add_widget(Table(list_dicts=data))

    def apply_filter(self, conditions):
        """
        External interface to set a filter.
        """
        old_mask = self.mask.copy()

        if len(conditions) == 0:
            self._reset_mask()

        else:
            self._reset_mask()  # set all to True for destructive conjunction

            no_error = True
            for column, condition in conditions:
                if condition.strip() == '':
                    continue
                condition = condition.replace("_", "self.df_orig['{}']".format(column))
                print("Evaluating condition:", condition)
                try:
                    tmp_mask = eval(condition)
                    if isinstance(tmp_mask, pd.Series) and tmp_mask.dtype == np.bool:
                        self.mask &= tmp_mask
                except Exception as e:
                    print("Failed with:", e)
                    no_error = False

        has_changed = any(old_mask != self.mask)

    def get_filtered_df(self):
        return self.df_orig.loc[self.mask, :]

    def _reset_mask(self):
        pass
        self.mask = pd.Series([True] *
                              self.df_orig.shape[0],
                              index=self.df_orig.index)

class DfguiWidget(TabbedPanel):

    def __init__(self, df, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.panel2.populate_columns(df.columns[:])
        self.panel1.populate_data(df)
        self.panel3.populate(['word_ll', 'word_ul'])
        #self.app = App.get_running_app()

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        arr = self.panel3.get_filters()
        print(str(arr))
        self.panel1.apply_filter(self.panel3.get_filters())
        print('disabled = self.panel2.get_disabled_columns() = ', self.panel2.get_disabled_columns())
        self.panel1._generate_table(disabled=
                            self.panel2.get_disabled_columns())


class ManageDB(Screen):
    def __init__(self, lippath: str, **kwargs):
        super(ManageDB, self).__init__(**kwargs)
        #App.__init__(self)
        self.lippath = lippath
        self.load_lipstick()
        #self.mainGrid = GridLayout(cols=2)


    def load_lipstick(self):
        self.lipstick = pd.read_csv(self.lippath, index_col=0)

    def build(self):
        self.mainGrid.add_widget(DfguiWidget(self.lipstick, size_hint_x=0.9, width=100))

        opGrid = GridLayout(cols=1, size_hint_x=0.1, width=10)
        backButton = Button(text='Back', size_hint_x=None, height=20, background_color=(0, 0,1, 1))
        #addEntry = AddNewEntry(size_hint_x=None, height=20, background_color=(0,1,0, 1))
        addEntry = Button(text='New \n entry', on_release=self.manager.switch_to(AddNewEntry),
            size_hint_x=None, height=20, background_color=(0, 0,1, 1))
        delEntry = Button(text='Delete \nentry', size_hint_x=None, height=20, background_color=(1, 0,0, 1))

        for b in [backButton, addEntry, delEntry]:
            opGrid.add_widget(b)
        self.mainGrid.add_widget(opGrid)

        return self.mainGrid

class Manager(App):
    def __init__(self, lippath: str, **kwargs):
        super(Manager, self).__init__(**kwargs)
        App.__init__(self)
        self.lippath = lippath
        #self.load_lipstick()
        self.lipstick = pd.read_csv(self.lippath, index_col=0)

    def build(self):
        sm = ScreenManager()

        sm.add_widget(Screen1(lippath=self.lippath))
        sm.add_widget(AddNewEntry())
        sm.add_widget(RemoveEntryScreen())
        return sm

class Screen1(Screen):
    lippath = StringProperty(None)
    def __init__(self, lippath: str, **kwargs):
        super(Screen1, self).__init__(**kwargs)
        #App.__init__(self)
        self.lippath = lippath
        self.lipstick = pd.read_csv(self.lippath, index_col=0)
        self.children[0].children[0].add_widget(Button(text='Test button', size_hint=(300, 300)) )
        #self.children[0].children[0].add_widget(DfguiWidget(self.lipstick))#, size_hint_x=0.9, width=100))
        """addEntry = Button(text='New \nentry',
            size_hint_x=None, height=20, background_color=(0, 1,0, 1),
            on_release=self.addEntryCallback())
        self.add_widget(addEntry)"""

    def addEntryCallback(self):
        print(self.parent)
        self.parent.current = 'add_dbEntry'

def manageDB_main(lippath):

    Manager(lippath=lippath).run()

if __name__ == '__main__':

  lippath = '~/Documents/ManHatTan/LIPSTICK/Die_Verwandlung.lip'
  # For testing
  manageDB_main(lippath)
