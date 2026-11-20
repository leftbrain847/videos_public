"""Listen-back substitute: print exactly what Kokoro will be told to say, as phonemes, so misreads show before a render.

python3 engine/ipa.py videos/<id>        every line: text, then the phonemes Kokoro gets (overrides marked with *)
python3 engine/ipa.py Csonka "N F L"     single words or phrases
Uses Kokoro's own phonemizer (espeak-ng via kokoro-onnx), so it matches the render. Needs engine/setup.sh.
Scan for: digits read oddly, names that sound wrong, letters run together, a stress on the wrong syllable.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402
from kokoro_onnx.tokenizer import Tokenizer  # noqa: E402

T = Tokenizer()


def show(text):
    return " ".join(("*" + chunk) if is_ph else T.phonemize(chunk, "en-us") for is_ph, chunk in voice.split_overrides(text))


def main():
    for arg in sys.argv[1:]:
        vj = Path(arg) / "video.json"
        if vj.exists():
            for i, l in enumerate(json.loads(vj.read_text())["lines"], 1):
                print(f"{i:>2} {l['text']}\n   {show(l['text'])}")
                for w in voice.unsure_names(l["text"]):
                    print(f"   ? {w}: pronunciation not confirmed")
        else:
            print(f"{arg}: {show(arg)}")


if __name__ == "__main__":
    main()
