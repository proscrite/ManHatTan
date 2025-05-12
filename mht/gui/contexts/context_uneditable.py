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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import BooleanProperty,\
                            ObjectProperty,\
                            NumericProperty,\
                            StringProperty

from collections import OrderedDict
import apertium
import re
import sys
sys.path.append('../python_scripts/')
from bulkTranslate import *

from googletrans import Translator
from contexter import *


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

<ScrollCell>:
    canvas.before:
        Color:
            #rgba: root.colorEven if root.is_even else root.colorOdd
            rgba: [root.green_val, 0., abs(root.green_val-0.73), 1] if root.is_even else [root.green_val, 0., abs(root.green_val-0.83), 1]
            ##rgba: [0.23, 0.23, 0.83, 1] if root.is_even else [0.2, 0.2, 0.72, 1]

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
    #bar_color: [0.2, 0.7, 0.9, 1]
    #bar_inactive_color: [0.2, 0.7, 0.9, .5]
    do_scroll_x: True
    do_scroll_y: True
    effect_cls: "ScrollEffect"
    viewclass: "ScrollCell"
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
""")

class HeaderCell(Button):
    def __init__(self, *args, **kwargs):
        super(HeaderCell, self).__init__(*args, **kwargs)
        if self.text == 'blue':
            color = [0, 0, 0.8, 1]
        else:
            color = [0.165, 0.165, 0.165, 1]

class ScrollCell(Label):
    text = StringProperty(None)
    is_even = BooleanProperty(None)
    green_val = NumericProperty(0.)
    colorEven = ListProperty([0.2, 0.2, 0.8, 1])
    colorOdd = ListProperty([0.2, 0.2, 0.7, 1])

    """def __init__(self, *args, **kwargs):
        super(ScrollCell, self).__init__(*args, **kwargs)
        self.colorEven = [0, 0, 0.8, 1]
        self.colorOdd = [0.2, 0.2, 0.82, 1]
        self.color = [0.2, green_val, 0.82, 1]"""

class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, list_dicts=None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        titles = list_dicts[0].keys()
        print('In TableHeader, titles =', titles)
        for title in titles:
            self.header.add_widget(HeaderCell(text=title))

class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], color_map=[], *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(list_dicts[0])

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        #print('list_dicts: \n', list_dicts)
        #print('color_map: \n', color_map)
        for i, (ord_dict, col_dict) in enumerate(zip(list_dicts, color_map)):
            is_even = i % 2 == 0
            row_vals = ord_dict.values()
            row_cols = col_dict.values()

            for text, green_val in zip(row_vals, row_cols):
                if text == 'None':
                    text = ''

                self.data.append({'text': text, 'is_even': is_even, 'green_val':green_val})

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass

class Table(BoxLayout):

    def __init__(self, list_dicts=[], color_map=[], *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = TableHeader(list_dicts=list_dicts)
        self.table_data = TableData(list_dicts=list_dicts, color_map=color_map)

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

    def populate_data(self, df, dfaux):
        self.df_orig = df
        self.dfaux = dfaux
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = []#'en', 'kwen0', 'kwen1']
        self.sort_key = None
        self._reset_mask()
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        dfaux = self.dfaux
        data = []
        datacolor = []
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        colorkeys = [x for x in dfaux.columns[:] if x not in self._disabled]

        if sort_key is not None:

            self.app.set_word_col(sort_key)   # Process column from selected color

            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]
        for i1 in range(len(df.iloc[:, 0])):
            row = OrderedDict.fromkeys(keys)
            rowc = OrderedDict.fromkeys(colorkeys)

            for i2 in range(len(keys)):
                row[keys[i2]] = str(df.iloc[i1, i2])
                rowc[colorkeys[i2]] = float(dfaux.iloc[i1, i2])
            data.append(row)
            datacolor.append(rowc)

        data = sorted(data, key=lambda k: k[self.sort_key])
        self.add_widget(Table(list_dicts=data, color_map=datacolor))

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

class ColumnSelectionPanel(BoxLayout):
    """
    Panel for selecting and re-arranging columns.
    """

    def populate_columns(self, columns):
        """
        When DataFrame is initialized, fill the columns selection panel.
        """
        default_cols = ['word_ll', 'word_ul', 'context']
        self.col_list.bind(minimum_height=self.col_list.setter('height'))
        for col in columns:
            if col in default_cols:
                self.col_list.add_widget(ToggleButton(text=col, state='down'))
            else:
                self.col_list.add_widget(ToggleButton(text=col, state='normal'))

    def get_disabled_columns(self):
        return [x.text for x in self.col_list.children if x.state != 'down']


class DfguiWidget(TabbedPanel):

    def __init__(self, df, dfaux, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.dfaux = dfaux
        self.panel1.populate_data(df, dfaux)
        self.panel2.populate_columns(df.columns[:])
        #self.app = App.get_running_app()

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        #arr = self.panel3.get_filters()
        #print(str(arr))
        #self.panel1.apply_filter(self.panel3.get_filters())
        self.panel1._generate_table(disabled=
                                    self.panel2.get_disabled_columns())


class ContextEditor(App):
    def __init__(self, lippath: str, **kwargs):
        super(ContextEditor, self).__init__(**kwargs)
        App.__init__(self)
        self.lippath = lippath
        self.load_lipstick()

    def load_lipstick(self):
        dest_lang = 'en'
        src_lang = 'it'
        ctx = pd.read_csv(self.lippath, index_col=0)
        splitCtx = ctx['it'].str.split()
        self.lipstick = pd.DataFrame.from_records(list(splitCtx))
        self.lipstick.columns = ['it'+str(i) for i in self.lipstick.columns]

        self.pdf = pd.read_csv('~/Documents/ManHatTan/LIPSTICK/Io_Uccido_pdf.ctx', index_col=0)

    def build(self):
        mainGrid = GridLayout(cols=2)

        mainGrid.add_widget(DfguiWidget(self.lipstick, self.pdf, size_hint_x=0.9, width=100))

        opGrid = GridLayout(cols=1, size_hint_x=0.1, width=10)

        return mainGrid

    def modify_lip(self, entry_before: str, edited_entry: str):
        print('Modifying lipstick term:', entry_before )
        if entry_before in self.lipstick.word_ll.values:
            self.lipstick.set_index('word_ll', inplace=True, drop=False)
            self.lipstick.loc[entry_before, 'word_ll'] = edited_entry
        elif entry_before in self.lipstick.word_ul.values:
            self.lipstick.set_index('word_ul', inplace=True, drop=False)
            self.lipstick.loc[entry_before, 'word_ul'] = edited_entry
        else:
            print('Error: edited entry is not word_ll or word_ll...')

    def saveNexit(self, instance):
        #self.lipstick.to_csv(self.lippath, index=False)
        App.stop(self)


def context_editor_main(lippath : str):#, word_color: str, dest_lang : str, src_lang : str):
    CTX = ContextEditor(lippath)
    CTX.run()

if __name__ == '__main__':

  lippath = '~/Documents/ManHatTan/LIPSTICK/Io_Uccido_temp.ctx'
  auxpath = '~/Documents/ManHatTan/LIPSTICK/Io_Uccido_pdf.ctx'
  #lippath = sys.argv[1]
  # For testing
  context_editor_main(lippath)
