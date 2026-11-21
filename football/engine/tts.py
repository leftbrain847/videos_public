"""Narration: one af_heart line per script line (Kokoro), fitted to exactly TARGET seconds, plus caption timing.

python3 tts.py <video_dir> --models <dir with kokoro-v1.0.onnx and voices-v1.0.bin>
Writes <video_dir>/build/narration.wav and timing.json.
"""
import argparse, json, re, sys
from pathlib import Path
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402  speech rules + pronunciation lookup (no dependencies)

VOICE = {
    "engine": "kokoro",
    "voice": "af_heart",       # locked by J (2026-11-20): the Mastery Field Guide voice
    "lang": "en-us",
    "speed": 1.0,              # starting speed; raised in steps up to max_speed if the script runs long
    "max_speed": voice.RULES["max_speed"],   # 1.06: faster sounds rushed. If the script doesn't fit, cut words
    "speed_step": 0.03,
}
TIMING = {
    "target_s": 60.0,          # every video is exactly this long
    "lead_in_s": 0.15,
    "gap_s": 0.28,             # pause between lines (stretched to fill, up to max_gap_s)
    "max_gap_s": 0.9,
    "tail_min_s": 0.6,         # silence after the last line (the end-card beat)
    "words_per_chunk": 3,      # caption chunk size
    "fade_ms": 6,
}


def chunks(text, start, end, n):
    words = [w for w in re.split(r"\s+", text.upper().strip()) if w]
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= n or re.search(r"[.?!,:;]$", w) and len(cur) >= 2:
            groups.append(cur); cur = []
    if cur:
        if groups and len(cur) == 1:
            groups[-1] += cur
        else:
            groups.append(cur)
    weights = [sum(len(w) for w in g) + 2 for g in groups]
    tot = sum(weights); t = start; out = []
    for g, wgt in zip(groups, weights):
        d = (end - start) * wgt / tot
        out.append({"words": g, "start": round(t, 3), "end": round(t + d, 3)}); t += d
    return out


def phonemes(k, text):
    """Text -> Kokoro phonemes, with pronunciation.json overrides spliced in (case-sensitive, whole words, possessives)."""
    return voice.phonemize(text, lambda chunk: k.tokenizer.phonemize(chunk, VOICE["lang"]))


def synth(k, text, speed):
    if any(is_ph for is_ph, _ in voice.split_overrides(text)):
        x, sr = k.create(phonemes(k, text), voice=VOICE["voice"], speed=speed, lang=VOICE["lang"], is_phonemes=True)
    else:
        x, sr = k.create(text, voice=VOICE["voice"], speed=speed, lang=VOICE["lang"])
    x = np.asarray(x, dtype=np.float32)
    # trim near-silence at both ends, then fade to avoid Kokoro's onset click
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz):
        x = x[max(0, nz[0] - int(0.02 * sr)): nz[-1] + int(0.06 * sr)]
    f = int(TIMING["fade_ms"] / 1000 * sr)
    if f and len(x) > 2 * f:
        x[:f] *= np.linspace(0, 1, f, dtype=np.float32); x[-f:] *= np.linspace(1, 0, f, dtype=np.float32)
    return x, sr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video_dir"); ap.add_argument("--models", required=True)
    a = ap.parse_args()
    vd = Path(a.video_dir); S = json.loads((vd / "video.json").read_text())
    if S.get("voice") == "v2":   # a v2 script is spoken exactly as written: refuse it if it breaks a speech rule
        errs = [m for _, m in voice.lint_script(S) if "won't fit" not in m]
        if errs:
            sys.exit("speech rules failed (run check.py):\n  " + "\n  ".join(errs))
    from kokoro_onnx import Kokoro
    k = Kokoro(str(Path(a.models) / "kokoro-v1.0.onnx"), str(Path(a.models) / "voices-v1.0.bin"))
    T = float(S.get("target_s", TIMING["target_s"])); speed = VOICE["speed"]   # 60 s shorts; story series set 90
    while True:
        clips = [synth(k, l["text"], speed) for l in S["lines"]]
        sr = clips[0][1]; speech = sum(len(c[0]) for c in clips) / sr
        need = TIMING["lead_in_s"] + speech + TIMING["gap_s"] * (len(clips) - 1) + TIMING["tail_min_s"]
        if need <= T or speed >= VOICE["max_speed"]:
            break
        speed = round(speed + VOICE["speed_step"], 3)
    if need > T:
        sys.exit(f"script too long: {need:.1f}s at speed {speed} (target {T}s). Cut words.")
    spare = T - need
    gap = min(TIMING["max_gap_s"], TIMING["gap_s"] + spare / max(1, len(clips) - 1))
    audio = np.zeros(int(T * sr), dtype=np.float32); t = TIMING["lead_in_s"]; lines = []
    for (x, _), l in zip(clips, S["lines"]):
        i = int(t * sr); audio[i:i + len(x)] += x[: len(audio) - i]
        s, e = t, t + len(x) / sr
        lines.append({"start": round(s, 3), "end": round(e, 3), "chunks": chunks(l.get("cap", l["text"]), s, e, TIMING["words_per_chunk"])})
        t = e + gap
    # each line's visual span runs until the next line starts; the last runs to the end
    for i in range(len(lines) - 1):
        lines[i]["end"] = lines[i + 1]["start"]
    lines[-1]["end"] = T
    b = vd / "build"; b.mkdir(exist_ok=True)
    sf.write(str(b / "narration.wav"), audio, sr, subtype="PCM_16")
    (b / "timing.json").write_text(json.dumps({"target_s": T, "speed": speed, "voice": VOICE["voice"], "lines": lines}, indent=1))
    print(f"narration {T}s, speech {speech:.1f}s, speed {speed}, gap {gap:.2f}s")


if __name__ == "__main__":
    main()
