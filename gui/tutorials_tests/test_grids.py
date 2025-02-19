from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        # Main GridLayout with 3 columns
        grid = GridLayout(rows=2, row_force_default=True, row_default_height=50)

        upperPanel = GridLayout(cols=3, row_force_default=True, row_default_height=50)
        # Add widgets to the first row of the main grid
        upperPanel.add_widget(Label(text="Item 1"))
        upperPanel.add_widget(Label(text="Item 2"))
        upperPanel.add_widget(Label(text="Item 3"))

        # Add widgets to the second row of the main grid
        upperPanel.add_widget(Button(text="Button 1"))
        upperPanel.add_widget(Button(text="Button 2"))
        upperPanel.add_widget(Button(text="Button 3"))

        grid.add_widget(upperPanel)
        # AnswerPanel to span all 3 columns of the lower row
        answer_panel = GridLayout(cols=2, row_force_default=True, row_default_height=50)
        answer_panel.add_widget(Button(text="Answer 1"))
        answer_panel.add_widget(Button(text="Answer 2"))

        # Add AnswerPanel to the main grid
        grid.add_widget(answer_panel)  # Treat the entire last row as one widget

        # Ensure the AnswerPanel spans all 3 columns
        answer_panel.size_hint_x = 1
        answer_panel.size_hint_y = None
        answer_panel.height = 100  # Optional fixed height for AnswerPanel

        return grid

if __name__ == '__main__':
    MyApp().run()
