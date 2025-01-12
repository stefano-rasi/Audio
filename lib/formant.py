import random

import scipy
import numpy as np

class Formant:
    def __init__(self, curve, sample_rate, min_freq=20, max_freq=20000):
        self.sample_rate = sample_rate

        freq_range = max_freq - min_freq

        xs = np.linspace(0, 1, freq_range)

        ys = curve.evaluate(freq_range)

        freq_xs = (xs * freq_range + min_freq) / max_freq

        interpolate = scipy.interpolate.interp1d(freq_xs, ys, fill_value='extrapolate')

        self.formant = interpolate(np.linspace(0, 1, int(round(sample_rate / 2))))

    def make_noise(self):
        angles = np.random.rand(len(self.formant)) * (2 * np.pi)

        complex_angles = (np.cos(angles) + 1j * np.sin(angles))

        half_fft = self.formant * complex_angles

        fft = np.concatenate((half_fft, np.flipud(np.conj(half_fft[1:]))))

        return scipy.fftpack.ifft(fft).real * len(self.formant)

    def make_waveform(self, pitch, random_phase=1, scale=4):
        max_freq = int(round(self.sample_rate / pitch / 2)) - 1

        wavelength = int(round(self.sample_rate / pitch * scale))

        half_fft = np.zeros(wavelength, dtype=complex)

        for i in range(max_freq):
            p = int(round(pitch * i))

            angle = random.random() * (2 * np.pi) * random_phase

            complex_angle = (np.cos(angle) + 1j * np.sin(angle))

            half_fft[(i + 1) * 2 * scale] = self.formant[p] * complex_angle

        fft = np.concatenate((half_fft, np.flipud(np.conj(half_fft[1:]))))

        return scipy.fftpack.ifft(fft).real * wavelength

class LogFormant(Formant):
    def __init__(self, curve, sample_rate, min_freq=20, max_freq=20000):
        self.sample_rate = sample_rate

        freq_range = max_freq - min_freq

        xs = np.linspace(0, 1, freq_range)

        ys = curve.evaluate(freq_range)

        log_min_freq = np.log2(min_freq)

        log_freq_range = np.log2(max_freq) - np.log2(min_freq)

        log_xs = np.power(2, xs * log_freq_range + log_min_freq) / max_freq

        interpolate = scipy.interpolate.interp1d(log_xs, ys, fill_value='extrapolate')

        self.formant = interpolate(np.linspace(0, 1, int(round(sample_rate / 2))))