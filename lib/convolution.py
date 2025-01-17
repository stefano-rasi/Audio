import numpy as np
import scipy

class Convolution:
    def __init__(self, impulse):
        self.window = np.zeros(len(impulse))

        self.impulse_fft = scipy.fft.rfft(impulse) / (len(impulse) / 2)

    def apply(self, samples):
        self.window = np.roll(self.window, -len(samples))

        self.window[-len(samples):] = samples

        window_fft = scipy.fft.rfft(self.window)

        convolution_fft = window_fft * self.impulse_fft

        convolution = scipy.fft.irfft(convolution_fft)

        return convolution[-len(samples):]