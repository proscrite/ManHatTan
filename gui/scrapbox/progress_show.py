from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import pandas as pd
import numpy as np

import sys
sys.path.append('../scripts/python_scripts/')
sys.path.append('../scripts/ML_duolingo')

def plot_progress(lipstick : pd.DataFrame):
    Nwords = len(lipstick)
    #nrows = int(np.sqrt(Nwords))
#    ncols = int( np.ceil(Nwords/ nrows))
    ncols = 4
    nrows = int(np.ceil(Nwords / ncols))
    print('ncols = %i, nrows = %i' %(ncols, nrows))

    fig, ax = plt.subplots(nrows, ncols, figsize=(30, 10 * nrows))#, subplot_kw=dict(aspect="equal"))
    for i, (w,p) in enumerate(zip(lipstick.word_ll, lipstick.p_pred)):
        j, k = i//ncols, i%ncols
        wedges, texts = ax[j,k].pie([p, 1-p], wedgeprops=dict(width=0.5), startangle=0, colors=['b', '0.9'])
        ax[j,k].set_xlabel(w, fontsize=8)
    plt.subplots_adjust(hspace=2, wspace=0.5, left=0.1, right=0.9)
    #plt.tight_layout()
    return plt.gcf()

#########################################################

root = Builder.load_string(r"""
<OrangeWidget>


<OrangeGraphicWidget>

    canvas:
        Color:
            rgba: 1, .5, 0, 1
        Rectangle:
            pos: self.center_x - 15, 20
            size: 30, self.height - (self.height / 10)
    BoxLayout:
        id: destination

    Button:
        text: "Back"
        pos_hint: {'center_x': .5, 'center_y': .95}
        size_hint: (None, None)
        background_color: (0, 0, 1, 1)
""")
class Plots(Widget):
    def __init__(self):
        super(Plots, self).__init__()
        self.number_of_plots = 3
        self.chart, self.axes = plt.subplots(nrows=self.number_of_plots,
                                             ncols=3,
                                             facecolor=(0.9, 0.9, 0.9))

class OrangeWidget(Screen):
    def __init__(self, **kwargs):
        super(OrangeWidget, self).__init__(**kwargs)
        self.app = App.get_running_app()

        scrollView = ScrollView(size_hint=(1, 1))

        figure = plot_progress(self.app.lipstick)

        # add custom widget into that layout
        customWidget = OrangeGraphicWidget(height=1600, size_hint_y=None)
        customWidget.ids.destination.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        #customWidget.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        scrollView.add_widget(customWidget)

        self.add_widget(scrollView)

class OrangeGraphicWidget(RelativeLayout):
    pass

class ProgressChart(App):
    def __init__(self, lipstick: pd.DataFrame):
        App.__init__(self)
        self.lipstick = lipstick
    def build(self):
        return OrangeWidget()


if __name__ == "__main__":
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/Die_Verwandlung.lip'
    #lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Il_castello_dei_destini_incrociati.lip'
    lipstick = pd.read_csv(lipstick_path, index_col=False)
    lipstick.set_index('word_ul', inplace=True, drop=False)

    PC = ProgressChart(lipstick)#, lipstick_path)
#    PC.build()
    PC.run()
