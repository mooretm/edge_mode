""" Custom widgets for Adaptive Rating """

# Import GUI packages
import tkinter as tk
from tkinter import ttk

# Import system packages
import sys
import os


def resource_path(relative_path):
    """ Get the absolute path to the resource 
        Works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ArrowGroup(tk.Frame):
    """ Group of arrow buttons indicating fast/slower 
        and big/small step size
     """
    def __init__(self, parent, button_text, command_args=None, 
    repeat_args=None, **kwargs):
        super().__init__(parent, **kwargs)
        command_args = command_args or {}
        repeat_args = repeat_args or {}

        # Layout
        options = {'padx': 5, 'pady':5}

        # Style
        style = ttk.Style(self)
        style.configure('Big.TLabel', font=("Helvetica", 14))
        style.configure('Big.TButton', font=("Helvetica", 11))


        # LABELS
        # Faster label
        lbl_faster = ttk.Label(self, text="Faster", style="Big.TLabel")
        lbl_faster.grid(row=0, column=0)

        # Slower label
        lbl_faster = ttk.Label(self, text="Slower", style="Big.TLabel")
        lbl_faster.grid(row=1, column=0)


        # BUTTONS
        # Image names for arrow icons
        image_names = ["big_up.png", "small_up.png", "big_down.png", 
        "small_down.png"]
        rows = [0,0,1,1]
        cols = [1,2,1,2]
        for idx, key in enumerate(command_args):
            img = resource_path(image_names[idx])
            btn = ttk.Button(self, takefocus=0,
                command=command_args[key])
            # Temp fix for compiled vs uncompiled file locations
            try:
                btn.image = tk.PhotoImage(file=img)
            except:
                btn.image = tk.PhotoImage(file='assets/' + image_names[idx])
            btn['image'] = btn.image
            btn.grid(row=rows[idx], column=cols[idx], **options)

        # Repeat button
        self.btn_repeat = ttk.Button(self, 
            textvariable=button_text, 
            command=repeat_args["repeat"],
            style='Big.TButton',
            takefocus=0)
        self.btn_repeat.grid(row=2, column=1, columnspan=2, **options)
