from kivy.app import App
from mht import gui
from mht.gui.common import COLOR_MAP, DEFAULT_COLOR
import os
from collections import OrderedDict
import numpy as np
import pandas as pd

kv_path = os.path.join(os.path.dirname(__file__), "kivy_cadera_constructor.kv")
gui.Builder.load_file(kv_path)


def blend_colors(color1, color2, alpha):
    """Blend two RGBA colors by alpha (0-1)."""
    return tuple([
        color1[i] * (1 - alpha) + color2[i] * alpha
        for i in range(3)
    ] + [1])


class HoverBehavior(object):
    hovered = gui.BooleanProperty(False)
    border_point = gui.ListProperty([0,0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        gui.Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        self.hovered = inside


class HeaderCell(gui.Button, HoverBehavior):
    bg_color = gui.ListProperty([1, 1, 1, 1])
    hover_color = gui.ListProperty([1, 1, 1, 1])
    down_color = gui.ListProperty([1, 1, 1, 1])
    hover_scale = gui.NumericProperty(1.0)  # <-- Add this line

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set hover and down colors based on bg_color
        self.hover_color = [min(1, c + 0.15) for c in self.bg_color[:3]] + [1]
        self.down_color = [max(0, c - 0.15) for c in self.bg_color[:3]] + [1]
        self.bind(hovered=self.on_hover)
        self.bind(state=self.on_state)

    def on_hover(self, instance, value):
        if value:
            self.bg_color = self.hover_color
            self.hover_scale = 1.08  # Grow by 8%
        else:
            self.bg_color = self.original_color if hasattr(self, 'original_color') else self.bg_color
            self.hover_scale = 1.0

    def on_state(self, instance, value):
        if value == 'down':
            self.bg_color = self.down_color
        elif self.hovered:
            self.bg_color = self.hover_color
        else:
            self.bg_color = self.original_color if hasattr(self, 'original_color') else self.bg_color

    def on_bg_color(self, instance, value):
        # Store the original color for restoring
        if not hasattr(self, 'original_color'):
            self.original_color = value[:]


class ScrollCell(gui.Label):
    text = gui.StringProperty(None)
    is_even = gui.BooleanProperty(None)
    colorEven = [0, 0, 0.8, 1]
    colorOdd = [0.2, 0.2, 0.82, 1]
    width = gui.NumericProperty(160)
    size_hint_x = gui.ObjectProperty(None)

class TableHeader(gui.ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = gui.ObjectProperty(None)

    def __init__(self, list_dicts=None, col_width=160, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)
        titles = list_dicts[0].keys()
        for title in titles:
            color = COLOR_MAP.get(title.lower(), DEFAULT_COLOR)
            self.header.add_widget(HeaderCell(text=title, width=col_width, size_hint_x=None, bg_color=color))

class TableData(gui.RecycleView):
    nrows = gui.NumericProperty(None)
    ncols = gui.NumericProperty(None)
    rgrid = gui.ObjectProperty(None)

    def __init__(self, list_dicts=[], col_width=160, *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(list_dicts[0])
        super(TableData, self).__init__(*args, **kwargs)
        self.data = []
        col_names = list(list_dicts[0].keys())
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            for j, (col, text) in enumerate(ord_dict.items()):
                base_color = COLOR_MAP.get(col.lower(), DEFAULT_COLOR)
                gray_even = (0.23, 0.23, 0.23, 1)
                gray_odd = (0.2, 0.2, 0.2, 1)
                # Blend: 70% base color, 30% gray
                blend = blend_colors(base_color, gray_even if is_even else gray_odd, 0.7)
                self.data.append({'text': text, 'is_even': is_even, 'width': col_width, 'size_hint_x': None, 'bg_color': blend})

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass

class Table(gui.BoxLayout):

    def __init__(self, list_dicts=[], col_width=160, *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.halign = "center"

        self.header = TableHeader(list_dicts=list_dicts, col_width=col_width)
        self.table_data = TableData(list_dicts=list_dicts, col_width=col_width)

        # self.table_data.bind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

class DataframePanel(gui.BoxLayout):
    """
    Panel providing the main data frame table view.
    """
    def __init__(self, **kwargs):
        super(DataframePanel, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def populate_data(self, df, col_width=160):
        self.df_orig = df
        self.col_width = col_width
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = ['session_correct', 'session_seen', 'history_correct',
            'history_seen', 'lexeme_string', 'delta', 'timestamp']
        self.sort_key = None
        self._reset_mask()
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        if sort_key is not None:
            self.app.set_word_col(sort_key)
            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]

        col_data, max_len = self._prepare_column_data(df, keys)
        self._pad_columns(col_data, max_len)
        data = self._build_row_data(col_data, keys, max_len)
        self.add_widget(Table(list_dicts=data, col_width=self.col_width))

    def _prepare_column_data(self, df, keys):
        """Sort each column so non-NaN at top, NaN ('-') at bottom. Return col_data dict and max_len."""
        col_data = {}
        max_len = 0
        for col in keys:
            col_series = df[col].fillna('-')
            sorted_col = sorted(col_series, key=lambda x: x == '-')
            col_data[col] = sorted_col
            if len(sorted_col) > max_len:
                max_len = len(sorted_col)
        return col_data, max_len

    def _pad_columns(self, col_data, max_len):
        """Pad columns with '-' so all columns have the same length."""
        for col in col_data:
            if len(col_data[col]) < max_len:
                col_data[col] += ['-'] * (max_len - len(col_data[col]))

    def _build_row_data(self, col_data, keys, max_len):
        """Build row-wise data for the table, truncating long entries."""
        data = []
        for i in range(max_len):
            row = OrderedDict()
            for col in keys:
                val = str(col_data[col][i])
                if len(val) > 40:
                    space_idx = val.find(' ', 40)
                    if space_idx != -1:
                        val = val[:space_idx] + "(...)"
                    else:
                        val = val[:50] + "(...)"
                row[col] = val
            data.append(row)
        return data

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

class ColumnSelectionPanel(gui.BoxLayout):
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
                self.col_list.add_widget(gui.ToggleButton(text=col, state='down'))
            else:
                self.col_list.add_widget(gui.ToggleButton(text=col, state='normal'))

    def get_disabled_columns(self):
        return [x.text for x in self.col_list.children if x.state != 'down']


class DfguiWidget(gui.TabbedPanel):

    def __init__(self, df, col_width=160, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.col_width = col_width
        self.panel1.populate_data(df, col_width=col_width)
        self.panel2.populate_columns(df.columns[:])

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        #arr = self.panel3.get_filters()
        #print(str(arr))
        #self.panel1.apply_filter(self.panel3.get_filters())
        self.panel1._generate_table(disabled=
                                    self.panel2.get_disabled_columns())

# Uncomment the following code to use the chooseColor class as standalone kivy App

# class chooseColor(App):
#     def __init__(self, cder_path: str, **kwargs):
#         super(chooseColor, self).__init__(**kwargs)
#         App.__init__(self)
#         self.word_color: str
#         self.cder_path = cder_path

#     def set_word_col(self, word_col):
#         self.word_color = word_col
#         #stopTouchApp()
#         App.stop(self)

#     def build(self):
#         cadera = pd.read_csv(self.cder_path, index_col=0, nrows=10)
#         mainGrid = gui.GridLayout(cols=2)

#         boxDf = gui.BoxLayout(orientation='vertical')
#         boxDf.add_widget(DfguiWidget(cadera))
#         mainGrid.add_widget(boxDf)

#         langGrid = gui.GridLayout(cols=1)
#         langGrid.add_widget(gui.Label(text='Select highlight color used:'))

#         mainGrid.add_widget(langGrid)
#         return mainGrid

#     def run(self):
#         super().run()
#         return self.word_color


# def choose_color_main(cder_path):
#     stopTouchApp()
#     CC = chooseColor(cder_path)
#     word_color = CC.run()
#     print('Filter color =', word_color)
#     return word_color

# if __name__ == '__main__':

#     cder_path = '~/Documents/ManHatTan/CADERAs/Il castello dei destini incrociati - Notizbuch.cder'
#     CC = chooseColor(cder_path)
#     word_color = CC.run()
#     print('Filter color =', word_color)

#     #word_color = DFA.retrieve_word_col()
