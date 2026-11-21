"""Speech rules for Capy's narration (Kokoro af_heart). No dependencies: check.py, tts.py and CI all use this.

Kokoro reads `text` exactly as written and picks its own emphasis, so the script is the only lever. These rules make
whole classes of misreads impossible instead of patching them one at a time (1978 read as "nineteen hundred seventy
eight", "AFC" as one word, "Csonka" as "C Sonka"). Rules are in GUIDELINES.md, "Writing for the voice".
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
RULES = {
    "max_sentence_words": 8,        # measured: 9+ words got a mid-sentence pause 57% of the time, 8 or fewer 9%
    "and_min_words": 4,             # "and" in a sentence this long joins two actions often enough to ban it outright
    "max_colons_per_line": 1,       # Kokoro always pauses at a colon: one deliberate beat at most
    "max_speed": 1.06,              # narration must fit the video (60 s, or target_s) at this Kokoro speed or less
    # fit estimate for CI (no Kokoro there): af_heart at speed 1.0 speaks about this many letters a second.
    # Measured 2026-11-20 on 9 scripts at speed 1.0: 11.9-14.1 letters/s, median 13.5. 13.0 leans toward flagging long
    # scripts. tts.py is the real gate; this catches long scripts in CI before a render.
    "letters_per_s": 13.0,
    "fit_margin_s": 0.0,
}
# Rule 1: `text` is exactly what is spoken. These never belong in it (digits and symbols go in `cap`).
SYMBOLS = re.compile(r"[0-9%$&/#@+=*<>_|\\~^\[\]{}]")
NON_ASCII = re.compile(r"[^\x00-\x7f’—…]")   # accents are spelled plainly (Maracana); curly ' — … ok
ABBREVIATIONS = {"vs", "mr", "mrs", "ms", "dr", "st", "jr", "sr", "approx", "etc", "yds", "pts", "mph", "ft"}   # QB, TD... are caught as all-caps
CAPS_OK = set()                     # all-caps words allowed in `text` (none yet: say letters spaced, "N F L")


def load_pron(path=ROOT / "pronunciation.json"):
    """pronunciation.json: word -> Kokoro phonemes (espeak-style IPA) to override, or "ok" (checked, espeak is right)."""
    raw = json.loads(Path(path).read_text())
    words = {w: v for w, v in raw.items() if not w.startswith("_")}
    return words, set(raw.get("_unsure", []))


def load_common(path=ROOT / "words.txt"):
    """Common English words: allowed capitalized at the start of a sentence without a pronunciation entry."""
    return {w.strip().lower() for w in Path(path).read_text().split() if w.strip() and not w.startswith("#")}


PRON, UNSURE = load_pron()
OVERRIDES = {w: v for w, v in PRON.items() if v != "ok"}
COMMON = load_common()

# ---- numbers: what a digit token should be written as (used in error messages; also folded in from spoken-years) ----
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
NUMBER_WORDS = "|".join(ONES + TENS[2:] + ["hundred", "thousand", "a half"])   # "fourth and twenty five" is a number, not two actions
ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth", "twelve": "twelfth"}


def cardinal(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + cardinal(n % 100))
    if n < 1_000_000:
        return cardinal(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + cardinal(n % 1000))
    return cardinal(n // 1_000_000) + " million" + ("" if n % 1_000_000 == 0 else " " + cardinal(n % 1_000_000))


def year(y):
    """Years the way a broadcaster says them: 1978 -> nineteen seventy eight, 2005 -> two thousand five, 2016 -> twenty sixteen."""
    hi, lo = divmod(y, 100)
    if 2000 <= y <= 2009:
        return "two thousand" + ("" if lo == 0 else " " + ONES[lo])
    return cardinal(hi) + (" hundred" if lo == 0 else " oh " + ONES[lo] if lo < 10 else " " + cardinal(lo))


def ordinal(n):
    w = cardinal(n).split(); last = w[-1]
    w[-1] = ORD.get(last) or (last[:-1] + "ieth" if last.endswith("y") else last + "th")
    return " ".join(w)


def say(tok):
    """Suggest the spoken form of a token with digits or symbols, e.g. '1978' -> 'nineteen seventy eight'."""
    t = tok.strip(".,?!:;\"'()")
    if re.fullmatch(r"(19|20)\d\d", t):
        return year(int(t))
    if re.fullmatch(r"\d{1,3}(,\d{3})+|\d+", t):
        return cardinal(int(t.replace(",", "")))
    m = re.fullmatch(r"(\d+)(st|nd|rd|th)", t)
    if m:
        return ordinal(int(m.group(1)))
    m = re.fullmatch(r"(\d+)-(\d+)", t)
    if m:
        return f"{cardinal(int(m.group(1)))} to {cardinal(int(m.group(2)))}"
    m = re.fullmatch(r"(\d+)(ers|s)('?)", t)
    if m:
        return "forty niners" if m.group(1) == "49" else cardinal(int(m.group(1))) + "s"
    m = re.fullmatch(r"(\d+(?:\.\d+)?)%", t)
    if m:
        return m.group(1).replace(".", " point ") + " percent"
    m = re.fullmatch(r"\$(\d[\d,]*)", t)
    if m:
        return cardinal(int(m.group(1).replace(",", ""))) + " dollars"
    return None


# ---- the checks ----
def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s]


def words_of(s):
    return re.findall(r"[A-Za-z][A-Za-z'’\-]*", s)


def base(w):
    """Strip a possessive: Buffalo's -> Buffalo, Bills' -> Bills."""
    return re.sub(r"(['’]s|['’])$", "", w)


def known(w):
    """Is this capitalized word listed (whole, or every hyphen part)?"""
    w = base(w)
    return w in PRON or all(p in PRON for p in w.split("-") if p)


def lint_text(text):
    """All speech-rule problems in one line's `text`, as strings. Empty list = clean."""
    out = []
    for tok in text.split():
        if SYMBOLS.search(tok):
            s = say(tok)
            out.append(f"digit or symbol in text: '{tok}'" + (f" (say \"{s}\"; digits go in cap)" if s else " (spell it out; digits go in cap)"))
        elif NON_ASCII.search(tok):
            out.append(f"non-ASCII letter in text: '{tok}' (spell it plainly; add the name to pronunciation.json)")
    for w in words_of(text):
        b = base(w)
        if len(b) >= 2 and b.isupper() and b not in CAPS_OK:
            out.append(f"all-caps '{b}' in text: Kokoro may read it as a word. Write the letters spaced (\"{' '.join(b)}\") or the full words")
        if b.lower() in ABBREVIATIONS:
            out.append(f"abbreviation '{b}' in text: write the full word")
    if text.count(":") > RULES["max_colons_per_line"]:
        out.append(f"{text.count(':')} colons in one line (max {RULES['max_colons_per_line']}: Kokoro pauses at each)")
    for s in sentences(text):
        ws = words_of(s)
        if len(ws) > RULES["max_sentence_words"]:
            out.append(f"{len(ws)} words in one sentence (max {RULES['max_sentence_words']}): \"{s}\"")
        if len(ws) >= RULES["and_min_words"] and re.search(r"\band\b(?!\s+(" + NUMBER_WORDS + r")\b)", s, re.I):
            out.append(f"'and' joins two things in one sentence; split it or use a comma: \"{s}\"")
        for i, w in enumerate(ws):
            b = base(w)
            if not b[:1].isupper() or len(b) == 1:
                continue   # lowercase, or a single letter (letters read reliably: "N F L", "I", "A")
            if known(b):
                continue
            if i == 0 and b.lower() in COMMON:
                continue   # an ordinary word that starts the sentence
            out.append(f"unlisted name '{b}': add it to engine/pronunciation.json (phonemes, or \"ok\" after checking its IPA)")
    return out


def unsure_names(text):
    return sorted({base(w) for w in words_of(text) if base(w) in UNSURE})


def estimate_s(lines, speed=1.0, lead=0.15, gap=0.28, tail=0.6):
    """Rough narration length (s) from letter count; good to about 5% on calibrated scripts."""
    letters = sum(len(re.findall(r"[A-Za-z]", l["text"])) for l in lines)
    return lead + letters / RULES["letters_per_s"] / speed + gap * (len(lines) - 1) + tail


def lint_script(S):
    """Every speech-rule problem in a script: [(line number or 0, message)]."""
    out = [(i, m) for i, l in enumerate(S.get("lines", []), 1) for m in lint_text(l["text"])]
    est = estimate_s(S.get("lines", []), RULES["max_speed"])
    T = float(S.get("target_s", 60.0))
    if est > T - RULES["fit_margin_s"]:
        out.append((0, f"narration won't fit {T:.0f} s at speed {RULES['max_speed']} (estimated {est:.1f} s). Cut words"))
    return out


# ---- pronunciation lookup for tts.py: override phonemes for listed words ----
OVR_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(sorted(map(re.escape, OVERRIDES), key=len, reverse=True)) + r")(['’]s)?(?![A-Za-z])") if OVERRIDES else None


def possessive(ph):
    """Phonemes for "'s" after a word: iz after s/z/sh sounds, s after voiceless consonants, z otherwise."""
    last = ph.rstrip("ˈˌː")[-1:]
    return "ɪz" if last in "szʃʒ" or ph.endswith("tʃ") or ph.endswith("dʒ") else "s" if last in "ptkfθ" else "z"


def split_overrides(text):
    """Split text into [(is_phonemes, chunk)] so tts.py phonemizes plain chunks and drops in listed overrides."""
    if not OVR_RE:
        return [(False, text)]
    out, i = [], 0
    for m in OVR_RE.finditer(text):
        if text[i:m.start()].strip():
            out.append((False, text[i:m.start()]))
        ph = OVERRIDES[m.group(1)]
        out.append((True, ph + (possessive(ph) if m.group(2) else ""))); i = m.end()
    if text[i:].strip():
        out.append((False, text[i:]))
    return out


def phonemize(text, plain):
    """Phonemes for a whole line: plain(chunk) for ordinary text, dictionary overrides spliced in."""
    out = [chunk if is_ph else plain(chunk) for is_ph, chunk in split_overrides(text)]
    return re.sub(r"\s+([,.!?;:])", r"\1", " ".join(o.strip() for o in out))
