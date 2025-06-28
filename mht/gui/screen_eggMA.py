# --- Egg Multiple Answer Screen (refactored for centralized gui imports) --- #
import os
from mht import gui
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import matplotlib.pyplot as plt
from bidi.algorithm import get_display

from mht.gui.common import *
from mht.scripts.python_scripts.update_lipstick import update_all
from mht.scripts.python_scripts import egg_processing as egg_proc

class EggScreen(gui.MultipleAnswerScreen):
    def __init__(self, lipstick_path, modality='rt', **kwargs):
        super().__init__(lipstick_path, modality=modality, **kwargs)
        self.is_egg_screen = True
        print('Initializing EggScreen with lipstick path:', lipstick_path)
        # Any Egg-specific initialization can go here

    def build_ui(self):
        super().build_ui()
        # --- Add Bypass Button ---
        bypass_btn = gui.Button(text='Bypass Word', background_color=(0.8, 0.5, 0.2, 1))
        bypass_btn.bind(on_release=self.bypass_word)
        self.optMenu.add_widget(bypass_btn)

    def _get_liptick_path(self):
        eggpath_dir, eggpath_fname = os.path.split(self.teamlippath)
        list_fname_split = eggpath_fname.split('_')[:-1]
        lippath_fname = '_'.join(list_fname_split) + '.lip'
        lippath = os.path.join(eggpath_dir.replace('EGGs', 'LIPSTICK'), lippath_fname)
        return lippath
    
    def _reset_lipstick_path(self, team_lippath):
        """Reset the lipstick path to the team lipstick path."""
        print('New teamlippath:', team_lippath)
        self.app.teamlippath = team_lippath
        print('Updating BaseExerciseScreen lippath: ', self.lippath)
        self.lippath = team_lippath

    def _check_egg_hatch(self):
        """Check if the egg has hatched and add it to main lipstick accordingly."""
        self.lipstick = self.lipstick.set_index('word_ul', drop=False)
        rebag = self.lipstick.loc[self.word_ul, 'rebag']

        if rebag:
            print('Egg hatched! Adding to main lipstick')
            self._hatch_egg(self.word_ul, self.answer, self.lipstick, self.lippath, self.modality)

        else:
            print('Egg not hatched yet')
            return

    def _hatch_egg(self, word_ul, answer, lipstick, lipstick_path, modality):
        """Add the entry from the egg to the main lipstick."""
        egg_path = lipstick_path
        team_lippath = self._get_liptick_path()
        lippath = team_lippath.replace('_team.lip', '.lip')
        general_lipstick = pd.read_csv(lippath)
        random_nid = egg_proc.get_random_nid(general_lipstick)
        egg_entry = egg_proc.init_hatched_egg(lipstick, word_ul, random_nid, flag_lexeme=True)
       
        self.show_hatch_animation(random_nid)

        new_lipstick = egg_proc.add_egg_to_lipstick(egg_entry, general_lipstick)
        if new_lipstick is not None:
            print('New lipstick after hatching:', new_lipstick)
            new_lipstick.to_csv(lippath, index=False)
            print(f'New lipstick saved to {lippath}')
        else:
            print('No new lipstick entry created.')
        
        # Delete the word from the egg database
        egg_proc.delete_word_from_egg(word_ul, egg_path)

    def _reload_egg_screen(self):
        """Reload the EggScreen to refresh the current word."""
        manager = self.manager
        temp_screen = None

        # Add a temporary blank screen if not present
        if not manager.has_screen('temp_blank'):
            temp_screen = gui.Screen(name='temp_blank')
            manager.add_widget(temp_screen)
        manager.current = 'temp_blank'

        if manager.has_screen(self.name):
            manager.remove_widget(self)  # Remove the current EggScreen
        
        new_egg_screen = EggScreen(self.teamlippath, modality=self.modality, name=self.name)
        manager.add_widget(new_egg_screen)   # Add the new EggScreen with the same name
        manager.current = self.name     # Switch to the new EggScreen

        if temp_screen:
            manager.remove_widget(temp_screen)

    def bypass_word(self, instance):
        """Bypass the current word: remove from egg db and reload EggScreen."""
        print(f"Bypassing word: {self.word_ul}")
        self._delete_word_from_EGG(self.word_ul)
        self._reload_egg_screen()

    def on_close(self, *_):
        # Dismiss the popup if it exists
        if hasattr(self, 'answer_popup') and self.answer_popup:
            self.answer_popup.dismiss()
            self.answer_popup = None

        _ = update_all(self.lipstick, self.teamlippath, self.word_ul, self.perf, self.speed, mode='m' + self.modality)
        
        # Check whether the egg hatches:
        self._check_egg_hatch()

        # Egg-specific logic for resetting paths
        print('Egg mode active, resetting lipstick_path: ', self.teamlippath)
        team_lippath = self._get_liptick_path()
        self._reset_lipstick_path(team_lippath)

        current_name = self.name
        self.go_back(current_name)

    def show_hatch_animation(self, random_nid):
        layout = gui.BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = gui.Label(text="The egg is hatching!", font_size=32, size_hint=(1, 0.2))
        layout.add_widget(label)

        self._fill_hatch_popup(layout, random_nid)

        anchor = gui.AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.85))
        anchor.add_widget(self.fig_canvas)
        layout.add_widget(anchor)

        self.continue_btn = gui.Button(text="Continue", size_hint=(1, 0.2), font_size=24, disabled=True)
        layout.add_widget(self.continue_btn)

        popup = gui.Popup(title="Egg Hatching!", content=layout, size_hint=(0.8, 0.6), auto_dismiss=False)
        self.continue_btn.bind(on_release=popup.dismiss)

        self._run_hatch_animation(popup)
        popup.open()

    def _fill_hatch_popup(self, layout, random_nid):
        fig, ax = plt.subplots(figsize=(3, 3))
        fig.patch.set_facecolor('black')
        ax.axis('off')
        ax.set_facecolor('black')

        self.im_obj_egg, self.anim_egg = load_pkmn_animation(ax, nframe=0, nid=0, n_cracks=5)
        self.im_obj_new, self.anim_new = load_pkmn_animation(ax, nframe=0, nid=random_nid)
        
        if self.rtl_flag: 
            self.word_ll = get_display(self.word_ll)
        ax.set_title(f'{self.word_ll}', color='yellow', fontsize=26)
        self.im_obj_new.set_visible(False)

        frame_size = self.anim_egg.shape[0]
        ax.set_xlim(0, frame_size)
        ax.set_ylim(frame_size, 0)

        self.fig_canvas = FigureCanvasKivyAgg(fig)
        self.ax = ax

    def _run_hatch_animation(self, popup):
        self._hatch_anim_frame = 0
        self._hatch_anim_cycles = 0
        egg_total_frames = self.anim_egg.shape[1] // self.anim_egg.shape[0]
        new_total_frames = self.anim_new.shape[1] // self.anim_new.shape[0]
        max_egg_cycles = 2
        new_anim_played = False

        def update(dt):
            nonlocal new_anim_played
            if not new_anim_played:
                frame_width = self.anim_egg.shape[0]
                frame = self._hatch_anim_frame % egg_total_frames
                new_img = self.anim_egg[:, frame_width * frame: frame_width * (frame + 1), :]
                self.im_obj_egg.set_data(new_img)
                self.fig_canvas.draw()
                self._hatch_anim_frame += 1
                if self._hatch_anim_frame % egg_total_frames == 0:
                    self._hatch_anim_cycles += 1
                    if self._hatch_anim_cycles >= max_egg_cycles:
                        self.im_obj_egg.set_visible(False)
                        self.im_obj_new.set_visible(True)
                        self._hatch_anim_frame = 0
                        self._hatch_anim_cycles = 0
                        self.ax.set_xlim(0, self.anim_new.shape[0])
                        self.ax.set_ylim(self.anim_new.shape[0], 0)
                        new_anim_played = True
                        self.continue_btn.disabled = False
            else:
                frame_width = self.anim_new.shape[0]
                frame = self._hatch_anim_frame % new_total_frames
                new_img = self.anim_new[:, frame_width * frame: frame_width * (frame + 1), :]
                self.im_obj_new.set_data(new_img)
                self.fig_canvas.draw()
                self._hatch_anim_frame += 1

        self._hatch_anim_event = gui.Clock.schedule_interval(update, 1/12)

        def on_dismiss(instance):
            gui.Clock.unschedule(self._hatch_anim_event)
        popup.bind(on_dismiss=on_dismiss)