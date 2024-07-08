""" Code for Maddie. Creates a stereo .wav file from a mono .wav file.
"""

import soundfile as sf
from pathlib import Path
import os
import numpy as np

_path = r'\\starfile\Public\Temp\CAR Group\Yellowstone Pilot\Telephony recordings\Parsed recordings 11.761'
files = Path(_path).glob('*.wav')
files = list(files)
print(f"\nfield: Found {len(files)} files")

for file in files:
    sig_mono, fs = sf.read(file)
    sig_stereo = np.c_[sig_mono, sig_mono]
    #sf.write(os.path.basename(file)[:-4] + '_stereo.wav', sig_stereo, fs)
    sf.write(os.path.basename(file), sig_stereo, fs)
