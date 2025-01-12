import numpy as np

def db_to_amplitude(db):
    return np.power(10, db / 20)

def power_to_amplitude(power, min_db=-60):
    db = power * (min_db * -1) + min_db

    return db_to_amplitude(db)