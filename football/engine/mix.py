"""Audio for one video: af_heart narration on top, the piano bed ducked under it, and sound effects cued from the script.

python3 mix.py <video_dir>      -> <video_dir>/build/mix.wav (60 s, stereo, 44.1 kHz)
Effects are recorded, professionally made CC0 sounds (wyzowl/sfx-kit), never synthesized. Cues come from video.json:
in a play, a kick, each catch, each ball flight (whoosh) and a touchdown (`celebrate`: the crowd) land at their point
in the line; a set change gets a soft cut swish. A line can add its own: "sfx": [[u, "hit"]] (the reveal; one per video).
"""
import json, subprocess, sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).parent
SR = 44100
MIX = {
    "music": ROOT / "audio" / "piano.mp3",
    "music_db": -9.0,            # bed level before ducking (the file is already quiet: about -29 dB mean)
    "duck_db": -9.0,             # extra cut while Capy talks
    "duck_attack_s": 0.08, "duck_release_s": 0.45,
    "music_fade_s": [0.6, 1.5],
    "voice_db": 3.0,
    "sfx_db": {"kick": 0, "catch": -2, "whoosh": 2, "roar": -3, "cut": -10, "hit": -6},   # gains on files peaking near -10 dB
    "limit": 0.97,
}


def load(path, n=None):
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, "<f4").reshape(-1, 2).copy()
    if n is not None:
        x = np.tile(x, (int(np.ceil(n / len(x))), 1))[:n] if len(x) < n else x[:n]
    return x


def db(v):
    return 10 ** (v / 20)


def place(bus, clip, t, gain):
    i = int(t * SR); j = min(len(bus), i + len(clip))
    if 0 <= i < len(bus):
        bus[i:j] += clip[: j - i] * gain


def main():
    vd = Path(sys.argv[1]); S = json.loads((vd / "video.json").read_text()); T = json.loads((vd / "build" / "timing.json").read_text())
    n = int(T["target_s"] * SR)
    voice = load(vd / "build" / "narration.wav", n) * db(MIX["voice_db"])
    music = load(MIX["music"], n) * db(MIX["music_db"])
    # duck the music under the voice: envelope of the voice, smoothed with attack/release
    env = np.abs(voice).max(1); w = int(0.03 * SR); env = np.convolve(env, np.ones(w) / w, "same")
    talk = (env > 0.01).astype(np.float32)
    a, r = 1 / (MIX["duck_attack_s"] * SR), 1 / (MIX["duck_release_s"] * SR); g = np.empty(n, np.float32); cur = 0.0
    for k in range(n):
        cur = min(1.0, cur + a) if talk[k] > cur else max(0.0, cur - r); g[k] = cur
    music *= (1 - (1 - db(MIX["duck_db"])) * g)[:, None]
    fi, fo = (int(s * SR) for s in MIX["music_fade_s"])
    music[:fi] *= np.linspace(0, 1, fi)[:, None]; music[-fo:] *= np.linspace(1, 0, fo)[:, None]
    sfx = {p.stem: load(p) for p in (ROOT / "audio" / "sfx").glob("*.wav")}
    fx = np.zeros((n, 2), np.float32)
    cur_set = S.get("set")
    for i, line in enumerate(S["lines"]):
        L = T["lines"][i]
        if i and line.get("set") and line["set"] != cur_set and "cut" in sfx:
            place(fx, sfx["cut"], L["start"] - 0.05, db(MIX["sfx_db"]["cut"]))
        cur_set = line.get("set", cur_set)
        dur = L["end"] - L["start"]; cues = list(line.get("sfx", []))
        play = line.get("play") or {}
        for who in (play.get("cast") or {}).values():
            for u, act in who.get("actions", []):
                if act == "kick": cues.append([u + 0.12, "kick"])
                if act == "catch": cues.append([u, "catch"])
                if act == "celebrate": cues.append([u - 0.05, "roar"])
        if play.get("ball"):   # a whoosh for each real flight (a short toss under 4 units stays quiet)
            flights = play["ball"] if isinstance(play["ball"][0][0], list) else [play["ball"]]
            for f in flights:
                if sum((a - b) ** 2 for a, b in zip(f[0][1:], f[-1][1:])) ** 0.5 >= 4:
                    cues.append([f[0][0], "whoosh"])
        seen = set()
        for u, name in cues:
            key = name if name in ("roar", "hit") else (round(u, 2), name)   # one crowd roar / reveal hit per line
            if name in sfx and key not in seen:
                seen.add(key); place(fx, sfx[name], L["start"] + u * dur, db(MIX["sfx_db"].get(name, -8)))
    out = voice + music + fx
    peak = np.abs(out).max()
    if peak > MIX["limit"]:
        out *= MIX["limit"] / peak
    sf.write(str(vd / "build" / "mix.wav"), out, SR, subtype="PCM_16")
    print(f"mix: peak {peak:.2f}, sfx cues placed")


if __name__ == "__main__":
    main()
