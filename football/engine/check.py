"""Validate a video.json against the football shorts guidelines before spending time on narration and renders.

python3 check.py <video_dir> [...]      exit 1 if any video fails
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402  speech rules (GUIDELINES.md, "Writing for the voice")

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
    "actions": {"idle", "talk", "point", "cheer", "facepalm", "shrug", "throw", "hold", "cross", "slump", "clap", "wave", "run", "walk", "catch", "kick", "celebrate"},
    "narrator": "capy",
    # Speech rules live in voice.py. A script marked "voice": "v2" must pass all of them (strict); older scripts get a
    # one-line count until they're rewritten. strict=True here would hold every script to them.
    "voice": {"strict": False, "mark": "v2"},
    # J, 2026-11-20 UAT: feature Capy more. In v2 scripts she is the subject of at least this many shots (shot on/with
    # capy), including the first and last lines. A J-approved video is marked "locked" and keeps its approved cut.
    "capy_min_shots": 5,
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
        if l.get("speaker") and l["speaker"] != RULES["narrator"]:
            errs.append(f"{tag}: speaker must be capy (every line is her voice; others don't lip-sync)")
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


PLAY = {"z": (-10.0, 6.0), "min_gap": 1.5, "max_speed": 12.0, "samples": 60,
        "contact_s": 0.2, "sync_tol_s": 0.1}   # kit.js MOTION.contact; gestures within 0.1 s (about 2 frames) of the ball


def along(pts, u):
    """Same Catmull-Rom path as page.html along()."""
    if u <= pts[0][0]:
        return pts[0][1:]
    if u >= pts[-1][0]:
        return pts[-1][1:]
    i = 0
    while i < len(pts) - 2 and u > pts[i + 1][0]:
        i += 1
    p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
    f = (u - p1[0]) / max(1e-6, p2[0] - p1[0])
    cr = lambda a, b, c, d: 0.5 * (2 * b + (-a + c) * f + (2 * a - 5 * b + 4 * c - d) * f * f + (-a + 3 * b - 3 * c + d) * f ** 3)
    return [cr(p0[k], p1[k], p2[k], p3[k]) for k in range(1, len(p1))]


def play_errors(S, timing=None):
    """Field geometry of every `play`: z inside the action band, 1.5+ units between people, runs at 12 u/s or less
    (speed needs build/timing.json for line lengths)."""
    out, P = [], PLAY
    for i, l in enumerate(S.get("lines", []), 1):
        cast = {k: v["path"] for k, v in ((l.get("play") or {}).get("cast") or {}).items() if v.get("path")}
        if not cast:
            continue
        dur = (timing["lines"][i - 1]["end"] - timing["lines"][i - 1]["start"]) if timing else None
        flagged = set()
        if dur:   # gestures in sync with the ball: a kick/throw releases a flight, a catch ends one
            ball = (l.get("play") or {}).get("ball") or []
            flights = ball if ball and isinstance(ball[0][0], list) else ([ball] if ball else [])
            starts, ends = [f[0][0] * dur for f in flights], [f[-1][0] * dur for f in flights]
            for k, v in ((l.get("play") or {}).get("cast") or {}).items():
                for u, act in v.get("actions", []):
                    at = u * dur
                    if act in ("kick", "throw") and not any(abs(at + P["contact_s"] - s0) <= P["sync_tol_s"] for s0 in starts):
                        out.append(f"line {i}: {k}'s {act} at u {u} releases at {at + P['contact_s']:.2f} s; no ball flight starts then (flights start at {[round(x, 2) for x in starts]} s)")
                    if act == "catch" and not any(abs(at - e) <= P["sync_tol_s"] for e in ends):
                        out.append(f"line {i}: {k}'s catch at {at:.2f} s isn't when a ball arrives ({[round(x, 2) for x in ends]} s)")
        for n in range(P["samples"] + 1):
            u = n / P["samples"]; pos = {k: along(p, u) for k, p in cast.items()}
            for k, (x, z) in pos.items():
                if not P["z"][0] <= z <= P["z"][1] and ("z", k) not in flagged:
                    flagged.add(("z", k)); out.append(f"line {i}: {k} at z {z:.1f} at u {u:.2f} (keep z in {P['z']})")
                if dur and n:
                    x0, z0 = along(cast[k], u - 1 / P["samples"])
                    v = ((x - x0) ** 2 + (z - z0) ** 2) ** 0.5 / (dur / P["samples"])
                    if v > P["max_speed"] + 0.05 and ("v", k) not in flagged:
                        flagged.add(("v", k)); out.append(f"line {i}: {k} runs {v:.1f} u/s at u {u:.2f} (max {P['max_speed']})")
            ks = sorted(pos)
            for a in range(len(ks)):
                for b in range(a + 1, len(ks)):
                    (xa, za), (xb, zb) = pos[ks[a]], pos[ks[b]]
                    if ((xa - xb) ** 2 + (za - zb) ** 2) ** 0.5 < P["min_gap"] and ("gap", ks[a], ks[b]) not in flagged:
                        flagged.add(("gap", ks[a], ks[b])); out.append(f"line {i}: {ks[a]} and {ks[b]} closer than {P['min_gap']} at u {u:.2f}")
    return out


def strict(S):
    return RULES["voice"]["strict"] or S.get("voice") == RULES["voice"]["mark"]


def voice_errors(vd):
    """Speech-rule problems: failures for a v2 script, a count for the rest."""
    S = json.loads((Path(vd) / "video.json").read_text())
    out = [(f"line {i}: " if i else "") + m for i, m in voice.lint_script(S)]
    tj = Path(vd) / "build" / "timing.json"
    if tj.exists():
        sp = json.loads(tj.read_text()).get("speed", 1.0)
        if sp > voice.RULES["max_speed"]:
            out.append(f"last narration needed speed {sp} (max {voice.RULES['max_speed']}). Cut words")
    out += play_errors(S, json.loads(tj.read_text()) if tj.exists() else None)
    if not S.get("locked"):
        n = sum(1 for l in S.get("lines", []) if "capy" in ((l.get("shot") or {}).get("on"), (l.get("shot") or {}).get("with")))
        if n < RULES["capy_min_shots"]:
            out.append(f"Capy is the subject of {n} shots (want {RULES['capy_min_shots']}+: she opens, guides and closes)")
    unsure = sorted({n for l in S.get("lines", []) for n in voice.unsure_names(l["text"])})
    return S, out, unsure


def main():
    import test_voice
    test_voice.run()   # the checker checks itself first: a broken rule must never pass scripts silently
    bad = 0
    for vd in sys.argv[1:]:
        words, errs = check(vd)
        S, verrs, unsure = voice_errors(vd)
        if strict(S):
            errs += ["voice: " + e for e in verrs]
        print(("OK  " if not errs else "FAIL") + f" {vd} ({words} words{', voice v2' if strict(S) else ''})")
        for e in errs:
            print("   -", e)
        if not strict(S) and verrs:
            print(f"   ~ voice: {len(verrs)} speech-rule issues (fail once the script is marked \"voice\": \"v2\")")
        if strict(S) and unsure:
            print("   ? listen for:", ", ".join(unsure), "(pronunciation not confirmed; see pronunciation.json _unsure)")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
