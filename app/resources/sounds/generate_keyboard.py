"""Generate mechanical keyboard style typing sounds."""
import math
import wave
import random


def write_wav(path, freq, duration_ms, volume=0.15, sample_rate=44100, decay=True, click=False):
    """Generate a single WAV file with optional click/decay."""
    n_samples = int(sample_rate * duration_ms / 1000)
    frames = []
    for i in range(n_samples):
        t = i / sample_rate

        if click and i < 100:  # Initial click transient
            click_env = 1.0 - (i / 100)
            value = volume * 2.0 * click_env * (random.random() * 0.5 + 0.5) * math.sin(2 * math.pi * (freq * 3) * t)
        else:
            value = volume * math.sin(2 * math.pi * freq * t)

        # Apply decay envelope
        if decay:
            decay_factor = math.exp(-t * 50)  # Fast decay
            value *= decay_factor

        # Soft clipping
        value = max(-1, min(1, value))
        sample = int(value * 32767)
        frames.append(sample.to_bytes(2, "little", signed=True))

    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(b"".join(frames))


# Mechanical keyboard click sounds - variation pool
base_dir = "D:/MMMM/DOWNLOAD/new/PersianTypeffffff/PersianType/app/resources/sounds"

# Normal keypress variations (light mechanical clicks)
for i in range(5):
    freq = random.uniform(800, 1200)
    dur = random.randint(30, 50)
    vol = random.uniform(0.08, 0.15)
    write_wav(f"{base_dir}/click_{i}.wav", freq, dur, volume=vol, click=True)

# Spacebar - deeper thock
write_wav(f"{base_dir}/space.wav", 150, 80, volume=0.12, decay=True, click=True)

# Error sound - subtle but distinct (lower pitch, slightly longer)
for i in range(3):
    freq = random.uniform(180, 250)
    dur = random.randint(80, 120)
    write_wav(f"{base_dir}/error_{i}.wav", freq, dur, volume=0.1, decay=True, click=False)

print("Mechanical keyboard sounds generated.")