"""Controller for simulating DEM gain decreases
    in different frequency bands.
"""

###########
# Imports #
###########
# Import custom modules
from models import Audio
from fader_obj import Fader
import tmsignals as ts


####################
# Initialize Audio #
####################
# Read in audio with SNR of 0
speech_obj = Audio('.\\audio_files_in\\CST_Speech_Trunc.wav', -20)
babble_obj = Audio('.\\audio_files_in\\CST_Babble_4.wav', -20)

# Create signal of interest by combining speech and noise
speech = speech_obj.working_audio
babble = babble_obj.working_audio[0:len(speech)]
combo = speech + babble

# Make calibration noise based on combo
#from scipy.io import wavfile
#sig = speech_obj.original_audio + babble_obj.original_audio[0:len(speech_obj.original_audio)]
#wavfile.write('SPIN.wav', speech_obj.fs, sig)


#################
# Set constants #
#################
for dur in range(1,2): 
    SIGNAL = combo # .wav
    FS = speech_obj.fs # samples/sec
    TRANS_DUR = dur # seconds
    FLOOR = ts.db2mag(-10) # magnitude
    GAIN = 6 # dB
    DIRECT_PATH = 'y' # remove this
    DIRECTION = 'decrease' # decrease/increase (in level)


    """Run simulation"""
    #######################
    # Overall Gain Change #
    #######################
    oag = Fader(
        signal=SIGNAL,
        fs=FS,
        trans_dur=TRANS_DUR,
        floor=FLOOR,
        gain=GAIN,
        direct_path=DIRECT_PATH,
        direction=DIRECTION
        )

    print('-' * 70)
    print('OAG')
    print('-' * 70)
    oag.run(sig_change=oag.signal, sig_stable=None)
    #oag.plot_segments(sig_before_gate=oag.signal)
    #oag.write_audio("OAG")
    print('\n')


    ########################
    # Low Freq Gain Change #
    ########################
    lfg = Fader(
        signal=SIGNAL,
        fs=FS,
        trans_dur=TRANS_DUR,
        floor=FLOOR,
        gain=GAIN,
        direct_path=DIRECT_PATH,
        direction=DIRECTION
        )

    print('-' * 70)
    print('LFG')
    print('-' * 70)
    lfg.run(sig_change=lfg.low, sig_stable=lfg.high)
    #lfg.plot_segments(sig_before_gate=lfg.low)
    #lfg.write_audio("LFG")
    print('\n')


    #########################
    # High Freq Gain Change #
    #########################
    hfg = Fader(
        signal=SIGNAL,
        fs=FS,
        trans_dur=TRANS_DUR,
        floor=FLOOR,
        gain=GAIN,
        direct_path=DIRECT_PATH,
        direction=DIRECTION
        )

    print('-' * 70)
    print('HFG')
    print('-' * 70)
    hfg.run(sig_change=hfg.high, sig_stable=hfg.low)
    #hfg.plot_segments(sig_before_gate=hfg.high)
    #hfg.write_audio("HFG")
    print('\n')


    #########
    # Plots #
    #########
    """
    oag.plot_segments(sig_ungated=oag.signal)
    oag.plot_overlay()

    lfg.plot_segments(sig_ungated=lfg.low)
    lfg.plot_overlay()

    hfg.plot_segments(sig_ungated=hfg.high)
    hfg.plot_overlay()
    """
