"""Fader utility to change gain over time for selected frequency band.

    Author: Travis M. Moore
    Created: 19 Aug, 2022
    Last Edited: 14 Sep, 2022
"""

###########
# Imports #
###########
# Imports data science packages
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import sound packages
import sounddevice as sd
from scipy.io import wavfile

# Import custom modules
import tmsignals as ts


#########
# BEGIN #
#########
class Fader():
    """Change gain over time for selected frequency band
    """
    def __init__(self, signal, fs, trans_dur, floor, gain, 
    direct_path, direction):
        """Initialize object.
        """
        self.signal = signal
        self.FLOOR = floor
        self.FS = fs
        self.TRANS_DUR = trans_dur
        self.GAIN = gain
        self.DIRECT_PATH = direct_path
        self.DIRECTION = direction

        # Set initial values
        self.STABLE = 'both' # change to "start, end, both, none"
        self.STABLE_DUR = 5 # seconds
        self.DELAY = int(np.ceil((5/1000) * self.FS))

        # Truncate signal based on total duration
        self._set_audio_dur()

        # Filter signals
        # NOTE: necessary even for OAG to get direct path signal
        self.do_filter()

        """After init, the ready signals are:
            *self.signal
            *self.high
            *self.low
            *self.direct
        """


    def run(self, sig_change, sig_stable=None):
        """Call functions in order to create final signal.
        """
        self.mk_segments(sig_change=sig_change)

        if self.DIRECTION == 'decrease':
            self.decrease_gain(sig_decrease=sig_change)
        elif self.DIRECTION == 'increase':
            self.increase_gain(sig_increase=sig_change)

        self.ha_out(sig_stable=sig_stable)
        self.add_direct_path()

        self.calc_rms()


    def _calc_samps(self):
        """Calculate total duration based on stable portions
        """
        if self.STABLE == 'both':
            self.total_dur = (self.STABLE_DUR * 2) + self.TRANS_DUR

        elif (self.STABLE == 'start') or (self.STABLE == 'end'):
            self.total_dur = self.STABLE_DUR + self.TRANS_DUR

        elif self.STABLE == 'none':
            self.total_dur = self.TRANS_DUR

        # Convert seconds to samples
        self.stable_dur_samps = self.STABLE_DUR * self.FS
        self.trans_dur_samps = self.TRANS_DUR * self.FS
        self.total_dur_samps = (self.stable_dur_samps * 2) + self.trans_dur_samps


    def _set_audio_dur(self):
        """Truncate audio based on total duration
        """
        # Get total duration in samples
        self._calc_samps()

        # Truncate audio
        self.signal = self.signal[0:self.total_dur_samps]


    def do_filter(self):
        # Lowpass filter audio at 1000 Hz
        self.low = self.butter_filt(
            sig=self.signal, 
            type='low', 
            cutoff=1000, 
            order=10, 
            fs=self.FS, 
            plts='n')

        # Highpass filter audio at 1000 Hz
        self.high = self.butter_filt(
            sig=self.signal, 
            type='high', 
            cutoff=1000, 
            order=10, 
            fs=self.FS, 
            plts='n')

        # Lowpass filter audio at 750 Hz
        # Direct sound path
        self.direct = self.butter_filt(
            sig=self.signal, 
            type='low', 
            cutoff=750, 
            order=10, 
            fs=self.FS, 
            plts='n')


    def mk_segments(self, sig_change):
        """Splice audio into start, transition, and end clips
        """
        # Start clip
        self.sig_start = sig_change[0:self.stable_dur_samps]

        # Transition clip
        self.sig_trans = sig_change[self.stable_dur_samps:
            (self.stable_dur_samps + self.trans_dur_samps)]

        # End clip
        self.sig_end = sig_change[(self.stable_dur_samps 
            + self.trans_dur_samps):]
        
        # Define edge regions
        self.edge1 = (self.STABLE_DUR) * self.FS
        self.edge2 = (self.STABLE_DUR + self.TRANS_DUR) * self.FS


    def decrease_gain(self, sig_decrease):
        """Apply ramp to signal.
        """
        # Create ramp
        self.start_env = np.ones(len(self.sig_start))
        self.trans_env = np.linspace(1, self.FLOOR, len(self.sig_trans))
        self.end_env = np.repeat(self.FLOOR, len(self.sig_end))
        
        if self.STABLE == 'both':
            sig_decrease = sig_decrease
            self.envelope = np.hstack([self.start_env, self.trans_env, 
                self.end_env])

        elif self.STABLE == 'start':
            sig_decrease = sig_decrease[0:(len(self.sig_start) + len(self.sig_trans))]
            self.envelope = np.hstack([self.start_env, self.trans_env])
            
        elif self.STABLE == 'none':
            sig_decrease = sig_decrease[0:len(self.sig_trans)]
            self.envelope == self.trans_env

        else:
            raise NameError("Invalid selection for 'STABLE.'" +
                "Options are: 'both', 'start', and 'none.'")
        
        # Apply ramp to signal
        self.sig_gated = sig_decrease * self.envelope


    def increase_gain(self, sig_increase):
        """Apply ramp to signal.
        """
        # Create ramp
        self.start_env = np.repeat(self.FLOOR, len(self.sig_end))
        self.trans_env = np.linspace(self.FLOOR, 1, len(self.sig_trans))
        self.end_env = np.ones(len(self.sig_start))

        if self.STABLE == 'both':
            sig_increase = sig_increase
            self.envelope = np.hstack([self.start_env, self.trans_env, 
                self.end_env])
        
        elif self.STABLE == 'none':
            sig_increase = sig_increase[0:len(self.sig_trans)]
            self.envelope == self.trans_env

        else:
            raise NameError("Invalid selection for 'STABLE.'" +
                "Options are: 'both' or 'none.'")

        # Apply ramp to signal
        self.sig_gated = sig_increase * self.envelope


    def ha_out(self, sig_stable=None):
        """Prepare hearing aid final output.
        """
        # Recombine filtered signals
        if sig_stable is not None:
            # Truncate stable sig to match gated length
            self.sig_stable = sig_stable[0:len(self.sig_gated)]
            # Add gated and stable signals
            self.ha_sig = self.sig_gated + self.sig_stable
        else:
            self.ha_sig = self.sig_gated

        # Set final_sig as ha_sig
        # This is overriden if direct_path() is called
        self.final_sig = self.ha_sig


    def add_direct_path(self):
        """Add the direct path signal.
        """
        # Truncate direct path sound to match ha out
        self.direct = self.direct[0:len(self.ha_sig)]

        # Apply delay to ha out signal
        self.ha_sig = self.ha_sig[0:-self.DELAY]

        # Apply delay to direct path signal
        self.direct = self.direct[self.DELAY:]

        # Caculcate RMS of original signal
        self.signal_rms = np.round(ts.mag2db(ts.rms(self.signal)), 2)

        # Reduce RMS of direct path by self.GAIN
        self.direct = ts.setRMS(self.direct, self.signal_rms-self.GAIN)

        # Combine HA signal and direct path signals
        self.final_sig = self.ha_sig + self.direct


    def calc_rms(self):
        # Provide update to console
        print(f"Original signal RMS: {self.signal_rms} dB")
        print(f"HA signal RMS: " + 
            f"{np.round(ts.mag2db(ts.rms(self.ha_sig)), 2)} dB")
        print(f"Direct path signal RMS:" +
            f"{np.round(ts.mag2db(ts.rms(self.direct)), 2)} dB\n")

        # Calculate RMS drop using stable periods
        if self.STABLE == 'both':
            ha_start_rms = ts.mag2db(ts.rms(self.sig_gated[0:self.edge1]))
            ha_end_rms = ts.mag2db(ts.rms(self.sig_gated[self.edge2:]))
            #print(f"\nDry RMS: {ha_start_rms}")
            #print(f"Wet RMS: {ha_end_rms}")
            print("HA signal RMS drop: " +
                f"{np.round(ha_start_rms - ha_end_rms, 2)} dB")

            final_start_rms = ts.mag2db(ts.rms(self.final_sig[0:self.edge1]))
            final_end_rms = ts.mag2db(ts.rms(self.final_sig[self.edge2:]))
            #print(f"Dry RMS: {final_start_rms}")
            #print(f"Wet RMS: {final_end_rms}")
            print("HA signal + direct path signal RMS drop: " +
                f"{np.round(final_start_rms - final_end_rms, 2)} dB")


    def play_audio(self):
        """Present audio.
        """
        # Normalize final_sig to avoid clipping
        normed_sig = ts.doNormalize(self.final_sig, self.FS)

        # Present audio
        sd.play(normed_sig.T, self.FS)
        sd.wait(self.total_dur)


    def write_audio(self, condition):
        """Write audio as .wav file
        """
        wavfile.write(f'.\\audio_files_out\\{self.DIRECTION}_' + 
            condition + '_' + str(self.TRANS_DUR) + '.wav', 
            self.FS, self.final_sig)


    ####################
    # Filter functions #
    ####################
    def _filt_freq_response(b, a, nyq, cutoff):
        """Plot butterworth frequency response
        """
        w, h = signal.freqz(b, a)
        plt.semilogx((nyq / np.pi) * w, abs(h))
        plt.grid(True)
        plt.axvline(cutoff, c='g')
        plt.ylabel('Gain')
        plt.xlabel('Frequency (Hz)')
        plt.title("Butterworth filter frequency response")
        plt.show()


    def butter_filt(self, sig, type, cutoff, order, fs, plts):
        """Create and apply butterworth filter
        """
        nyq = 0.5 * fs
        norm_cutoff = cutoff / nyq
        b, a = signal.butter(order, norm_cutoff, btype=type, analog=False)
        y = signal.filtfilt(b, a, sig)

        if plts == 'y':
            self._filt_freq_response(b, a, nyq, cutoff)
        
        return y


    ######################
    # PLOTTING FUNCTIONS #
    ######################
    def plot_high_low(self, lowpass, highpass):
        """Plot filtered and recombined signals
        """
        a1 = plt.subplot2grid((2,2),(0,0), rowspan=1, colspan=1)
        a2 = plt.subplot2grid((2,2),(0,1), rowspan=1, colspan=1)
        a3 = plt.subplot2grid((2,2),(1,0), rowspan=1, colspan=2)
        a1.plot(lowpass, c='b')
        a1.set(title='Freqs < 1kHz', xlabel='Samples', ylabel='Amplitude')
        a1.set_ylim((-1,1))
        a2.plot(highpass, c='r')
        a2.set(title='Freqs > 1kHz', xlabel='Samples', ylabel='Amplitude')
        a2.set_ylim((-1,1))
        a3.plot(lowpass + highpass)
        a3.set(title='Recombined Signal', xlabel='Samples', ylabel='Amplitude')
        a3.set_ylim((-1, 1))
        plt.suptitle("Signal Filtering around 1 kHz")
        plt.tight_layout()
        plt.show()


    def plot_segments(self, sig_before_gate):
        """Plot gated and ungatd signal with stable portions highlighted
        """
        # Plot gated and pre-gated signals
        plt.plot(sig_before_gate, c='b')
        plt.plot(self.sig_gated, c='g')

        # First RMS region
        if (self.STABLE == 'start') or (self.STABLE == 'both'):
            coord = [[0,-1], [0,1], [self.edge1,1], [self.edge1,-1]]
            coord.append(coord[0]) # repeat the first point to close shape
            # Plot polygon
            xs, ys = zip(*coord) # create lists of x and y values
            plt.fill(xs, ys, edgecolor='none', facecolor="lightsalmon", 
                alpha=0.25)

        if self.STABLE == 'both':
            # Second RMS region
            coord = [[self.edge2,-1], [self.edge2,1], [len(self.sig_gated),1], 
                [len(self.sig_gated),-1]]
            coord.append(coord[0]) # repeat the first point to close shape
            # Plot polygon
            xs, ys = zip(*coord) # create lists of x and y values
            plt.fill(xs, ys, edgecolor='none', facecolor="lightsalmon", 
                alpha=0.25)
        plt.show()


    def plot_delay(self):
        """plot the delay between DEM and direct path signals
        """
        plt.subplot(3,1,1)
        plt.plot(self.ha_sig[0:1000])
        plt.title('Amplified signal')

        plt.subplot(3,1,2)
        plt.plot(self.direct[0:1000])
        plt.title('Direct pathway signal')

        plt.subplot(3,1,3)
        plt.plot(self.final_sig[0:1000])
        plt.title('Combined signal')
        plt.show()


    def plot_overlay(self):
        """Plot overlay of original, HA signal and direct path signals
        """
        plt.plot(self.signal[0:len(self.final_sig)], label="Input Audio")
        plt.plot(self.final_sig, label="HA Output + Direct Path")
        plt.plot(self.ha_sig, label="HA Output")
        plt.title('Time Waveforms')
        plt.legend(loc='upper right')
        plt.show()
