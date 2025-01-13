import os
import sys
import time
import argparse
import importlib.util

import scipy
import numpy as np
import pygame
import pyaudio

from threading import Thread

t = 0

events = []

def seconds(s):
    return s * sample_rate

class TrackThread(Thread):
    def __init__(self, track):
        super().__init__()

        self.track = track

    def run(self):
        t1 = 0

        self.running = True

        while True:
            for section in self.track.sections:
                for _ in range(section.repeats):
                    for bar in section.bars:
                        if callable(bar):
                            bar = bar()

                        for event in bar.events:
                            if not self.running:
                                return

                            t2 = t1 + event['beat'] * seconds(60 / bpm)

                            if t2 >= t:
                                sound = event['sound']

                                if callable(sound):
                                    sound = sound()

                                events.append({ 'time': t2, 'sound': sound })

                        t1 += bar.beats * seconds(60 / bpm)

                        while t1 - t > seconds(60):
                            if not self.running:
                                return

                            time.sleep(0.1)

            if not track.loop:
                break

    def stop(self):
        self.running = False

class SpectrumAnalyzer:
    def __init__(self, width=1024, height=512, min_freq=20, max_freq=20000):
        pygame.display.init()

        pygame.display.set_caption('Spectrum')

        self.spectrum = None

        self.min_freq = min_freq
        self.max_freq = max_freq

        self.samples = np.zeros(max_freq)

        self.surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)

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
                    [x, height - (y * height * 4), 1, height]
                )

            pygame.display.flip()

sys.path.insert(0, 'lib')

parser = argparse.ArgumentParser(prog='song')

parser.add_argument('path', nargs='?')
parser.add_argument('--bpm', type=int, default=120)
parser.add_argument('--sample_rate', type=int, default=44100)

args = parser.parse_args()

bpm = args.bpm
path = args.path
sample_rate = args.sample_rate

basename = os.path.basename(path)

spec = importlib.util.spec_from_file_location(basename, path)

module = importlib.util.module_from_spec(spec)

sys.modules[basename] = module

spec.loader.exec_module(module)

song = module.Song(sample_rate)

track_threads = []

for track in song.tracks:
    track_thread = TrackThread(track)

    track_threads.append(track_thread)

    track_thread.start()

sounds = []

spectrum_analyzer = SpectrumAnalyzer()

def callback(in_data, frame_count, time_info, status):
    global t

    for event in events[:]:
        if event['time'] <= t:
            sounds.append(event['sound'])

            events.remove(event)

    samples = np.zeros(frame_count)

    for sound in sounds[:]:
        s = sound.get_samples(frame_count)

        if s is None:
            sounds.remove(sound)
        else:
            samples += s

    t += frame_count

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

mtime = os.path.getmtime(path)

running = True

while running:
    new_mtime = os.path.getmtime(path)

    if new_mtime != mtime:
        mtime = new_mtime

        spec.loader.exec_module(module)

        song = module.Song(sample_rate)

        for track_thread in track_threads:
            track_thread.stop()

        events.clear()

        track_threads.clear()

        for track in song.tracks:
            track_thread = TrackThread(track)

            track_threads.append(track_thread)

            track_thread.start()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    spectrum_analyzer.refresh()

for track_thread in track_threads:
    track_thread.stop()

stream.close()

p.terminate()