"""Listen-back: transcribe each narrated line with an open speech-to-text model and diff it against `text`.

python3 engine/listen.py videos/<id>      -> prints misheard words, writes videos/<id>/build/listen.json
A word the model mishears usually means Kokoro mispronounced it. Needs faster-whisper (the render workflow installs it
and downloads the model from Hugging Face, which Actions can reach). Numbers the model writes as digits are spoken
back into words with voice.say() before comparing.
"""
import difflib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402

MODEL = {"name": "base.en", "beam": 5}


def words(text):
    """Normalize to comparable spoken words: digits spoken out, punctuation and case dropped."""
    out = []
    for tok in text.replace("-", " ").split():
        s = voice.say(tok) if re.search(r"\d", tok) else None
        out += (s or tok).split()
    return [w for w in (re.sub(r"[^a-z']", "", w.lower()).strip("'") for w in out) if w]


def diff(said, heard):
    """[(expected words, heard words)] for each place the transcript differs from the script."""
    a, b = words(said), words(heard)
    return [(" ".join(a[i1:i2]), " ".join(b[j1:j2])) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes() if op != "equal"]


def main():
    from faster_whisper import WhisperModel
    import soundfile as sf
    vd = Path(sys.argv[1]); S = json.loads((vd / "video.json").read_text()); T = json.loads((vd / "build" / "timing.json").read_text())
    audio, sr = sf.read(str(vd / "build" / "narration.wav"), dtype="float32")
    if sr != 16000:   # whisper wants 16 kHz mono
        import numpy as np
        n = int(len(audio) * 16000 / sr); audio = np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype("float32")
    m = WhisperModel(MODEL["name"], device="cpu", compute_type="int8")
    report, flagged = [], 0
    for i, (l, t) in enumerate(zip(S["lines"], T["lines"]), 1):
        a, b = int(max(0, t["start"] - 0.1) * 16000), int((t["end"] + 0.05) * 16000)   # a line's span runs to the next line
        segs, _ = m.transcribe(audio[a:b], language="en", beam_size=MODEL["beam"], condition_on_previous_text=False)
        heard = " ".join(s.text for s in segs).strip()
        d = diff(l["text"], heard); flagged += bool(d)
        report.append({"line": i, "text": l["text"], "heard": heard, "diff": d})
        for exp, got in d:
            print(f"line {i}: script \"{exp}\" -> heard \"{got}\"")
    (vd / "build" / "listen.json").write_text(json.dumps(report, indent=1))
    print(f"listen-back: {flagged} of {len(report)} lines differ")


if __name__ == "__main__":
    main()
