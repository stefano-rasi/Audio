import random

import numpy as np
import scipy

class Formant:
    def __init__(self, curve, sample_rate, min_freq=20, max_freq=20000):
        self.sample_rate = sample_rate

        freq_range = max_freq - min_freq

        x = np.linspace(0, 1, freq_range)

        y = curve.evaluate(freq_range)

        freq_x = (x * freq_range + min_freq) / max_freq

        interpolate = scipy.interpolate.interp1d(freq_x, y, fill_value='extrapolate')

        self.formant = interpolate(np.linspace(0, 1, sample_rate // 2))

    def make_noise(self):
        angles = np.random.rand(len(self.formant)) * (2 * np.pi)

        complex_angles = (np.cos(angles) + 1j * np.sin(angles))

        half_fft = self.formant * complex_angles

        fft = np.concatenate((half_fft, np.flipud(np.conj(half_fft[1:]))))

        noise = scipy.fftpack.ifft(fft).real * len(self.formant)

        return noise

    def make_waveform(self, pitch, random_phase=0, scale=4, mode='fft'):
        max_freq = int((self.sample_rate / pitch) // 2) - 1

        wavelength = int(round(self.sample_rate / pitch * scale))

        if mode == 'fft':
            half_fft = np.zeros(wavelength, dtype=complex)

            for i in range(max_freq):
                p = int(round(pitch * i))

                angle = random.random() * (2 * np.pi) * random_phase

                complex_angle = (np.cos(angle) + 1j * np.sin(angle))

                half_fft[(i + 1) * 2 * scale] = self.formant[p] * complex_angle

            fft = np.concatenate((half_fft, np.flipud(np.conj(half_fft[1:]))))

            waveform = scipy.fftpack.ifft(fft).real * wavelength

            return waveform
        elif mode == 'sin':
            sins = np.empty([max_freq, wavelength])

            for i in range(max_freq):
                p = int(round(pitch * i))

                phase = (i + 1) * 2 * np.pi * scale * (random.random() * random_phase)

                amplitude = self.formant[p]

                sins[i] = np.sin(np.linspace(0, (i + 1) * 2 * np.pi * scale, wavelength) + phase) * amplitude

            waveform = np.sum(sins, axis=0)

            return waveform

class LogFormant(Formant):
    def __init__(self, curve, sample_rate, min_freq=20, max_freq=20000):
        self.sample_rate = sample_rate

        freq_range = max_freq - min_freq

        x = np.linspace(0, 1, freq_range)

        y = curve.evaluate(freq_range)

        log_min_freq = np.log2(min_freq)

        log_freq_range = np.log2(max_freq) - np.log2(min_freq)

        log_x = np.power(2, x * log_freq_range + log_min_freq) / max_freq

        interpolate = scipy.interpolate.interp1d(log_x, y, fill_value='extrapolate')

        self.formant = interpolate(np.linspace(0, 1, sample_rate // 2))