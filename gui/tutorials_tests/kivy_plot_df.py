from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
import pandas as pd

exercisedict = {'exercise':['Pushups', 'Squats', 'Curls'],'focus':['Chest','Legs','Arms'],'equip':['None','None','Dumbells'], 'deftime':['30','30','40']}
exercisedf = pd.DataFrame(exercisedict)


class MainScreen(Screen):
    pass


class EditWorkoutScreen(Screen):

    def setupscreen(self):
        for index, row in exercisedf.iterrows():
            MyGrid(str(row.exercise),str(row.focus),str(row.equip),str(row.deftime))

    def addgrids(self):
        global grids
        for i in grids:
            print (i.children)
            self.ids.exercisestoverify.add_widget(i)

    def printtext(self):
        global grids
        for i in grids:
            print (i.extime.text)


class ScreenManagement(ScreenManager):
    pass

grids= []
class MyGrid(GridLayout):
    def __init__(self,exname,exfocus,exequip,extime, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        global grids
        def testtext(self):
            print (self.text)
        self.exname = Label(text=exname)
        self.exfocus = Label(text=exfocus)
        self.exequip = Label(text=exequip)
        self.extime = TextInput(text=extime, size_hint=(None,None), size=(25,30),font_size=11, multiline=False)
        self.extime.bind(on_text_validate=testtext)

        self.add_widget(self.exname)
        self.add_widget(self.exfocus)
        self.add_widget(self.exequip)
        self.add_widget(self.extime)

        grids.append(self)


presentation = Builder.load_string("""
#: import FadeTransition kivy.uix.screenmanager.FadeTransition

ScreenManagement:
    transition: FadeTransition()
    MainScreen:
    EditWorkoutScreen:

####### Layout Outlines #############################################################
<GridLayout>:
    canvas.after:
        Color:
            rgb: 1,0,0
        Line:
            rectangle: self.x+1,self.y+1,self.width-1,self.height-1
        Color:
            rgb: 1,1,1

<FloatLayout>:
    canvas.after:
        Color:
            rgb: 1,0,0
        Line:
            rectangle: self.x+1,self.y+1,self.width-1,self.height-1
        Color:
            rgb: 1,1,1
<BoxLayout>:
    canvas.after:
        Color:
            rgb: 1,0,0
        Line:
            rectangle: self.x+1,self.y+1,self.width-1,self.height-1
        Color:
            rgb: 1,1,1
#########################################################################################
<MainScreen>:
    name: "main"
    FloatLayout:
        id: test
        canvas.before:
            Color:
                rgba: 0, 0, 1, .5
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Workout Creator"
            pos_hint:{"x": 0, "y": .4}
            font_size: 40
        Label:
            text: "Welcome"
            pos_hint:{"x": -.4, "y": .4}
            font_size: 20
        Button:
            text: "Click here"
            color: 0,1,0,1
            size_hint: .2, .1
            pos_hint: {"x":.4, "y":.7}
            on_release: root.manager.current = "editworkout"

<MyGrid>:
    rows: 1

<EditWorkoutScreen>:
    name:'editworkout'
    on_enter: root.setupscreen()
    FloatLayout:
        Label:
            text: 'Verify/Edit Workout'
            pos: 0, 550
            font_size: 20

        ScrollView:
            pos_hint: {"x":.160, "y":-.15}
            GridLayout:
                id: exercisestoverify
                size_hint_y: None
                size_hint_x: .80
                orientation: "vertical"
                height: self.minimum_height
                row_default_height: 30
                spacing: 0
                cols:1
        Button:
            text: 'press'
            on_press: root.addgrids()
            size: 100,20
            size_hint: None,None
        Button:
            text: 'text input text'
            on_press: root.printtext()
            size: 100,20
            size_hint: None,None
            pos: 100,100

""")


class MainApp(App):

    def build(self):
        return presentation


MainApp().run()
