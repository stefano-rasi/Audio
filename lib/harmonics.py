import random

import scipy
import numpy as np

from collections.abc import Mapping, Iterable

class Harmonics:
    def __init__(self, harmonics):
        self.harmonics = {}

        if isinstance(harmonics, Mapping):
            self.harmonics = harmonics
        elif isinstance(harmonics, Iterable):
            for i, power in enumerate(harmonics):
                self.harmonics[i + 1] = power

    def make_waveform(self, pitch, sample_rate, random_phase=1, scale=4):
        wavelength = int(sample_rate / pitch * scale)

        half_fft = np.zeros(wavelength, dtype=complex)

        for i, power in self.harmonics.items():
            angle = random.random() * (2 * np.pi) * random_phase

            complex_angle = (np.cos(angle) + 1j * np.sin(angle))

            half_fft[i * 2 * scale] = power * complex_angle

        fft = np.concatenate((half_fft, np.flipud(np.conj(half_fft[1:]))))

        return scipy.fftpack.ifft(fft).real * wavelength