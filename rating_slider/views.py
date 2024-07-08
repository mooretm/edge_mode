""" View for Rating Sliders """

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.simpledialog import Dialog

# Custom widgets
import widgets as w

# Import data science packages
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


class MainFrame(ttk.Frame):
    def __init__(self, parent, model, settings, sessionpars, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.model = model
        self.fields = self.model.fields
        self.settings = settings
        self.sessionpars = sessionpars


        def get_current_value():
            """ Retrieves current slider values """
            return int(self._vars['Awareness Rating'].get()), int(self._vars['Acceptability Rating'].get())


        def slider_changed(event):
            """ Updates slider values when moved """
            self._vars['Awareness Rating'].set(get_current_value()[0])
            self._vars['Acceptability Rating'].set(get_current_value()[1])


        # Data dictionary
        self._vars = {
            'Awareness Rating': tk.DoubleVar(value=50),
            'Acceptability Rating': tk.DoubleVar(value=50),
            'Audio Filename': tk.StringVar()
        }

        # Verbal anchors
        aware_anchors = ['Not\nAware', 'Slightly\nAware', 
            'Somewhat\nAware', 'Moderately\nAware', 'Extremely\nAware']
        accept_anchors = ['Not\nAcceptable', 'Slightly\nAcceptable', 
            'Somewhat\nAcceptable', 'Moderately\nAcceptable', 
            'Extremely\nAcceptable']

        # Styles
        # These are global settings
        style = ttk.Style(self)
        style.configure('TLabel', font=("Helvetica", 10))
        style.configure('TLabelframe.Label', font=("Helvetica", 11))
        style.configure('TButton', font=("Helvetica", 10))

        # Awareness Slider
        w.RatingSlider(self, 
            question="Please rate how aware you were of the transition:",
            anchors=aware_anchors, 
            slider_args={'from_':0, 'to':100, 'length':500, 
                'orient':'horizontal', 'command':slider_changed, 
                'variable':self._vars['Awareness Rating']}
            ).grid(row=5,column=0)

        # Acceptability Slider
        w.RatingSlider(self, 
            question="Please rate how acceptable the transition was:",
            anchors=accept_anchors, 
            slider_args={'from_':0, 'to':100, 'length':500, 
                'orient':'horizontal', 'command':slider_changed, 
                'variable':self._vars['Acceptability Rating']}
            ).grid(row=10,column=0)

        # Button frame
        frm_button = ttk.Frame(self)
        frm_button.grid(row=15, column=0, columnspan=5, padx=20, pady=20)

        # Play button
        self.btn_play = ttk.Button(frm_button, text="Play", command=self.play)
        self.btn_play.grid(row=0, column=0, sticky='w', padx=15)

        # Submit button
        self.btn_submit = ttk.Button(frm_button, text="Submit", 
            state="disabled", command=self._on_submit)
        self.btn_submit.grid(row=0, column=1, sticky='e', padx=15)


    def play(self):
        """ Present audio. Can be repeated as many times as 
            the listener wants.
        """
        # Send play audio event to app
        self.event_generate('<<PlayAudio>>')

    
    def _on_submit(self):
        # Send save data event to app
        self.event_generate('<<SaveRecord>>')


    def get(self):
        """ Retrieve data as dictionary """
        data = dict()
        for key, variable in self._vars.items():
            try:
                data[key] = variable.get()
            except tk.TclError:
                message=f'Error with: {key}.'
                raise ValueError(message)
        return data


    def reset(self):
        """ Clear all values """   
        for var in self._vars.values():
            var.set(50)
        # Disable submit button on press
        # Set focus to play button
        self.btn_submit.config(state="disabled")
        self.btn_play.focus()


class SessionParams(Dialog):
    """ A dialog that asks for session parameters """
    def __init__(self, parent, sessionpars, title, error=''):
        self.sessionpars = sessionpars
        self._error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, frame):
        options = {'padx':5, 'pady':5}
        ttk.Label(frame, text="Please Enter Session Parameters").grid(row=0, column=0, columnspan=3, **options)
        if self._error.get():
            ttk.Label(frame, textvariable=self._error).grid(row=1, column=0, **options)

        # Subject
        ttk.Label(frame, text="Subject:"
            ).grid(row=2, column=0, sticky='e', **options)
        ttk.Entry(frame, width=20, 
            textvariable=self.sessionpars['Subject']
            ).grid(row=2, column=1, sticky='w')
        
        # Condition
        ttk.Label(frame, text="Condition:"
            ).grid(row=3, column=0, sticky='e', **options)
        ttk.Entry(frame, width=20, 
            textvariable=self.sessionpars['Condition']
            ).grid(row=3, column=1, sticky='w')

        # Level
        ttk.Label(frame, text="Level:"
            ).grid(row=4, column=0, sticky='e', **options)
        ttk.Entry(frame, width=20, 
            textvariable=self.sessionpars['Presentation Level']
            ).grid(row=4, column=1, sticky='w')

        # Directory
        frm_path = ttk.LabelFrame(frame, text="Please select audio file directory")
        frm_path.grid(row=5, column=0, columnspan=2, **options, ipadx=5, ipady=5)
        my_frame = frame
        ttk.Label(my_frame, text="Path:"
            ).grid(row=5, column=0, sticky='e', **options)
        ttk.Label(my_frame, textvariable=self.sessionpars['Audio Files Path'], 
            borderwidth=2, relief="solid", width=60
            ).grid(row=5, column=1, sticky='w')
        ttk.Button(my_frame, text="Browse", command=self._get_directory
            ).grid(row=6, column=1, sticky='w')

    def _get_directory(self):
        # Ask user to specify audio files directory
        self.sessionpars['Audio Files Path'].set(filedialog.askdirectory())


    def ok(self):
        print("View:184: Sending save event...")
        self.parent.event_generate('<<ParsDialogOk>>')
        self.destroy()

    
    def cancel(self):
        print("View:190: Sending load event...")
        self.parent.event_generate('<<ParsDialogCancel>>')
        self.destroy()


    # def apply(self):
    #     # Send event to main window on "ok"
    #     #self.parent.event_generate('<<ParsDialogOk>>')
    #     pass
