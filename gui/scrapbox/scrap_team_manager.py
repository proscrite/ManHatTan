import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import numpy as np

class MiniFigureCell(BoxLayout):
    def __init__(self, pk, **kwargs):
        # Arrange the cell as a horizontal box:
        # [Left Button | Matplotlib Figure (with gridspec) | Right Button]
        super().__init__(orientation='horizontal', **kwargs)
        
        # Left button with partial transparency
        left_button = Button(text=pk["word_ll"],
                             background_color=(1, 1, 1, 0.3),  # white with 0.3 alpha
                             size_hint=(0.2, 1))
        self.add_widget(left_button)
        
        # Create the mini-figure using GridSpec
        # We create a figure manually rather than using plt.subplots()
        fig = plt.figure(figsize=(3, 2))
        # Create a gridspec with 3 rows and 4 columns
        gs = GridSpec(3, 4, figure=fig,
                      width_ratios=[0.3, 0.3, 0.3, 0.9],
                      height_ratios=[1, 1, 1])
        
        # Create a main axes that spans the top two rows over all columns
        ax_main = fig.add_subplot(gs[:2, :])
        # Draw your main plot (for example, a line plot)
        x = np.linspace(0, 10, 100)
        ax_main.plot(x, np.sin(x), color="cyan")
        ax_main.set_title(pk["name"], color="white")
        ax_main.set_facecolor('black')
        # Hide ticks if desired
        ax_main.set_xticks([])
        ax_main.set_yticks([])
        
        # Add additional subplots as needed (example: a health bar below)
        # We place this health bar in the bottom row, spanning first three columns
        ax_health = fig.add_subplot(gs[2, :3])
        ax_health.set_xlim(0, 1)
        # Here you can customize the “health bar” (example: a horizontal bar)
        # For demonstration, we just fill part of the background
        ax_health.barh(0, pk.get("health", 0.5), color='lime', height=0.5)
        ax_health.set_yticks([])
        ax_health.set_xticks([])
        ax_health.set_facecolor('gray')
        
        # Set the figure background to match if necessary
        fig.patch.set_facecolor('black')
        
        # Wrap the figure in a Kivy widget
        canvas = FigureCanvasKivyAgg(fig)
        canvas.size_hint = (0.6, 1)  # Adjust size as needed
        self.add_widget(canvas)
        
        # Right button (for example, showing HP or another stat)
        # right_button = Button(text=f"HP: {pk.get('hp', 'N/A')}/100",
        #                       background_color=(1, 1, 1, 0.3),
        #                       size_hint=(0.2, 1))
        # self.add_widget(right_button)

class MyApp(App):
    def build(self):
        # Main grid: 2 rows x 3 columns (or as needed)
        main_grid = GridLayout(rows=2, cols=3)
        
        # Example Pokémon/stats data for each cell
        pokemons = [
            {"name": "Aipom",    "word_ll": "Scholarship", "hp": 15, "health": 0.7},
            {"name": "Krabby",   "word_ll": "Intention",   "hp": 14, "health": 0.6},
            {"name": "Oshawott", "word_ll": "Towel",       "hp": 16, "health": 0.8},
            {"name": "Ralts",    "word_ll": "To Arrive",   "hp": 16, "health": 0.65},
            {"name": "Chimchar", "word_ll": "Grade",       "hp": 16, "health": 0.9},
            {"name": "Joltik",   "word_ll": "Screen",      "hp": 10, "health": 0.5}
        ]
        
        for pk in pokemons:
            cell = MiniFigureCell(pk)
            main_grid.add_widget(cell)
        
        return main_grid

if __name__ == '__main__':
    MyApp().run()
