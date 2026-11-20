"""Render workflow plan: validate the requested video ids and emit the job matrix.

VIDEOS="s4_01_music_city_miracle s1_01_tuck_rule" python3 tools/render_plan.py   -> matrix=[{"id": ..., "index": ...}]
Ids come from a workflow_dispatch input, so they are checked against a strict pattern and the videos folder before
anything uses them. Each video's reel index is its position among all videos, so every video gets a different reel.
"""
import json, os, re, sys
from pathlib import Path

MAX = 20
ID = re.compile(r"^s[1-4]_\d\d_[a-z0-9_]{1,60}$")


def plan(raw, videos=Path(__file__).resolve().parent.parent / "football" / "videos"):
    ids = raw.split()
    if not ids:
        sys.exit("no video ids given")
    if len(ids) > MAX:
        sys.exit(f"{len(ids)} videos requested; max {MAX} per run")
    every = sorted(p.name for p in videos.iterdir() if (p / "video.json").exists())
    bad = [i for i in ids if not ID.match(i) or i not in every]
    if bad:
        sys.exit(f"unknown video ids: {bad}")
    return [{"id": i, "index": every.index(i)} for i in dict.fromkeys(ids)]


if __name__ == "__main__":
    m = plan(os.environ.get("VIDEOS", ""))
    print("matrix=" + json.dumps(m)); print("ids=" + " ".join(v["id"] for v in m))
