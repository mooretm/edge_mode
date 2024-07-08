""" Model class for Rating Sliders """

# Import system packages
import csv
from pathlib import Path
from datetime import datetime
import os
# Import data science packages
import numpy as np
import matplotlib.pyplot as plt
# Import data packages
import json
# Import science packages
import numpy as np
import random
from scipy.io import wavfile
# Import audio packages
import sounddevice as sd
# Import custom modules
from constants import FieldTypes as FT


class AudioList:
    """ Get audio files and randomize list """
    fields = {'Audio List': []}

    def __init__(self, sessionpars):
        
        self.sessionpars = sessionpars

        print("Models_31: Checking for audio files dir...")
        # If the file doesn't exist, return
        if not os.path.exists(self.sessionpars['Audio Files Path'].get()):
            print("Models_34: Not a valid audio files directory!")
            return
        # If a valid path has been given, get the files
        self.fields['Audio List'] = os.listdir(self.sessionpars['Audio Files Path'].get())
        random.shuffle(self.fields['Audio List'])
        print("Models_39: Loaded randomized audio files into AudioList model")
        #print(self.fields['Audio List'])


class CSVModel:
    """ CSV file storage """
    def __init__(self, sessionpars):

        # Initialize sessionpars
        self.sessionpars = sessionpars

        self.datestamp = datetime.now().strftime("%Y_%b_%d_%H%M")

    # Data dictionary
    fields = {
        "Awareness Rating": {'req': True, 'type': FT.decimal},
        "Acceptability Rating": {'req': True, 'type': FT.decimal},
        "Audio Filename": {'req': True}
        }

    
    def save_record(self, data):
        """ Save a dictionary of data to .csv file """
        filename = f"{self.datestamp}_{self.sessionpars['Condition'].get()}_{self.sessionpars['Subject'].get()}.csv"
        self.file = Path(filename)

        # Check for write access to store csv
        file_exists = os.access(self.file, os.F_OK)
        parent_writable = os.access(self.file.parent, os.W_OK)
        file_writable = os.access(self.file, os.W_OK)
        if (
            (not file_exists and not parent_writable) or
            (file_exists and not file_writable)
        ):
            msg = f"Permission denied accessing file: {filename}"
            raise PermissionError(msg)

        # Combine rating data and session parameters
        # 1. Create temp sessionpars dict to avoid changing runtime vals
        # 2. Get actual sessionpars values (not tk controls)
        temp_sessionpars = dict()
        for key in self.sessionpars:
            temp_sessionpars[key] = self.sessionpars[key].get()

        # Add rating data to the end of the sessionpars dict
        temp_sessionpars.update(data)

        # Reformat keys for easy import
        keys = temp_sessionpars.keys()
        # Make all lowercase and replace spaces with underscores
        keys_formatted = [x.lower().replace(' ', '_') for x in keys]

        # Make a new dictionary with the formatted keys
        all_data = dict()
        for idx, key in enumerate(keys):
            all_data[keys_formatted[idx]] = temp_sessionpars[key]
        # Remove audio files dir from dictionary
        # (No need to write the dir to file)
        all_data.pop('audio_files_path')

        # Create new field for trailing underscore naming
        # See naming convention info above
        # Take everything after the last underscore
        filename_val = all_data["audio_filename"].split("_")[-1]
        # Remove .wav file extension
        filename_val = filename_val[:-4]
        all_data["filename_value"] = filename_val

        # Save combined dict to file
        newfile = not self.file.exists()
        with open(self.file, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=all_data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(all_data)


class SessionParsModel:
    """ A model for saving session parameters """
    fields = {
        'Subject': {'type': 'str', 'value': '999'},
        'Condition': {'type': 'str', 'value': 'Quiet'},
        'Presentation Level': {'type': 'float', 'value': -50},
        'Speaker Number': {'type': 'int', 'value': 1},
        'Audio Files Path': {'type': 'str', 'value': 'Please select a path'}
    }


    def __init__(self):
        filename = 'rating_tool_pars.json'
        # Store settings file in user's home directory
        self.filepath = Path.home() / filename
        # Load settings file
        self.load()


    def load(self):
        """ Load the settings from the file """
        print("Models_78: Checking for pars file...")
        # If the file doesn't exist, return
        if not self.filepath.exists():
            return

        # Open the file and read in the raw values
        print("Models_84: File found - reading raw vals from pars file...")
        with open(self.filepath, 'r') as fh:
            raw_values = json.load(fh)

        # Don't implicitly trust the raw values; only get known keys
        print("Models_89: Loading vals into sessionpars model if they match model keys")
        for key in self.fields:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.fields[key]['value'] = raw_value


    def save(self):
        """ Save the current settings to the file """
        print("Models_153: Writing session pars from model to file...")
        with open(self.filepath, 'w') as fh:
            json.dump(self.fields, fh)
        
    
    def set(self, key, value):
        """ Set a variable value """
        print("Models_160: Setting sessionpars model fields with running vals...")
        if (
            key in self.fields and 
            type(value).__name__ == self.fields[key]['type']
        ):
            self.fields[key]['value'] = value
        else:
            raise ValueError("Bad key or wrong variable type")





class SettingsModel:
    """ A model for saving settings """
    fields = {
        'autofill date': {'type': 'bool', 'value': True}
    }


    def __init__(self):
        filename = 'rating_tool.json'
        # Store settings file in user's home directory
        self.filepath = Path.home() / filename
        print(self.filepath)
        # Load settings file
        self.load()


    def load(self):
        """ Load the settings from the file """
        # If the file doesn't exist, return
        if not self.filepath.exists():
            return

        # Open the file and read in the raw values
        with open(self.filepath, 'r') as fh:
            raw_values = json.load(fh)

        # Don't implicitly trust the raw values; only get known keys
        for key in self.fields:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.fields[key]['value'] = raw_value


    def save(self):
        """ Save the current settings to the file """
        with open(self.filepath, 'w') as fh:
            json.dump(self.fields, fh)
            print("Settings file written")

    
    def set(self, key, value):
        """ Set a variable value """
        if (
            key in self.fields and 
            type(value).__name__ == self.fields[key]['type']
        ):
            self.fields[key]['value'] = value
        else:
            raise ValueError("Bad key or wrong variable type")


class Audio:
    """ An object for use with .wav files. Audio objects 
        can read a given .wav file, handle audio data type 
        conversion, and store information about a .wav 
        file.
    """
    # Dictionary of data types and ranges for conversions
    wav_dict = {
        'float32': (-1.0, 1.0),
        'int32': (-2147483648, 2147483647),
        'int16': (-32768, 32767),
        'uint8': (0, 255)
    }

    def __init__(self, file_path, level):
        # Parse file path
        self.directory = file_path.split(os.sep) # path only
        self.name = str(file_path.split(os.sep)[-1]) # file name only
        self.file_path = file_path
        self.level = level

        # Read audio file
        fs, audio_file = wavfile.read(self.file_path)

        # Get number of channels
        try:
            self.channels = audio_file.shape[1]
        except IndexError:
            self.channels = 1
        print(f"Number of channels: {self.channels}")

        # Assign audio file attributes
        self.fs = fs
        self.original_audio = audio_file
        self.dur = len(self.original_audio) / self.fs
        self.t = np.arange(0, self.dur, 1/self.fs)

        # Get data type
        #self.data_type = np.dtype(audio_file[0])
        self.data_type = audio_file.dtype
        print(f"Incoming audio data type: {self.data_type}")

        # Immediately convert to float64 for processing
        self.convert_to_float()


    def convert_to_float(self):
        """ Convert original audio data type to float64 
            for processing
        """
        if self.data_type == 'float64':
            self.working_audio = self.original_audio
        else:
            # 1. Convert to float64
            sig = self.original_audio.astype(np.float64)
            # 2. Divide by original dtype max val
            sig = sig / self.wav_dict[str(self.data_type)][1]
            self.working_audio = sig


    def play(self):
        """ Present working audio """
        #print(f"Presenting audio data type: {np.dtype(self.working_audio[0])}")
        print(f"Presenting audio data type: {self.working_audio.dtype}")
        # plt.subplot(1,3,1)
        # plt.plot(self.original_audio)
        # plt.subplot(1,3,2)
        # plt.plot(self.working_audio)

        if self.channels == 1:
            sig = self.setRMS(self.working_audio, self.level)
            self.working_audio = sig
        elif self.channels > 1:
            left = self.setRMS(self.working_audio[:,0], self.level)
            right = self.setRMS(self.working_audio[:,1], self.level)
            self.working_audio = np.array([left, right])
        # plt.subplot(1,3,3)
        # plt.plot(self.working_audio)
        # plt.show()

        sd.play(self.working_audio.T, self.fs)
        #sd.wait(self.dur+0.5)


    def convert_to_original(self):
        """ Convert back to original audio data type """
        # 1. Multiply float64 by original data type max
        sig = self.working_audio * self.wav_dict[str(self.data_type)][1]
        if self.data_type != 'float32':
            # 2. Round to return to integer values
            sig = np.round(sig)
        # 3. Convert back to original data type
        sig = sig.astype(self.data_type)
        print(f"Converted data type: {str(type(sig[0]))}")
        self.working_audio = sig


    @staticmethod
    def db2mag(db):
        """ 
            Convert decibels to magnitude. Takes a single
            value or a list of values.
        """
        # Must use this form to handle negative db values!
        try:
            mag = [10**(x/20) for x in db]
            return mag
        except:
            mag = 10**(db/20)
            return mag


    @staticmethod
    def mag2db(mag):
        """ 
            Convert magnitude to decibels. Takes a single
            value or a list of values.
        """
        try:
            db = [20 * np.log10(x) for x in mag]
            return db
        except:
            db = 20 * np.log10(mag)
            return db


    def rms(self, sig):
        """ 
            Calculate the root mean square of a signal. 
            
            NOTE: np.square will return invalid, negative 
                results if the number excedes the bit 
                depth. In these cases, convert to int64
                EXAMPLE: sig = np.array(sig,dtype=int)

            Written by: Travis M. Moore
            Last edited: Feb. 3, 2020
        """
        theRMS = np.sqrt(np.mean(np.square(sig)))
        return theRMS


    def setRMS(self, sig, amp, eq='n'):
        """
            Set RMS level of a 1-channel or 2-channel signal.
        
            SIG: a 1-channel or 2-channel signal
            AMP: the desired amplitude to be applied to 
                each channel. Note this will be the RMS 
                per channel, not the total of both channels.
            EQ: takes 'y' or 'n'. Whether or not to equalize 
                the levels in a 2-channel signal. For example, 
                a signal with an ILD would lose the ILD with 
                EQ='y', so the default in 'n'.

            EXAMPLE: 
            Create a 2 channel signal
            [t, tone1] = mkTone(200,0.1,30,48000)
            [t, tone2] = mkTone(100,0.1,0,48000)
            combo = np.array([tone1, tone2])
            adjusted = setRMS(combo,-15)

            Written by: Travis M. Moore
            Created: Jan. 10, 2022
            Last edited: May 17, 2022
        """
        #amp = self.level
        #sig = self.working_audio
        if len(sig.shape) == 1:
            rmsdb = self.mag2db(self.rms(sig))
            refdb = amp
            diffdb = np.abs(rmsdb - refdb)
            if rmsdb > refdb:
                sigAdj = sig / self.db2mag(diffdb)
            elif rmsdb < refdb:
                sigAdj = sig * self.db2mag(diffdb)
            # Edit 5/17/22
            # Added handling for when rmsdb == refdb
            elif rmsdb == refdb:
                sigAdj = sig
            return sigAdj
            
        elif len(sig.shape) == 2:
            rmsdbLeft = self.mag2db(self.rms(sig[0]))
            rmsdbRight = self.mag2db(self.rms(sig[1]))

            ILD = np.abs(rmsdbLeft - rmsdbRight) # get lvl diff

            # Determine lvl advantage
            if rmsdbLeft > rmsdbRight:
                lvlAdv = 'left'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbRight > rmsdbLeft:
                lvlAdv = 'right'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbLeft == rmsdbRight:
                lvlAdv = None

            #refdb = amp - 3 # apply half amp to each channel
            refdb = amp
            diffdbLeft = np.abs(rmsdbLeft - refdb)
            diffdbRight = np.abs(rmsdbRight - refdb)

            # Adjust left channel
            if rmsdbLeft > refdb:
                sigAdjLeft = sig[0] / self.db2mag(diffdbLeft)
            elif rmsdbLeft < refdb:
                sigAdjLeft = sig[0] * self.db2mag(diffdbLeft)
            # Adjust right channel
            if rmsdbRight > refdb:
                sigAdjRight = sig[1] / self.db2mag(diffdbRight)
            elif rmsdbRight < refdb:
                sigAdjRight = sig[1] * self.db2mag(diffdbRight)

            # If there is a lvl difference to maintain across channels
            if eq == 'n':
                if lvlAdv == 'left':
                    sigAdjLeft = sigAdjLeft * self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight / self.db2mag(ILD/2)
                elif lvlAdv == 'right':
                    sigAdjLeft = sigAdjLeft / self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight * self.db2mag(ILD/2)

            sigBothAdj = np.array([sigAdjLeft, sigAdjRight])
            return sigBothAdj
