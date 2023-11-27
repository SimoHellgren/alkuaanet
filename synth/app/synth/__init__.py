from .synth import combine, arpeggio
from .writers import samples_to_opus


def make_opus_blob(tones, tone_duration=1000, offset=500, sample_rate=44100):
    arpeggio_sound, arpeggio_duration = arpeggio(tones, tone_duration, offset)

    samples = combine(arpeggio_sound, arpeggio_duration, sample_rate)
    opus_bytes = samples_to_opus(samples, sample_rate)
    return opus_bytes
