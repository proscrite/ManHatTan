from kivy.app import App


class CalcApp(App):
    def calc(self, label):
        try:
            label.text = str(eval(label.text))
        except:
            label.text = 'syn error'

CalcApp().run()
