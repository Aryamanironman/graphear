import math, wave, struct
import numpy as np

SR = 44100
DUR = 42.0
N = int(SR * DUR)
t = np.linspace(0, DUR, N, endpoint=False)

# ---- same data as the video ----
def make_series(n, start, drift, wobble, spike_at, spike_amt):
    a = []
    for i in range(n):
        base = start + drift * (i / (n - 1))
        w = math.sin(i / 3.1) * wobble + math.sin(i / 7.4) * wobble * 0.45
        v = base + w
        if i == spike_at:
            v += spike_amt
        a.append(v)
    return a

DATA = make_series(64, 318, 82, 3.2, 47, 26)
N_PTS = len(DATA)
LO, HI = min(DATA) - 6, max(DATA) + 6

def freq(v):
    r = (v - LO) / (HI - LO)
    return 196.0 * (2 ** (r * 2.0))

# ---- helpers ----
def env(start, dur, attack=0.02, release=None, curve=4.0):
    """Smooth percussive envelope over the whole buffer."""
    e = np.zeros(N)
    s = int(start * SR); d = int(dur * SR)
    if s >= N: return e
    d = min(d, N - s)
    x = np.linspace(0, 1, d, endpoint=False)
    a = max(1, int(attack * SR))
    up = np.minimum(1, np.arange(d) / a)
    down = np.exp(-curve * x)
    if release:
        rel_n = int(release * SR)
        rr = np.ones(d)
        if rel_n < d:
            rr[-rel_n:] = np.linspace(1, 0, rel_n) ** 1.5
        down = down * rr
    e[s:s + d] = up * down
    return e

def tone(start, dur, f, amp=0.1, pan=0.0, kind='sine', attack=0.015, curve=4.0):
    e = env(start, dur, attack=attack, curve=curve)
    ph = 2 * np.pi * f * (t - start)
    if kind == 'sine':
        w = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    elif kind == 'tri':
        w = 2 / np.pi * np.arcsin(np.sin(ph))
    else:
        w = np.sin(ph)
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([w * e * amp * l, w * e * amp * r])

def pad(start, dur, freqs, amp=0.05, attack=1.2, release=2.0):
    out = np.zeros((2, N))
    for i, f in enumerate(freqs):
        e = env(start, dur, attack=attack, curve=0.9)
        # gentle fade at tail
        s = int(start * SR); d = min(int(dur * SR), N - s)
        if d > 0:
            rel = np.ones(d)
            rn = min(d, int(release * SR))
            rel[-rn:] *= np.linspace(1, 0, rn) ** 2
            e[s:s + d] *= rel
        det = 1 + (i - len(freqs) / 2) * 0.0015
        w = (np.sin(2 * np.pi * f * det * (t - start)) +
             0.5 * np.sin(2 * np.pi * f * 2 * det * (t - start)) * 0.3)
        pan = (i / max(1, len(freqs) - 1) - 0.5) * 0.6
        l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
        out[0] += w * e * amp * l
        out[1] += w * e * amp * r
    return out

mix = np.zeros((2, N))

# ---- 1. bed ----
mix += pad(0.0, 10.2, [110.0, 164.81, 220.0, 277.18], amp=0.030, attack=2.2, release=1.0)
mix += pad(19.6, 12.4, [174.61, 220.0, 261.63, 329.63], amp=0.026, attack=1.6, release=1.2)
mix += pad(31.6, 10.6, [130.81, 196.0, 261.63, 329.63], amp=0.026, attack=1.4, release=1.6)

# low heartbeat pulse under the problem section
for bt in [4.6, 5.6, 6.6, 7.6, 8.6]:
    mix += tone(bt, 0.9, 55, amp=0.055, kind='sine', attack=0.01, curve=3.2)

# ---- 2. section markers ----
for bt, f, a in [(0.3, 110, .05), (4.6, 82.4, .07), (9.6, 98, .05), (19.8, 110, .06),
                 (25.8, 87.31, .05), (31.8, 98, .05), (37.2, 110, .06)]:
    mix += tone(bt, 1.6, f, amp=a, kind='sine', attack=0.008, curve=2.2)

# ---- 3. sonification: 10.0 -> 18.8, 64 notes ----
T0, T1 = 10.0, 18.8
step = (T1 - T0) / N_PTS
for i, v in enumerate(DATA):
    st = T0 + i * step
    f = freq(v)
    # melodic note
    mix += tone(st, step * 1.35, f, amp=0.085, pan=(i % 5 - 2) * 0.06,
                attack=0.008, curve=3.2)
    # soft octave shimmer
    mix += tone(st, step * 1.1, f * 2, amp=0.016, pan=0.25, attack=0.01, curve=4.5)
    if i % 4 == 0:
        mix += tone(st, 0.16, 196 / 2, amp=0.035, attack=0.004, curve=5.0)
# accent the spike
spike_t = T0 + 47 * step
mix += tone(spike_t, 1.4, freq(DATA[47]) * 1.5, amp=0.05, attack=0.01, curve=1.6)
mix += tone(spike_t, 1.2, freq(DATA[47]), amp=0.10, attack=0.006, curve=1.8)

# ---- 4. mapping section tones ----
mix += tone(20.55, 1.1, 196, amp=0.09, pan=-0.1, attack=0.02, curve=1.6)   # low
mix += tone(21.15, 1.1, 784, amp=0.06, pan=0.1, attack=0.02, curve=1.6)    # high
# sweep up
s0, s1 = 21.9, 23.4
seg = t[(t >= s0) & (t < s1)]
if len(seg):
    f = 220 * (2 ** ((seg - s0) / (s1 - s0) * 1.6))
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.sin(np.linspace(0, np.pi, len(seg))) ** 0.7
    idx = np.where((t >= s0) & (t < s1))[0]
    w = (np.sin(ph) + 0.2 * np.sin(2 * ph)) * e * 0.055
    mix[0, idx] += w
    mix[1, idx] += w
# left / right pair
mix += tone(23.5, 1.3, 329.63, amp=0.085, pan=-0.85, attack=0.02, curve=1.5)
mix += tone(23.9, 1.3, 440.0, amp=0.075, pan=0.85, attack=0.02, curve=1.5)

# ---- 5. three-ways chord ----
mix += pad(26.0, 5.4, [220.0, 277.18, 329.63, 440.0], amp=0.032, attack=0.8, release=1.0)

# ---- 6. step ticks ----
for st in [32.4, 32.95, 33.5]:
    mix += tone(st, 0.22, 1320, amp=0.035, attack=0.003, curve=6.0)

# ---- 7. close ----
mix += pad(37.2, 4.6, [110.0, 164.81, 220.0, 277.18, 329.63], amp=0.042, attack=0.35, release=2.0)
mix += tone(38.4, 1.8, 880, amp=0.028, pan=0.2, attack=0.02, curve=2.0)

# ---- master ----
# gentle bus compression / soft clip
mix = np.tanh(mix * 1.25) / 1.25
# global fade in/out
fade_in = np.clip(t / 1.2, 0, 1) ** 1.5
fade_out = np.clip((DUR - 0.1 - t) / 1.6, 0, 1) ** 1.2
mix *= np.stack([fade_in * fade_out, fade_in * fade_out])
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89
# subtle stereo width
mix[0] = mix[0] * 0.98 + mix[1] * 0.04
mix[1] = mix[1] * 0.98 + mix[0] * 0.04
mix = np.clip(mix, -1, 1)

pcm = (mix.T * 32767).astype(np.int16)
with wave.open('out/soundtrack.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote out/soundtrack.wav', pcm.shape, 'peak', float(peak))
