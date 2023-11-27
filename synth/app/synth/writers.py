"""functions for writing opus (and wav) files from samples
    note: you'll need opusenc installed if you want to make opus files.
          If ran on Windows, you need to have opusenc on wsl (windows subsystem for linux) 
"""

import sys
import wave
from io import BytesIO
import struct
import subprocess
from .synth import combine, arpeggio, triangle_wave


def make_opus_blob(tones, tone_duration=1000, offset=500, sample_rate=44100):
    arpeggio_sound, arpeggio_duration = arpeggio(
        tones, tone_duration, offset, triangle_wave(10)
    )

    samples = combine(arpeggio_sound, arpeggio_duration, sample_rate)
    opus_bytes = samples_to_opus(samples, sample_rate)
    return opus_bytes


def samples_to_wav_bytes(samples, sample_rate=44100):
    stream = BytesIO()
    with wave.open(stream, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            f.writeframes(struct.pack("h", int(s * 32767.0)))

    stream.seek(0)

    return stream


def wav_bytes_to_opus(wav_bytes):
    # call opusenc through wsl if on windows
    command = "wsl opusenc - -" if sys.platform == "win32" else "opusenc - -"
    result = subprocess.run(command.split(), capture_output=True, input=wav_bytes)
    return result.stdout


def samples_to_opus(samples, sample_rate=44100):
    wav_bytes = samples_to_wav_bytes(samples, sample_rate).read()

    return wav_bytes_to_opus(wav_bytes)
