from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from bidi.algorithm import get_display
from kivy.clock import Clock


class FTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.multiline = False
        self.halign = 'center'
        self.bold = True  # This makes both the hint text and input text bold
        self.hint_text = kwargs.get('hint_text', 'Write here')
        self.multiline = False  # Ensures single-line input
        # To center vertically, we'll adjust padding and ensure text is aligned
        self.padding_y = [self.height / 2, self.height / 2]  #

        self.padding_x = [self.center[0] - self._get_text_width(max(self._lines, key=len), self.tab_width, self._label_cached) / 2.0,
            0] if self.text else [self.center[0], 0]
        # self.padding_y= [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
    
    def set_focus(self, dt):
        self.focus = True
        

class RTLTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "center"  # Align text visually to the right
        # self.font_name = "NotoSansHebrew-Regular.ttf"  # Hebrew-compatible font
        self.text_language = "he"  # Specify language as Hebrew
        self.multiline = False  # Force single-line text
        self._prevent_loop = False  # To prevent recursion
        self._text_backup = ""  # Backup to track the original logical text
        self.bold = True  # This makes both the hint text and input text bold
        self.padding_y = [self.height / 2, self.height / 2]  #
        self.text_input_focus = True

        Clock.schedule_once(self.set_focus, 0.1)  # Delayed focus

    def set_focus(self, dt):
        self.focus = True

    def insert_text(self, substring, from_undo=False):
        """Handles character insertion and ensures proper RTL display."""
        cursor_pos = self.cursor_index()

        # Update logical text order
        self._text_backup = (
            self._text_backup[:cursor_pos] + substring + self._text_backup[cursor_pos:]
        )
        # Convert logical text to visual RTL text using BiDi
        visual_text = get_display(self._text_backup)
        # Set the processed text and restore cursor position
        self.text = visual_text
        self.cursor = (cursor_pos + len(substring), 0)

    def delete_selection(self, *args):
        """Handles text deletion and ensures proper RTL display."""
        if not self.selection_text:
            return
        # Calculate selection range
        start, end = self.selection_from, self.selection_to
        # Ensure proper order of start and end
        start, end = min(start, end), max(start, end)
        # Update the logical text
        self._text_backup = self._text_backup[:start] + self._text_backup[end:]
        # Convert logical text to visual RTL text using BiDi
        visual_text = get_display(self._text_backup)
        # Update text and cursor position
        self.text = visual_text
        self.cursor = (start, 0)

    def do_backspace(self, from_undo=False, mode="bkspc"):
        """Handles backspace and ensures proper RTL display."""
        if not self._text_backup or self.cursor_index() <= 0:
            return
        cursor_pos = self.cursor_index()

        # Remove the character before the cursor in the logical text
        self._text_backup = (
            self._text_backup[: cursor_pos - 1] + self._text_backup[cursor_pos:]
        )

        # Convert logical text to visual RTL text using BiDi
        visual_text = get_display(self._text_backup)

        # Update text and restore cursor position
        self.text = visual_text
        self.cursor = (cursor_pos - 1, 0)
