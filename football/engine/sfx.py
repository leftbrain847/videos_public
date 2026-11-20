"""Sound effects, synthesized offline (no downloads, no licensing): whistle, kick, catch, whoosh, crowd bed, crowd roar.

Each is a pure function of its settings in SFX, rendered once to engine/audio/sfx/<name>.wav by `python3 sfx.py`.
These are a stand-in: swap any file for a recorded CC0 effect of the same name and the mix picks it up.
"""
import numpy as np
import soundfile as sf
from pathlib import Path

SR = 44100
OUT = Path(__file__).parent / "audio" / "sfx"
SFX = {
    "whistle":  {"seconds": 0.9, "freqs": [2950, 3110], "trill_hz": 34, "gain": 0.32},
    "kick":     {"seconds": 0.35, "thump_hz": 62, "click": 0.5, "gain": 0.9},
    "catch":    {"seconds": 0.18, "band": [180, 900], "gain": 0.7},
    "whoosh":   {"seconds": 0.55, "sweep": [400, 3800], "gain": 0.35},
    "crowd":    {"seconds": 12.0, "band": [250, 2600], "swell": 0.15, "gain": 0.22},
    "roar":     {"seconds": 4.0, "band": [200, 3200], "attack": 0.25, "gain": 0.6},
}


def _noise(n, rng, pink=True):
    w = rng.standard_normal(n)
    if not pink:
        return w
    f = np.fft.rfft(w); k = np.arange(len(f)); k[0] = 1
    return np.fft.irfft(f / np.sqrt(k), n)


def _band(x, lo, hi):
    f = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < lo) | (fr > hi)] = 0
    return np.fft.irfft(f, len(x))


def _norm(x, g):
    return (x / (np.max(np.abs(x)) + 1e-9) * g).astype(np.float32)


def render(name, rng):
    c = SFX[name]; n = int(c["seconds"] * SR); t = np.arange(n) / SR
    if name == "whistle":        # pea whistle: two close tones, trilled, quick attack and release
        x = sum(np.sin(2 * np.pi * f * t) for f in c["freqs"]) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * c["trill_hz"] * t)))
        env = np.minimum(1, t / 0.02) * np.minimum(1, (c["seconds"] - t) / 0.08)
        x = x * env + _band(_noise(n, rng, False), 2500, 4000) * 0.05 * env
    elif name == "kick":         # boot on ball: pitched-down thump plus a short click
        f = c["thump_hz"] * (1 + 2 * np.exp(-t * 40))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
        x += _band(_noise(n, rng, False), 1500, 6000) * np.exp(-t * 120) * c["click"]
    elif name == "catch":        # ball into hands: a dull, damped slap
        x = _band(_noise(n, rng, False), *c["band"]) * np.exp(-t * 35)
    elif name == "whoosh":       # air past the camera: band-passed noise sweeping up then fading
        x = np.zeros(n); seg = 512
        for i in range(0, n, seg):
            u = i / n; lo = c["sweep"][0] + (c["sweep"][1] - c["sweep"][0]) * u
            x[i:i + seg] = _band(_noise(seg, rng), lo, lo * 1.8)[: len(x[i:i + seg])]
        x *= np.sin(np.pi * t / c["seconds"]) ** 2
    elif name == "crowd":        # stadium bed: pink noise in the voice band with slow swells (loops)
        x = _band(_noise(n, rng), *c["band"]) * (1 + c["swell"] * np.sin(2 * np.pi * t / 4.5))
        fade = int(0.5 * SR); x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
    elif name == "roar":         # touchdown eruption: fast rise, long tail
        x = _band(_noise(n, rng), *c["band"]) * np.minimum(1, t / c["attack"]) * np.exp(-np.maximum(0, t - 1.2) * 0.9)
    return _norm(np.stack([x, np.roll(x, 37)], 1), c["gain"])


def main():
    OUT.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(7)
    for name in SFX:
        sf.write(str(OUT / f"{name}.wav"), render(name, rng), SR, subtype="PCM_16")
    print("sfx:", ", ".join(SFX))


if __name__ == "__main__":
    main()
