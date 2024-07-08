""" The Main Menu class for Adaptive Rating """

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

    def __init__(self, parent, sessionpars, **kwargs):
        super().__init__(parent, **kwargs)

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

        # Tools menu
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label="Audio Settings...",
            command=self._event('<<ToolsSpeaker>>')
        )
        tools_menu.add_command(
            label="Calibration...",
            command=self._event('<<ToolsCalibrate>>')
        )
        self.add_cascade(label='Tools', menu=tools_menu)


        # Help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(
            label='About',
            command=self.show_about
        )
        self.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        """ Show the about dialog """
        about_message = 'Adaptive Rating Tool'
        about_detail = (
            'Written by: Travis M. Moore\n'
            'Version 1.2.1\n'
            'Created: Jul 11, 2022\n'
            'Last Edited: Oct 10, 2022'
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )
