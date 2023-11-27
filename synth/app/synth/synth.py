"""sound generation happens here"""
from itertools import islice, tee, count, cycle
import numpy as np
from .notes import note_to_frequency
from typing import TypeAlias, Callable

take = lambda n, seq: islice(seq, 0, n)
nwise = lambda seq, n=2: zip(*(islice(it, i, None) for i, it in enumerate(tee(seq, n))))

Milliseconds: TypeAlias = int
Sound: TypeAlias = Callable[[np.ndarray[Milliseconds]], np.ndarray]
Volume: TypeAlias = float


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


def triangle_wave(n: int) -> Sound:
    # produce amplitudes with decay in amplitude
    amplitudes = (1 / np.power(e, 1.1) for e in count(1))

    # only every other harmonic should have a non-zero amplitude
    every_other = (a * b for a, b in zip(amplitudes, cycle([1, 0])))

    # coerce to list here, otherwise subsequent calls will use the same generator
    amplitudes = list(take(n, every_other))

    # return the first n amplitudes
    return lambda f: sound(f, amplitudes)


def adsr(
    duration: Milliseconds,
    attack: Milliseconds,
    decay: Milliseconds,
    sustain: float,
    release: Milliseconds,
) -> Volume:
    """Simple ADSR envelope. Produces a volume according to the parameters given,
    when the input is in the range [0, duration], otherwise 0 (off).
    In order to produce sounds from time t, the input must be shifted by t.
    Sustain is a float in range [0, 1] that determines the volume after the attack and decay phases.
    """
    # increase volume linearly from 0 to 1 for `attack` milliseconds
    a = lambda x: 1 / attack * x
    # decrease volume linearly from 1 to `sustain` for `decay` milliseconds
    d = lambda x: (sustain - 1) / decay * (x - attack) + 1

    # sustain volume until `release` milliseconds before end of note
    s = lambda x: sustain

    # decrease volume to 0 for `release` milliseconds
    r = lambda x: sustain - 1 / release * (x - duration + release - 1)
    default = lambda x: 0

    limits = np.array([0, attack, attack + decay, duration - release, duration])
    pairs = list(nwise(limits))

    return lambda xs: np.piecewise(
        xs, [(xs >= s) & (xs < e) for s, e in pairs], [a, d, s, r, default]
    )


def arpeggio(
    notes: list[str], note_duration: Milliseconds, offset: Milliseconds, sound: Sound
):
    """Produces a list of notes and times at which they should be played."""

    # total duration = last note starttime + note duration
    n = len(notes)
    duration = (n - 1) * offset + note_duration

    frequencies = map(note_to_frequency, notes)
    sounds = map(sound, frequencies)

    result = lambda xs: (
        s(xs) * adsr(note_duration, 90, 50, 0.8, 25)(xs - i * offset)
        for i, s in enumerate(sounds)
    )

    return lambda xs: np.sum(result(xs), 0), duration


def chord(notes: list[str], duration: Milliseconds, sound: Sound):
    frequencies = map(note_to_frequency, notes)
    sounds = map(sound, frequencies)

    result = lambda xs: (s(xs) * adsr(duration, 90, 50, 0.8, 25)(xs) for s in sounds)

    return lambda xs: np.sum(result(xs), 0), duration


def combine(
    sound,
    duration: Milliseconds,
    sample_rate=44100,
):
    """Creates a compound wave of given sounds. Sound array is scaled such that values are
    in range [-1, 1], so it can be directly passed on to a writer function.
    """
    # add 250ms to duration to avoid popping noise at the end
    total_duration = duration + 250
    xs = np.linspace(0, total_duration, int(total_duration * sample_rate / 1000))

    samples = sound(xs)
    scaled = samples / np.abs(samples).max()
    return scaled
