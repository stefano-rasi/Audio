import os
import sys
import time
import argparse
import importlib.util

import numpy as np
import pyaudio

from threading import Thread

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

t = 0

events = []

def seconds(s):
    return s * sample_rate

class EventLoopThread(Thread):
    def __init__(self, track):
        super().__init__()

        self.track = track

    def run(self):
        global t, events

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

threads = []

for track in song.tracks:
    thread = EventLoopThread(track)

    threads.append(thread)

    thread.start()

sounds = []

def callback(in_data, frame_count, time_info, status):
    global t, events, sounds

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

while True:
    new_mtime = os.path.getmtime(path)

    if new_mtime != mtime:
        mtime = new_mtime

        spec.loader.exec_module(module)

        song = module.Song(sample_rate)

        for thread in threads:
            thread.stop()

        events.clear()

        threads.clear()

        for track in song.tracks:
            thread = EventLoopThread(track)

            threads.append(thread)

            thread.start()
    else:
        try:
            time.sleep(0.1)
        except:
            break

for thread in threads:
    thread.stop()

stream.close()

p.terminate()