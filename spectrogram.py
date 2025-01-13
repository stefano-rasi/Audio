import argparse

import numpy as np
import librosa
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog='spectrogram')

parser.add_argument('path', nargs='?')

args = parser.parse_args()

path = args.path

y, sr = librosa.load(path)

stft = librosa.stft(y, n_fft=512, hop_length=512//32)

stft = librosa.amplitude_to_db(np.abs(stft))

librosa.display.specshow(stft, sr=sr)

plt.show()