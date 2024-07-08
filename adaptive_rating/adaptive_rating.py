""" Adaptive Rating:
    Wav-file-based adaptive rating task. Arrow buttons 
    allow for large and small step sizes of the 
    parameter under investigation. Data are saved as 
    .csv files.

    Written by: Travis M. Moore
    Created: Jul 11, 2022
    Last Edited: Oct 10, 2022
"""

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Import data science packages
import numpy as np
import pandas as pd
import random

# Import audio packages
import sounddevice as sd

# Import system packages
import sys
import os

# Import custom modules
import views as v
import models as m
from mainmenu import MainMenu


class Application(tk.Tk):
    """ Application root window """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.withdraw()
        self.title("Adaptive Rating Tool")

        # Load current session parameters (or defaults)
        self.sessionpars_model = m.SessionParsModel()
        self._load_sessionpars()

        # Set up file tracker counter
        # Set this here before loading the model
        # or counter is overriden to 0!
        self.counter = 0

        # Make audio files list model
        self._audio_list = pd.DataFrame()
        self.audio_data = pd.DataFrame()
        self._load_audiolist_model()

        # Initialize objects
        self.model = m.CSVModel(self.sessionpars)
        self.main_frame = v.MainFrame(self, self.model, self.sessionpars)
        self.main_frame.grid(row=1, column=0)
        self.main_frame.bind('<<SaveRecord>>', self._on_submit)
        self.main_frame.bind('<<RepeatAudio>>', self.present_audio)
        self.main_frame.bind('<<PlayAudio>>', self._get_audio)

        # Menu
        menu = MainMenu(self, self.sessionpars)
        self.config(menu=menu)
        # Create callback dictionary
        event_callbacks = {
            '<<FileSession>>': lambda _: self._show_sessionpars(),
            '<<FileQuit>>': lambda _: self.quit(),
            '<<ParsDialogOk>>': lambda _: self._save_sessionpars(),
            '<<ParsDialogCancel>>': lambda _: self._load_sessionpars(),
            '<<ToolsSpeaker>>': lambda _: self._show_audioconfig(),
            '<<AudioParsSubmit>>': lambda _: self._save_sessionpars(),
            '<<ToolsCalibrate>>': lambda _: self._show_calibration(),
            '<<CalibrationSubmit>>': lambda _: self._calc_level(),
            '<<PlayCalStim>>': lambda _: self._play_cal()
        }
        # Bind callbacks to sequences
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        # Status label to display trial count
        self.status = tk.StringVar(value="Trials Completed: 0")
        ttk.Label(self, textvariable=self.status).grid(
            sticky='w', padx=15, pady=(0,5))
        # Track trial number
        self._records_saved = 0

        # Set up root window
        #self.deiconify()

        self.center_window()


    def center_window(toplevel):
        """ Center the root window """
        toplevel.update_idletasks()
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        toplevel.geometry("+%d+%d" % (x, y)) 
        toplevel.deiconify()


    def _show_audioconfig(self):
        print("App_110: Calling audio config dialog...")
        v.AudioParams(self, self.sessionpars)

    
    def _show_calibration(self):
        print("App_115: Calling calibration dialog...")
        v.Calibration(self, self.sessionpars)


    def _show_sessionpars(self):
        """ Show the session parameters dialog """
        print("App_121: Calling sessionpars dialog...")
        v.SessionParams(self, sessionpars=self.sessionpars, 
            title="Session", error='')


    def _calc_level(self):
        slm_offset = self.sessionpars['SLM Reading'].get() - self.sessionpars['Raw Level'].get()
        print(f"SLM offset: {slm_offset}")
        self.sessionpars['Adjusted Presentation Level'].set(
            self.sessionpars['Presentation Level'].get() - slm_offset)
        print(f"Calculated level from _calc_level: " +
            f"{self.sessionpars['Adjusted Presentation Level'].get()}")
        self._save_sessionpars()


    def resource_path(self, relative_path):
        """ Get the absolute path to the resource 
            Works for dev and for PyInstaller
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


    def _play_cal(self):
        """ Load calibration file and present
        """
         # Check for default calibration stimulus request
        if self.sessionpars['Calibration File'].get() == 'cal_stim.wav':
            # Create calibration audio object
            try:
                # If running from compiled, look in compiled temporary location
                cal_file = self.resource_path('cal_stim.wav')
                cal_stim = m.Audio(cal_file, self.sessionpars['Raw Level'].get())
            except FileNotFoundError:
                # If running from command line, look in assets folder
                cal_file = '.\\assets\\cal_stim.wav'
                cal_stim = m.Audio(cal_file, self.sessionpars['Raw Level'].get())
        else: # Custom calibration file was provided
            print("Reading provided calibration file...")
            cal_stim = m.Audio(self.sessionpars['Calibration File'].get(), 
                self.sessionpars['Raw Level'].get())

        # Present calibration stimulus
        cal_stim.play(device_id=self.sessionpars['Audio Device ID'].get(), 
            channels=self.sessionpars['Speaker Number'].get())
    

    def _load_sessionpars(self):
        """ Load parameters into self.sessionpars dict 
        """
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create dict of settings variables from the model's settings.
        self.sessionpars = dict()
        for key, data in self.sessionpars_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.sessionpars[key] = vartype(value=data['value'])
        print("App_180: Loaded sessionpars model fields into " +
            "running sessionpars dict")


    def _save_sessionpars(self, *_):
        """ Save the current settings to a preferences file """
        print("App_185: Calling sessionpar model set vars and save functions")

        for key, variable in self.sessionpars.items():
            self.sessionpars_model.set(key, variable.get())
            self.sessionpars_model.save()


    def _load_audiolist_model(self):
        self.audiolist_model = m.AudioList(self.sessionpars)
        try:
            self.df_audio_data = self.audiolist_model.audio_data
        except:
            print("App_197: Problem creating list of audio files...")
            return
        if len(self.df_audio_data.index) > 0:
            print("App_200: Loaded audio files from AudioList model into " + 
                "runtime environment")
            self.counter = random.choice(
                np.arange(0,len(self.df_audio_data.index)-1))
            print(f"App_145: Starting record number: {self.counter}")
        else:
            print("App_204: No audio files in list!")
            messagebox.showwarning(
                title="No path selected",
                message="Please use File>Session to select a valid " +
                    "audio file directory!"
            )


    def _get_audio(self, *_):
        """ Increment counter, pull audio file, present audio """
        # Get what button was pressed
        data = self.main_frame.get()
        if data['Button ID'] == "bigup":
            self.counter -= 4
        elif data['Button ID'] == "smallup":
            self.counter -= 1
        elif data['Button ID'] == "bigdown":
            self.counter += 4
        elif data['Button ID'] == "smalldown":
            self.counter += 1

        # Make sure counter stays within bounds
        df_len = int(len(self.df_audio_data.index)-1)
        if self.counter >= df_len:
            self.counter = df_len
            #self.main_frame.event_generate('<<LowerLimit>>')
            print("App_241: Limit reached!")
            messagebox.showwarning(
                title='Limit Reached!',
                message="You are at the limit"
            )
        elif self.counter <= 0:
            self.counter = 0
            #self.main_frame.event_generate('<<UpperLimit>>')
            print("App_250: Limit reached!")
            messagebox.showwarning(
                title='Limit Reached!',
                message="You are at the limit"
            )

        # Present audio
        self.present_audio()


    def present_audio(self, *_):
        # Present audio
        print(f"App_237: Playing record #: {self.counter}")
        self.filename = self.df_audio_data["Audio List"].iloc[self.counter]
        print(f"App_239: Record name: {self.filename}")

        # Calculate adjusted presentation level in case of change
        self._calc_level()

        # Create audio object from stimulus list
        # Audio object expects a full file path and a presentation level
        print(f"Adjusted presentation level: " + 
            f"{self.sessionpars['Adjusted Presentation Level'].get()}")
        print(type(self.sessionpars['Adjusted Presentation Level'].get()))
        audio_obj = m.Audio(self.filename, 
            self.sessionpars['Adjusted Presentation Level'].get())

        # Present wav file stimulus
        audio_obj.play(device_id=self.sessionpars['Audio Device ID'].get(),
            channels=self.sessionpars['Speaker Number'].get())


    def _on_submit(self, *_):
        """ Save trial ratings, update trial counter,
            and reset sliders.
         """
        # Get _vars from main_frame view
        data = self.main_frame.get()
        # Update _vars with current audio file name
        data["Audio Filename"] = self.filename
        # Pass data dict to CSVModel for saving
        self.model.save_record(data)
        self._records_saved += 1
        self.status.set(f"Trials Completed: {self._records_saved}")
        self.main_frame.reset()
        # Choose a new random starting index
        self.counter = random.choice(
            np.arange(0,len(self.df_audio_data.index)-1))


    def _quit(self):
        """ Exit the program """
        self.destroy()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
