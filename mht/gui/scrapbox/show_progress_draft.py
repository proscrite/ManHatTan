from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.base import runTouchApp

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from functools import partial
from time import sleep

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
import sys

ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan/'
sys.path.append(ROOT_PATH+'/scripts/python_scripts/')
sys.path.append(ROOT_PATH+'/scripts/ML_duolingo')
from duolingo_hlr import *
from update_lipstick import *
from kivy_multipleAnswer import *


def plot_progress(lipstick : pd.DataFrame):
    Nwords = len(lipstick)
    #nrows = int(np.sqrt(Nwords))
#    ncols = int( np.ceil(Nwords/ nrows))
    ncols = 3
    nrows = int(np.ceil(Nwords / ncols))
    print('ncols = %i, nrows = %i' %(ncols, nrows))

    fig, ax = plt.subplots(nrows, ncols, figsize=(8, 10 * nrows))#, subplot_kw=dict(aspect="equal"))
    for i, (w,p) in enumerate(zip(lipstick.word_ll, lipstick.p_pred)):
        j, k = i//ncols, i%ncols
        wedges, texts = ax[j,k].pie([p, 1-p], wedgeprops=dict(width=0.5), startangle=0, colors=['b', '0.9'])
        ax[j,k].set_xlabel(w, fontsize=8)
    plt.tight_layout()
    return plt.gcf()

class ProgressChart(App):

    def __init__(self, lipstick: pd.DataFrame, lippath: str):
        App.__init__(self)
        self.lipstick = lipstick
        self.lippath = lippath

    def build(self):
        sv = ScrollView(size_hint=(6,10), size=Window.size, height=1200)
        #sv.do_scroll_x = False
        #sv.do_scroll_y = True

        chart = BoxLayout(size_hint=(6,6))

        #lb2 = Label(text='Progress tracking', size_hint=(0.1,0.1), )

        figure = plot_progress(self.lipstick)
        #print(figure)
        #chart.add_widget(lb2)
        chart.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        print('So far so good')
        sv.add_widget(chart)
        return sv

if __name__ == "__main__":
    lipstick_path = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/Hebrew_db.lip'
    lipstick = pd.read_csv(lipstick_path, index_col=False)
    print(lipstick.head())
    lipstick.set_index('word_ul', inplace=True, drop=False)

    PC = ProgressChart(lipstick.head(), lipstick_path)
#    PC.build()
    PC.run()
