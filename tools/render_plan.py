"""Render workflow plan: validate the requested video ids and emit the job matrix plus run settings.

VIDEOS="s4_01_music_city_miracle s1_01_tuck_rule" python3 tools/render_plan.py   -> matrix=[{"id": ..., "index": ...}]
On a push (EVENT=push) the request comes from football/render_queue.json instead of the dispatch inputs:
{"mode": "render" | "facts", "release": "football-batch-1" | "", "listen": true, "replace": false, "videos": [ids]}
Ids come from a workflow_dispatch input, so they are checked against a strict pattern and the videos folder before
anything uses them. Each video's reel index is its position among all videos, so every video gets a different reel.
"""
import json, os, re, sys
from pathlib import Path

MAX = 20
sys.path.insert(0, str(Path(__file__).resolve().parent))
import videos  # noqa: E402  id, folder and tag rules for every channel
QUEUE = Path(__file__).resolve().parent.parent / "football" / "render_queue.json"


def settings(env=os.environ, queue=QUEUE):
    """(videos, release, listen, replace, mode) from the queue file on push, else from the dispatch inputs."""
    if env.get("EVENT") == "push":
        q = json.loads(queue.read_text())
        unknown = set(q) - {"mode", "release", "listen", "replace", "videos", "_note"}
        if unknown:
            sys.exit(f"unknown queue keys: {sorted(unknown)}")
        if not all(isinstance(q.get(k, False), bool) for k in ("listen", "replace")):
            sys.exit("listen/replace must be true or false")
        vids = q.get("videos", [])
        if not isinstance(vids, list) or not all(isinstance(v, str) for v in vids):
            sys.exit("queue videos must be a list of ids")
        out = (" ".join(vids), q.get("release", ""), bool(q.get("listen", True)), bool(q.get("replace", False)), q.get("mode", "render"))
    else:
        out = (env.get("VIDEOS", ""), env.get("TAG", ""), env.get("LISTEN", "true") == "true", env.get("REPLACE", "false") == "true", "render")
    vids, tag, listen, replace, mode = out
    if tag and not videos.tag_ok(tag):
        sys.exit("bad release tag")
    if mode not in ("render", "facts"):
        sys.exit("mode must be render or facts")
    return vids, tag, listen, replace, mode


def plan(raw):
    ids = raw.split()
    if not ids:
        sys.exit("no video ids given")
    if len(ids) > MAX:
        sys.exit(f"{len(ids)} videos requested; max {MAX} per run")
    every = videos.all_ids()
    bad = [i for i in ids if not videos.channel(i) or i not in every]
    if bad:
        sys.exit(f"unknown video ids: {bad}")
    # dir: the video folder relative to football/ (where engine/make.sh runs), e.g. videos/<id> or ../stories/videos/<id>
    return [{"id": i, "index": every.index(i), "dir": "videos/" + i if videos.channel(i) == "football" else "../stories/videos/" + i}
            for i in dict.fromkeys(ids)]


if __name__ == "__main__":
    vids, tag, listen, replace, mode = settings()
    m = plan(vids)
    print("matrix=" + json.dumps(m)); print("ids=" + " ".join(v["id"] for v in m))
    print(f"release={tag}"); print(f"listen={str(listen).lower()}"); print(f"replace={str(replace).lower()}"); print(f"mode={mode}")
