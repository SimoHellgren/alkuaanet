"""sound generation happens here"""
from itertools import islice, tee, count, cycle
import numpy as np
from .notes import note_to_frequency
from typing import TypeAlias, Callable

take = lambda n, seq: islice(seq, 0, n)
nwise = lambda seq, n=2: zip(*(islice(it, i, None) for i, it in enumerate(tee(seq, n))))

Milliseconds: TypeAlias = int
Sound: TypeAlias = Callable[[np.ndarray[Milliseconds]], np.ndarray]


def sinewave(freq: float, amp: float) -> Sound:
    """return a function that produces a sinewave with a given frequency and amplitude.
    The returned function takes an array of time values in milliseconds as input.
    """
    return lambda xs: np.sin(2 * np.pi * freq * xs / 1000) * amp


def sound(freq: float, amps: list[float]) -> Sound:
    """Given a basefrequency and an iterable of amplitudes in range [0,1],
    return a function that produces a compound sinewave of the basefrequency
    and its overtones
    """
    funcs = [sinewave(freq * i, amp) for i, amp in enumerate(amps, 1)]

    return lambda xs: np.sum([f(xs) for f in funcs], 0)


def adsr(duration, attack, decay, sustain, release):
    """Simple ADSR envelope. Produces a volume according to the parameters given,
    when the input is in the range [0, duration], otherwise 0 (off).
    """
    a = lambda x: 1 / attack * x
    d = lambda x: (sustain - 1) / decay * (x - attack) + 1
    s = lambda x: sustain
    r = lambda x: sustain - 1 / release * (x - duration + release - 1)
    default = lambda x: 0

    limits = map(lambda x: x, [0, attack, attack + decay, duration - release, duration])
    pairs = list(nwise(limits))

    return lambda xs: np.piecewise(
        xs, [(xs >= s) & (xs < e) for s, e in pairs], [a, d, s, r, default]
    )


def play_sequence(
    notes: list[str],
    note_duration: Milliseconds,
    offset: Milliseconds,
    sample_rate=44100,
):
    """Creates a compound wave that plays given notes one after the other, starting at 'offset' intervals
    Applies a default sound. Timings are controlled by applying ADSR-envelopes and shifting the input
    in such a way that each note plays at the desired time. Resulting array is scaled such that values are
    in range [-1, 1], so it can be directly passed on to a writer function.

    NB: at least sound and envelope should be refactored / extracted to be parameters to this function
    """
    n = len(notes)

    # get the total duration by calculating when the last note starts and adding note_duration
    # also add .25s to avoid excessive popping noise at the end
    duration = (n - 1) * offset + note_duration + 250

    xs = np.linspace(0, duration, int(duration * sample_rate / 1000))

    fs = map(note_to_frequency, notes)

    # produce reciprocal amplitudes to generate sounds
    amps = (1 / np.power(e, 1.1) for e in count(1))
    pattern = tuple(take(10, (a * b for a, b in zip(amps, cycle((1, 0))))))

    sounds = [sound(f, pattern) for f in fs]

    envelope = adsr(note_duration, 90, 50, 0.8, 25)

    samples = np.sum(
        [s(xs) * envelope(xs - i * offset) for i, s in enumerate(sounds)], 0
    )

    scaled = samples / np.abs(samples).max()

    return scaled
