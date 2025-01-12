class Song:
    def __init__(self):
        self.tracks = []

    def add_track(self, track):
        self.tracks.append(track)

class Track:
    def __init__(self, loop=False):
        self.loop = loop

        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

class Section:
    def __init__(self, repeats=1):
        self.bars = []

        self.repeats = repeats

    def add_bar(self, bar):
        self.bars.append(bar)

class Bar:
    def __init__(self, beats):
        self.beats = beats

        self.events = []

    def play(self, beats, sound):
        for beat in beats:
            self.events.append({ 'beat': beat, 'sound': sound })