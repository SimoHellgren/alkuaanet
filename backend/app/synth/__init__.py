from .synth import play_sequence
from .writers import samples_to_opus

def make_opus_blob(tones, tone_duration=1, offset=.5, sample_rate=44100):
    samples = play_sequence(tones, tone_duration, offset, sample_rate)
    opus_bytes = samples_to_opus(samples, sample_rate)
    return opus_bytes