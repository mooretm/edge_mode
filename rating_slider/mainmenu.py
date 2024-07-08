""" The Main Menu class for Rating Sliders """

# Import GUI packages
import tkinter as tk
from tkinter import messagebox


class MainMenu(tk.Menu):
    """ Main Menu """
    # Find parent window and tell it to 
    # generate a callback sequence
    def _event(self, sequence):
        def callback(*_):
            root = self.master.winfo_toplevel()
            root.event_generate(sequence)
        return callback

    def __init__(self, parent, settings, sessionpars, **kwargs):
        super().__init__(parent, **kwargs)

        self.settings = settings
        self.sessionpars = sessionpars

        # File menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Session...",
            command=self._event('<<FileSession>>')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit",
            command=self._event('<<FileQuit>>')
        )
        self.add_cascade(label='File', menu=file_menu)
        # Help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(
            label='About',
            command=self.show_about
        )
        self.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        """ Show the about dialog """
        about_message = 'Rating Sliders'
        about_detail = (
            'Written by: Travis M. Moore\n'
            'Version 1.0.0\n'
            'Created: Jun 29, 2022\n'
            'Last Edited: Aug 23, 2022'
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )
