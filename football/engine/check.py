"""Validate a video.json against the football shorts guidelines before spending time on narration and renders.

python3 check.py <video_dir> [...]      exit 1 if any video fails
"""
import json, re, sys
from pathlib import Path

RULES = {
    "lines": (10, 18),
    "words": (135, 172),            # spoken words; ~2.6 words/s fits 60 s with breathing room
    "min_sources": 2,
    "min_distinct_shots": 5,
    "max_same_shot_run": 2,
    "keys_per_line": (1, 2),
    "sets": {"locker", "field", "press", "office", "living", "tunnel"},
    "shots": {"wide", "medium", "close", "low", "high", "two", "ots", "follow", "follow_high"},
    "moods": {"neutral", "angry", "worried", "shocked", "happy", "sad", "smug", "confused"},
    "actions": {"idle", "talk", "point", "cheer", "facepalm", "shrug", "throw", "hold", "cross", "slump", "clap", "wave", "run", "catch", "kick", "celebrate"},
    "narrator": "capy",
}


def norm(w):
    return re.sub(r"[^A-Z0-9%$]", "", w.upper())


def check(vd):
    errs = []
    S = json.loads((Path(vd) / "video.json").read_text())
    L, cast = S.get("lines", []), S.get("cast", {})
    if not (RULES["lines"][0] <= len(L) <= RULES["lines"][1]):
        errs.append(f"{len(L)} lines (want {RULES['lines']})")
    words = sum(len(l["text"].split()) for l in L)
    if not (RULES["words"][0] <= words <= RULES["words"][1]):
        errs.append(f"{words} spoken words (want {RULES['words']})")
    if len([s for s in S.get("sources", []) if s.get("url", "").startswith("http")]) < RULES["min_sources"]:
        errs.append("needs at least 2 sources with urls")
    if RULES["narrator"] not in cast or cast[RULES["narrator"]].get("kind") != "capy":
        errs.append("cast must include capy (kind: capy)")
    if S.get("set") not in RULES["sets"]:
        errs.append(f"unknown set {S.get('set')}")
    shots, run = [], 1
    for i, l in enumerate(L):
        tag = f"line {i + 1}"
        if l.get("set") and l["set"] not in RULES["sets"]:
            errs.append(f"{tag}: unknown set {l['set']}")
        sh = l.get("shot")
        if sh:
            if sh.get("type") not in RULES["shots"]:
                errs.append(f"{tag}: unknown shot {sh.get('type')}")
            for k in ("on", "with", "from"):
                if sh.get(k) and sh[k] not in cast and not (k == "on" and sh[k] == "ball"):
                    errs.append(f"{tag}: shot.{k} '{sh[k]}' not in cast")
            shots.append(json.dumps(sh, sort_keys=True))
        for cid, a in (l.get("act") or {}).items():
            if cid not in cast:
                errs.append(f"{tag}: act for unknown cast '{cid}'")
            if a.get("mood") and a["mood"] not in RULES["moods"]:
                errs.append(f"{tag}: mood {a['mood']}")
            if a.get("action") and a["action"] not in RULES["actions"]:
                errs.append(f"{tag}: action {a['action']}")
        for cid in (l.get("place") or {}):
            if cid not in cast:
                errs.append(f"{tag}: place for unknown cast '{cid}'")
        if l.get("speaker") and l["speaker"] not in cast:
            errs.append(f"{tag}: speaker '{l['speaker']}' not in cast")
        keys = l.get("key", [])
        if not (RULES["keys_per_line"][0] <= len(keys) <= RULES["keys_per_line"][1]):
            errs.append(f"{tag}: {len(keys)} key words (want 1-2)")
        cap = {norm(w) for w in l.get("cap", l["text"]).split()}
        for k in keys:
            if norm(k) not in cap:
                errs.append(f"{tag}: key '{k}' not in its caption")
    types = [json.loads(s).get("type") for s in shots]
    for i in range(len(types)):
        if i >= RULES["max_same_shot_run"] and len(set(types[i - RULES["max_same_shot_run"]: i + 1])) == 1:
            errs.append(f"shot type '{types[i]}' {RULES['max_same_shot_run'] + 1} times in a row (line {i + 1})")
    if len(set(shots)) < RULES["min_distinct_shots"]:
        errs.append(f"only {len(set(shots))} distinct shots (want {RULES['min_distinct_shots']}+)")
    # capy opens and closes
    for idx, name in ((0, "first"), (len(L) - 1, "last")):
        l = L[idx] if L else {}
        if l.get("speaker") != "capy":
            errs.append(f"{name} line: capy must be the speaker")
    if L and not L[-1]["text"].rstrip().endswith("?") and "?" not in L[-1]["text"]:
        errs.append("last line must ask the viewer a question (comment prompt)")
    return words, errs


def main():
    bad = 0
    for vd in sys.argv[1:]:
        words, errs = check(vd)
        print(("OK  " if not errs else "FAIL") + f" {vd} ({words} words)")
        for e in errs:
            print("   -", e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
