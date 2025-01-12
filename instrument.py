import os
import sys
import argparse
import importlib.util

import scipy
import numpy as np
import pynput
import pyaudio
import pygame.midi

from threading import Thread

class SpectrumAnalyzer:
    def __init__(self, width=1024, height=512, min_freq=20, max_freq=20000):
        pygame.display.init()

        pygame.display.set_caption('Spectrum analyzer')

        self.samples = np.zeros(max_freq)

        self.surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        self.spectrum = None

        self.min_freq = min_freq
        self.max_freq = max_freq

    def add_samples(self, samples):
        self.samples = np.roll(self.samples, -len(samples))

        self.samples[-len(samples):] = samples

        thread = Thread(target=self.make_spectrum)

        thread.start()

    def make_spectrum(self):
        ifft = scipy.fftpack.rfft(self.samples)

        spectrum = ifft[self.min_freq:]

        xs = np.linspace(0, 1, len(spectrum))

        ys = np.abs(spectrum) / (len(self.samples) / 2)

        freq_range = self.max_freq - self.min_freq

        log_xs = (np.log2(xs * freq_range + self.min_freq) - np.log2(self.min_freq)) / (np.log2(self.max_freq) - np.log2(self.min_freq))

        interpolate = scipy.interpolate.interp1d(log_xs, ys, fill_value='extrapolate')

        width = self.surface.get_width()

        self.spectrum = interpolate(np.linspace(0, 1, width))

    def refresh(self):
        self.surface.fill(0)

        height = self.surface.get_height()

        if self.spectrum is not None:
            for x, y in enumerate(self.spectrum):
                pygame.draw.rect(
                    self.surface,
                    (255, 255, 255),
                    [x, height - (y * height * 8), 1, height]
                )

            pygame.display.flip()

sys.path.insert(0, 'lib')

parser = argparse.ArgumentParser(prog='instrument')

parser.add_argument('path', nargs='?')

parser.add_argument('--midi', default=True, action=argparse.BooleanOptionalAction)
parser.add_argument('--keyboard', default=False, action=argparse.BooleanOptionalAction)
parser.add_argument('--sample_rate', type=int, default=44100)

args = parser.parse_args()

path = args.path
sample_rate = args.sample_rate

basename = os.path.basename(path)

spec = importlib.util.spec_from_file_location(basename, path)

module = importlib.util.module_from_spec(spec)

sys.modules[basename] = module

spec.loader.exec_module(module)

instrument = module.Instrument(sample_rate)

spectrum_analyzer = SpectrumAnalyzer()

def callback(in_data, frame_count, time_info, status):
    samples = instrument.get_samples(frame_count)

    spectrum_analyzer.add_samples(samples)

    return (samples.clip(-1, 1).astype(np.float32).tobytes(), pyaudio.paContinue)

p = pyaudio.PyAudio()

stream = p.open(
    rate=sample_rate,
    output=True,
    format=pyaudio.paFloat32,
    channels=1,
    stream_callback=callback
)

if args.midi:
    pygame.midi.init()

    input_id = pygame.midi.get_default_input_id()

    midi_input = pygame.midi.Input(input_id)

if args.keyboard:
    keyboard_listener = pynput.keyboard.Listener(on_press=instrument.on_key_press)

    keyboard_listener.start()

mtime = os.path.getmtime(path)

running = True

while running:
    new_mtime = os.path.getmtime(path)

    if new_mtime != mtime:
        mtime = new_mtime

        spec.loader.exec_module(module)

        instrument = module.Instrument(sample_rate)

        if args.keyboard:
            keyboard_listener.stop()

            keyboard_listener = pynput.keyboard.Listener(on_press=instrument.on_key_press)

            keyboard_listener.start()

    if args.midi:
        events = midi_input.read(16)

        for event in events:
            thread = Thread(target=lambda: instrument.on_midi_event(event[0]))

            thread.start()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    spectrum_analyzer.refresh()

stream.close()

p.terminate()