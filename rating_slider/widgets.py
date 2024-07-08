""" Custom widgets for Rating Sliders """

# Import GUI packages
import tkinter as tk
from tkinter import ttk


class RatingSlider(tk.Frame):
    """ A widget for subjective ratings with 
        visual anchors.
    """
    def __init__(self, parent, question, anchors, slider_args=None, 
    label_args=None, **kwargs):
        super().__init__(parent, **kwargs)
        slider_args = slider_args or {}
        label_args = label_args or {}

        frm_slider = ttk.LabelFrame(self, text=question, height = 140, width=slider_args['length']+100)
        frm_slider.grid(row=1, column=0, padx=30, pady=(30,0))

        scale_pos = [0, 0.25, 0.5, 0.75, 1]
        x_vals = []
        for idx, n in enumerate(scale_pos):
            x_vals.append(slider_args['length'] * scale_pos[idx])

        myScale = ttk.Scale(self, **slider_args)
        myScale.place(in_=frm_slider, relx=0.5, rely=0.5, anchor='c')

        frm_slider.update()
        offset = (frm_slider.winfo_width() - slider_args['length']) / 2

        for idx, anchor in enumerate(anchors, start=0):
            ttk.Label(self, text=anchor.split()[0]).place(in_=frm_slider, x=offset+x_vals[idx], rely=0.10, anchor='c')
            ttk.Label(self, text=anchor.split()[1]).place(in_=frm_slider, x=offset+x_vals[idx], rely=0.25, anchor='c')

        # Display slider value
        ttk.Label(self, text="Rating:").place(in_=frm_slider, relx=0.5, rely=0.8, anchor='e')
        ttk.Label(self, textvariable=slider_args['variable']).place(in_=frm_slider, relx=0.53, rely=0.8, anchor='e')

        self.update()
