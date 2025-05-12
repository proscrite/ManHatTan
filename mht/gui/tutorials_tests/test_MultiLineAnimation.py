from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
import numpy as np

class BlackBackgroundApp(App):
    def build(self):
        layout = BoxLayout()

        # Create a Matplotlib figure
        self.fig, self.ax = plt.subplots()
        
        # Set black background for the axes and figure
        self.ax.set_facecolor("black")
        self.fig.patch.set_facecolor("black")

        # Set tick and spine colors to match the black background
        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_edgecolor("white")

        # Plot style adjustments
        self.line, = self.ax.plot([], [], lw=2, color="lime")  # Bright green line for contrast

        # Set axis limits
        self.ax.set_xlim(0, 2 * np.pi)
        self.ax.set_ylim(-1.5, 1.5)

        # Add the Matplotlib figure to Kivy
        self.canvas = FigureCanvasKivyAgg(self.fig)
        layout.add_widget(self.canvas)

        # Animation setup
        self.x = np.linspace(0, 2 * np.pi, 100)
        self.frame = 0

        Clock.schedule_interval(self.update, 1 / 30)  # 30 FPS
        return layout

    def update(self, dt):
        """Update function for animation"""
        self.frame += 1
        y = np.sin(self.x + self.frame * 0.1)  # Animate sine wave
        self.line.set_data(self.x, y)
        self.canvas.draw()  # Redraw the canvas


if __name__ == "__main__":
    BlackBackgroundApp().run()
