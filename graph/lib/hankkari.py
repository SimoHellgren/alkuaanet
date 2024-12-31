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


def parse_note(note):
    tone, *accidents, octave = note

    return (
        NATURALS[tone] + sum(ACCIDENTALS[a] for a in accidents) + 12 * (int(octave) - 4)
    )


def profile(tones):
    first, *rest = map(parse_note, tones)
    return [0] + [tone - first for tone in rest]


def is_hankkari(tones):
    return profile(tones) == [0, -4, -9, -16]
