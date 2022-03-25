from .kivy.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib.figure import Figure
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class MyApp(App):

    def build(self):
        box = BoxLayout()

        figure = Figure()

        ax = figure.add_subplot(111)
        ax.plot([1, 23, 2, 4])
        canvas = FigureCanvasKivyAgg(figure)

        box.add_widget(canvas)

        return box

def main():
    MyApp().run()
