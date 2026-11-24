"""Generate simple WAV typing sounds (lightweight local resources)."""
import math
import wave


def write_wav(path, freq, duration_ms, volume=0.1, sample_rate=44100):
    n_samples = int(sample_rate * duration_ms / 1000)
    frames = []
    for i in range(n_samples):
        t = i / sample_rate
        value = volume * math.sin(2 * math.pi * freq * t)
        # apply simple fade-out to avoid clicks
        fade = min(1.0, i / (n_samples * 0.1)) if i < n_samples * 0.1 else 1.0
        value *= fade
        sample = int(max(-1, min(1, value)) * 32767)
        frames.append(sample.to_bytes(2, "little", signed=True))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"".join(frames))


write_wav("D:/MMMM/DOWNLOAD/new/PersianTypeffffff/PersianType/app/resources/sounds/correct.wav", 880, 80, volume=0.08)
write_wav("D:/MMMM/DOWNLOAD/new/PersianTypeffffff/PersianType/app/resources/sounds/error.wav", 220, 120, volume=0.08)
write_wav("D:/MMMM/DOWNLOAD/new/PersianTypeffffff/PersianType/app/resources/sounds/space.wav", 1320, 60, volume=0.06)
print("Sound files generated.")
