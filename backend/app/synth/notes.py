"""This module defines how notes are converted to frequencies.
   Currently only 12-tone equal temperament, but this would be the place
   to implement other tuning systems. Base frequency can be edited on-demand.
"""

import math

# equal temperament
RATIO = math.pow(2, 1 / 12)

NATURALS = {
    "C": -9,
    "D": -7,
    "E": -5,
    "F": -4,
    "G": -2,
    "A": 0,
    "B": 2,
}

ACCIDENTALS = {"#": 1, "b": -1, "x": 2}


def note_to_frequency(note, basefreq=440):
    """convert note of format 'A#4' to a frequency, with respect
    to a basefrequency for A4. Handles an arbitrary number of
    accidentals.
    """
    tone, *accidents, octave = note

    offset = NATURALS[tone] + sum(ACCIDENTALS[a] for a in accidents)

    return basefreq * math.pow(RATIO, offset) * 2 ** (int(octave) - 4)
