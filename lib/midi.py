import numpy as np

def note_to_pitch(midi_note):
    return np.power(2, (midi_note - 69) / 12) * 440