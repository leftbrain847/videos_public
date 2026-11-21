"""Render workflow plan: validate the requested video ids and emit the job matrix.

VIDEOS="s4_01_music_city_miracle s1_01_tuck_rule" TAG=football-batch-1 python3 tools/render_plan.py
BATCH=football/batches/batch-1.json python3 tools/render_plan.py      (a push to main that adds a batch file)
-> matrix=[{"id": ..., "index": ...}], ids, release, replace, listen (GitHub output lines)

A batch file is {"release": "football-batch-1", "videos": [ids...]} with optional "replace" and "listen" booleans.
Ids come from a workflow input or a batch file, so they are checked against a strict pattern and the videos folder
before anything uses them. Each video's reel index is its position among all videos, so every video gets a
different reel. Up to MAX videos per run; the workflow renders at most 20 at a time (max-parallel).
"""
import json, os, re, sys
from pathlib import Path

MAX = 30
TAG = re.compile(r"^football-batch-[0-9a-z-]{1,30}$")
BATCH = re.compile(r"^football/batches/[a-z0-9-]{1,40}\.json$")
ID = re.compile(r"^s[1-4]_\d\d_[a-z0-9_]{1,60}$")


def plan(raw, videos=Path(__file__).resolve().parent.parent / "football" / "videos"):
    ids = raw.split()
    if not ids:
        sys.exit("no video ids given")
    if len(ids) > MAX:
        sys.exit(f"{len(ids)} videos requested; max {MAX} per run")
    every = sorted(p.name for p in videos.iterdir() if (p / "video.json").exists())
    bad = [i for i in ids if not ID.fullmatch(i) or i not in every]
    if bad:
        sys.exit(f"unknown video ids: {bad}")
    return [{"id": i, "index": every.index(i)} for i in dict.fromkeys(ids)]


def settings(env=os.environ, root=Path(__file__).resolve().parent.parent):
    """(video ids, release tag, replace, listen) from a batch file (BATCH) or the workflow inputs."""
    if env.get("BATCH"):
        if not BATCH.fullmatch(env["BATCH"]):
            sys.exit(f"bad batch file path: {env['BATCH']!r}")
        b = json.loads((root / env["BATCH"]).read_text())
        if not isinstance(b.get("videos"), list) or not all(isinstance(v, str) for v in b["videos"]):
            sys.exit("batch file needs a list of video ids in 'videos'")
        vids, tag = " ".join(b["videos"]), b.get("release", "")
        replace, listen = b.get("replace", False) is True, b.get("listen", True) is not False
        if not tag:
            sys.exit("batch file needs a 'release' tag")
    else:
        vids, tag = env.get("VIDEOS", ""), env.get("TAG", "")
        replace, listen = env.get("REPLACE") == "true", env.get("LISTEN", "true") != "false"
    if tag and not TAG.fullmatch(tag):
        sys.exit(f"bad release tag: {tag!r}")
    return vids, tag, replace, listen


if __name__ == "__main__":
    vids, tag, replace, listen = settings()
    m = plan(vids)
    print("matrix=" + json.dumps(m)); print("ids=" + " ".join(v["id"] for v in m))
    print(f"release={tag}"); print(f"replace={str(replace).lower()}"); print(f"listen={str(listen).lower()}")
