from mht import gui

import time
from mht.gui.common import *

class SettingsScreen(gui.Screen):
    def __init__(self, lipstick_path, team_lip_path, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.lippath = lipstick_path
        self.teamlippath = team_lip_path

    def on_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        """Build the UI for the settings screen."""
        self.clear_widgets()  # Clear previous widgets if any

        # Anchor everything to the top
        anchor = gui.AnchorLayout(anchor_y='top')

        layout = gui.BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(1, None))
        layout.height = 350  # Adjust as needed

        title = gui.Label(text="Settings", font_size=60, size_hint_y=None, height=60)
        layout.add_widget(title)
        layout.add_widet(Widget(size_hint_y=None, height=20))  # Spacer

        # 2x2 grid for settings buttons
        grid = gui.GridLayout(cols=2, rows=3, spacing=20, size_hint_y=None, height=220)

        btn_db = gui.Button(
            text="Select Database",
            font_size=40,
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=140,
            on_release=self.select_database
        )
        btn_edit = gui.Button(
            text="Edit Database",
            font_size=40,
            background_color=(0.2, 0.8, 0.6, 1),  # Changed color
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=140,
            on_release=self.edit_database
        )
        btn_sched = gui.Button(
            text="Set Scheduler",
            font_size=40,
            background_color=(0.6, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=140,
            on_release=self.set_scheduler
        )
        btn_diff = gui.Button(
            text="Difficulty Level",
            font_size=40,
            background_color=(0.8, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=140,
            on_release=self.set_difficulty
        )
        back_btn = gui.Button(
            text="Back to Main Menu",
            font_size=40,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=140,
            on_release=self.go_back
        )

        grid.add_widget(btn_db)
        grid.add_widget(btn_edit)
        grid.add_widget(btn_sched)
        grid.add_widget(btn_diff)
        grid.add_widget(back_btn)

        layout.add_widget(grid)
        anchor.add_widget(layout)
        self.add_widget(anchor)

    def select_database(self, instance):
        print("Select Database pressed (placeholder)")

    def edit_database(self, instance):
        print("Edit Database pressed (placeholder)")
        # Here you would implement the logic to edit the database, e.g., open a file dialog
        # or redirect to another screen where the user can edit the database.
        
    def set_scheduler(self, instance):
        print("Set Scheduler pressed (placeholder)")

    def set_difficulty(self, instance):
        print("Difficulty Level pressed (placeholder)")

    def go_back(self, instance):
        """Go back to the main menu."""
        self.manager.transition = gui.SlideTransition(direction="right")
        self.manager.current = "main_menu"