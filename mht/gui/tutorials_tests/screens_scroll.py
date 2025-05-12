import time
import psutil
import matplotlib.pyplot as plt

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

# Chart Constants
MAX_MEASUREMENT_ARRAY_LENGTH = 500      # to trim measured values values
X_BASE_INTERVAL_LENGTH = 10             # time axis is displayed for an interval of 50 seconds
BASE_LINE_WIDTH = 0.5                   # line width of lines in plots
BASE_LINE_COLOR = "white"
COLUMNS_OF_PLOTS = 1                    # TODO implement more general layout possibilities, at the moment only 1-column

chart_variables = {
    "cpu_usage": {
        "order_number": 1,
        "title": "CPU Usage",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "CPU usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": False,
    },

    "upc_usage": {
        "order_number": 2,
        "title": "UPC Usage",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "UPC usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": True,
    },

    "test3": {
        "order_number": 3,
        "title": "test",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "UPC usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": True,
    },

    "test4": {
        "order_number": 4,
        "title": "test",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "UPC usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": True,
    },

    "test5": {
        "order_number": 5,
        "title": "test",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "UPC usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": True,
    },

    "test6": {
        "order_number": 6,
        "title": "test",
        "color": BASE_LINE_COLOR,
        "line_width": BASE_LINE_WIDTH,
        "x_interval_length": X_BASE_INTERVAL_LENGTH,
        "y_bottom": 0,
        "y_top": 100,
        "x_label": "Time in epochs",
        "y_label": "UPC usage in %",
        "x_values": [],
        "y_values": [],
        "anti_aliased": True,
    },
}


def slice_arrays(max_array_length):
    if len(chart_variables["cpu_usage"]["x_values"]) > max_array_length:
        for key in chart_variables:
            chart_variables[key]["x_values"] = chart_variables[key]["x_values"][int(max_array_length / 2):]
            chart_variables[key]["y_values"] = chart_variables[key]["y_values"][int(max_array_length / 2):]


class Plots(Widget):
    def __init__(self):
        super(Plots, self).__init__()
        self.number_of_plots = len(chart_variables)
        self.t_start = time.time()
        self.chart, self.axes = plt.subplots(nrows=self.number_of_plots,
                                             ncols=COLUMNS_OF_PLOTS,
                                             facecolor=(0.9, 0.9, 0.9))
        plt.subplots_adjust(hspace=0.01)
        self.chart.patch.set_alpha(0)  # transparent plot background

    def initialize_plots(self):
        for ax, key in zip(self.axes.flat, chart_variables):
            ax.set_title(chart_variables[key]["title"], color=chart_variables[key]["color"])
            ax.tick_params(labelcolor=chart_variables[key]["color"])
            ax.set_xlabel(chart_variables[key]["x_label"], color=chart_variables[key]["color"])
            ax.set_ylabel(chart_variables[key]["y_label"], color=chart_variables[key]["color"])
            ax.set_ylim(bottom=chart_variables[key]["y_bottom"],
                        top=chart_variables[key]["y_top"])
            ax.set_frame_on(False)  # remove white background inside each subplot
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')

    def plot_data(self):
        slice_arrays(MAX_MEASUREMENT_ARRAY_LENGTH)
        for ax, key in zip(self.axes.flat, chart_variables):
            x_axis_interval_length = chart_variables[key]["x_interval_length"]
            elapsed_time = time.time() - self.t_start
            number_of_intervals = elapsed_time // x_axis_interval_length  # index 0 to get div part only
            chart_variables[key]["x_values"].append(elapsed_time)
            chart_variables[key]["y_values"].append(psutil.cpu_percent())
            ax.plot(chart_variables[key]["x_values"],
                    chart_variables[key]["y_values"],
                    color=chart_variables[key]["color"],
                    linewidth=chart_variables[key]["line_width"],
                    antialiased=chart_variables[key]["anti_aliased"])
            self.chart.canvas.draw()
            x_left = x_axis_interval_length * number_of_intervals
            x_right = x_axis_interval_length * (number_of_intervals + 1)
            ax.set_xlim(left=x_left, right=x_right)

    def update_plots(self, _):
        self.plot_data()

class MyApp(App):

    def build(self):
        plot = Plots()
        plot.initialize_plots()
        Clock.schedule_interval(plot.update_plots, 0.2)
        scroll_view = ScrollView()
        box = BoxLayout()
        box.spacing = 24
        scroll_view.add_widget(box)
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        return scroll_view


if __name__ == "__main__":
    MyApp().run()
