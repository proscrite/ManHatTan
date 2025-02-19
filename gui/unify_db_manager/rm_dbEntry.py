import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.actionbar import ActionDropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.base import runTouchApp, stopTouchApp
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
import sys
from functools import partial
from collections import OrderedDict
import numpy as np
import pandas as pd
from googletrans import Translator

import datetime
from datetime import date

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

<ScrollButton>:
    canvas.before:
        Color:
            ###rgba: root.colorEven if root.is_even else root.colorOdd
            rgba: [0.23, 0.23, 0.23, 1] if root.is_even else [0.2, 0.2, 0.2, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    text: root.text
    row: root.row
    font_size: "12dp"
    halign: "center"
    valign: "middle"
    text_size: self.size
    size_hint: 1, 1
    height: 60
    width: 400
    on_release: root.parent.parent.parent.parent.parent.parent._remove_entry(self.row)

<TableData>:
    rgrid: rgrid
    scroll_type: ['bars', 'content']
    bar_color: [0.2, 0.7, 0.9, 1]
    bar_inactive_color: [0.2, 0.7, 0.9, .5]
    do_scroll_x: True
    do_scroll_y: True
    effect_cls: "ScrollEffect"
    viewclass: "ScrollButton"
    RecycleGridLayout:
        id: rgrid
        rows: root.nrows
        cols: root.ncols
        size_hint: (None, None)
        width: self.minimum_width
        height: self.minimum_height


<DfguiRemove>:
    panel1: fil_select_panel
    panel2: data_frame_panel
    panel3: col_select_panel

    do_default_tab: False

    TabbedPanelItem:
        text: 'Filters'
        FilterPanel:
            id: fil_select_panel

    TabbedPanelItem:
        text: 'Data Frame'
        on_release: root.open_panel2()
        DataframePanel:
            id: data_frame_panel
    TabbedPanelItem:
        text: 'Columns'
        ColumnSelectionPanel:
            id: col_select_panel


<DataframePanel>:
    orientation: 'vertical'

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

class HeaderCell(Button):
    def __init__(self, *args, **kwargs):
        super(HeaderCell, self).__init__(*args, **kwargs)
        if self.text == 'blue':
            color = [0, 0, 0.8, 1]
        else:
            color = [0.165, 0.165, 0.165, 1]

class ScrollButton(Button):
    text = StringProperty(None)
    col = StringProperty(None)
    is_even = BooleanProperty(None)
#    colorEven = [0, 0, 0.8, 1]
#    colorOdd = [0.2, 0.2, 0.82, 1]

class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, list_dicts=None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        titles = list_dicts[0].keys()

        for title in titles:
            self.header.add_widget(HeaderCell(text=title))

class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(list_dicts[0])

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            row_vals = ord_dict.values()
            #cols = ord_dict.keys()
            for text in row_vals:
                self.data.append({'text': text, 'is_even': is_even, 'row': ord_dict})

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
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = []
        self.sort_key = None
        self._reset_mask()
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        data = []
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        if sort_key is not None:

            self.app.set_word_col(sort_key)   # Process column from selected color

            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]
        for i1 in range(len(df.iloc[:, 0])):
            row = OrderedDict.fromkeys(keys)
            for i2 in range(len(keys)):
                row[keys[i2]] = str(df.iloc[i1, i2])
            data.append(row)
        data = sorted(data, key=lambda k: k[self.sort_key])
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

                #condition = condition.replace("_", "self.df_orig['{}']".format(column))
                condition = ''.join("self.df_orig['{}'] == '{}'".format(column, condition))
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

class ColumnSelectionPanel(BoxLayout):
    """
    Panel for selecting and re-arranging columns.
    """

    def populate_columns(self, columns):
        """
        When DataFrame is initialized, fill the columns selection panel.
        """
        self.col_list.bind(minimum_height=self.col_list.setter('height'))
        for col in columns:
            self.col_list.add_widget(ToggleButton(text=col, state='down'))

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



class DfguiRemove(TabbedPanel):

    def __init__(self, df, **kwargs):
        super(DfguiRemove, self).__init__(**kwargs)
        self.df = df
        self.panel1.populate(['word_ll', 'word_ul'])
        self.panel2.populate_data(df)
        self.panel3.populate_columns(df.columns[:])
        #self.app = App.get_running_app()

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel2(self):
        arr = self.panel1.get_filters()
        print(str(arr))
        self.panel2.apply_filter(self.panel1.get_filters())
        self.panel2._generate_table(disabled=
                                    self.panel3.get_disabled_columns())

    def _remove_entry(self, row):
        self.df.set_index('word_ll', drop=False, inplace=True)
        self.rmIndex = row['word_ll']
        print(self.df.loc[self.rmIndex], 'is going to be removed')
        self._confirmPop(self.df.loc[self.rmIndex])

    def _confirmPop(self, entry: pd.Series):
        #print('entry[word_ll] = ', entry['word_ll'])
        confirmPop = GridLayout(cols=1, padding=10)
        twoCols1 = GridLayout(cols=2)
        twoCols2 = GridLayout(cols=2)

        lbWordLearn = Button(text=entry['word_ll'], background_color=(0, 0, 1, 1))
        lbWordInput = Button(text=entry['word_ul'], background_color=(0, 0, 1, 1))
        twoCols1.add_widget(lbWordLearn)
        twoCols1.add_widget(lbWordInput)

        writeLip_callback = partial(self.writeLip)
        label2 = Label(text='Are you sure you want to continue?')
        confirm = Button(text='Confirm', on_release=self.writeLip, background_color=(0,1,0,1))
        cancel = Button(text='Cancel', on_release=lambda x: self.popConfirm.dismiss(), background_color=(1,0,0,1))
        twoCols2.add_widget(cancel)
        twoCols2.add_widget(confirm)

        confirmPop.add_widget(twoCols1)
        confirmPop.add_widget(label2)
        confirmPop.add_widget(twoCols2)

        self.popConfirm = Popup(content=confirmPop, title='You are about to delete the following entry:')
        self.popConfirm.open()

    def writeLip(self, instance):
        self.df.drop(self.rmIndex, inplace=True)
        # self.df.to_csv(app.lippath) # Maybe in RemoveEntry?
        print(self.rmIndex, ' was removed')
        self.df.reset_index(drop=True, inplace=True)
        self.panel2._reset_mask()
        self.panel2._generate_table(disabled=[])
                                    #self.panel3.get_disabled_columns())
        self.popConfirm.dismiss()


class RemoveEntry(App):
    def __init__(self, lippath: str, **kwargs):
        super(RemoveEntry, self).__init__(**kwargs)
        App.__init__(self)
        self.word_color: str
        self.lippath = lippath


    def build(self):
        self.lipstick = pd.read_csv(self.lippath, index_col=0)
        self.lipstick.set_index('word_ll', drop=False, inplace=True)
        mainGrid = GridLayout(cols=2)

        boxDf = BoxLayout(orientation='vertical')
        boxDf.add_widget(DfguiRemove(self.lipstick))
        mainGrid.add_widget(boxDf)

        return mainGrid

    def run(self):
        super().run()
        return self.word_color

def reset():
    if not EventLoop.event_listeners:
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}


def remove_entry_main(lippath):
    reset()
    stopTouchApp()
    RE = RemoveEntry(lippath)
    word_rm = RE.run()
    print('Filter color =', word_rm)
    return word_color

if __name__ == '__main__':

    #lippath = '~/Documents/ManHatTan/LIPSTICK/Il_castello_dei_destini_incrociati.lip'
    lippath = sys.argv[1]
    remove_entry_main(lippath)

    #word_color = DFA.retrieve_word_col()
