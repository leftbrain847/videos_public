"""Bottom half: a 60 s Disk Football highlight reel from the shared capture pool.

python3 highlights.py <video_dir> [--pool ../gameplay] [--index N]
Writes <video_dir>/build/bottom.mp4 (1080x960, silent). Deterministic per --index, so every video gets a different reel.
"""
import argparse, json, random, subprocess, tempfile
from pathlib import Path

REEL = {
    "seconds": 60.0,
    "crop": [1080, 1200, 0, 420],      # w, h, x, y of the 1080x1920 capture to keep: the band where plays happen, disks as large as possible
    "pad_color": "0x1b1a17",           # the field's own dark tone fills the sides
    "pre_snap_s": 0.5,                 # start this long before the snap
    "post_down_s": 1.1,                # hold this long after the ball is down (see the result)
    "min_yards": 15,                   # non-touchdown plays shorter than this never make the reel
    "td_bonus": 1000,                  # touchdowns always rank first
    "lateral_bonus": 15,               # per lateral, only when the play gained real yards...
    "lateral_min_yards": 20,           # ...this many or more (no pointless laterals)
    "top_k": 40,                       # draw each reel from the best K plays
    "fps": 24,
}


def plays(pool):
    out = []
    for ev in sorted(Path(pool).glob("**/events_s*.json")):
        clip = ev.with_name(ev.name.replace("events_", "clip_").replace(".json", ".mp4"))
        if not clip.exists():
            continue
        E = json.loads(ev.read_text())
        snaps = {e["play"]: e["t"] for e in E if e["type"] == "snap"}
        nxt = sorted(snaps.values())
        for d in (e for e in E if e["type"] == "down"):
            if d["play"] not in snaps:
                continue
            td, yds, lat = bool(d.get("td")), float(d.get("yards") or 0), int(d.get("laterals") or 0)
            if not td and yds < REEL["min_yards"]:
                continue
            if lat and not td and yds < REEL["lateral_min_yards"]:   # no pointless laterals (J)
                continue
            score = (REEL["td_bonus"] if td else 0) + yds + (lat * REEL["lateral_bonus"] if yds >= REEL["lateral_min_yards"] else 0)
            start = max(0, snaps[d["play"]] - REEL["pre_snap_s"])
            end = d["t"] + REEL["post_down_s"]
            later = [t for t in nxt if t > snaps[d["play"]]]
            if later:
                end = min(end, later[0] - 0.2)
            out.append({"clip": str(clip), "start": round(start, 3), "end": round(end, 3), "score": round(score, 1), "td": td, "yards": round(yds), "laterals": lat})
    return sorted(out, key=lambda p: -p["score"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video_dir"); ap.add_argument("--pool", default=str(Path(__file__).parent.parent / "gameplay")); ap.add_argument("--index", type=int, default=0)
    a = ap.parse_args()
    P = plays(a.pool)
    if not P:
        raise SystemExit(f"no plays in {a.pool}")
    top = P[: REEL["top_k"]]
    rng = random.Random(a.index)
    tds = [p for p in top if p["td"]]
    first = tds[a.index % len(tds)] if tds else top[0]
    rest = [p for p in top if p is not first]; rng.shuffle(rest)
    reel, total = [first], first["end"] - first["start"]
    for p in rest + P[REEL["top_k"]:]:
        if total >= REEL["seconds"]:
            break
        reel.append(p); total += p["end"] - p["start"]
    w, h, x, y = REEL["crop"]
    b = Path(a.video_dir) / "build"; b.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        parts = []
        for i, p in enumerate(reel):
            f = Path(td) / f"p{i:02d}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(p["start"]), "-to", str(p["end"]), "-i", p["clip"],
                            "-vf", f"crop={w}:{h}:{x}:{y},scale=-2:960,pad=1080:960:(ow-iw)/2:0:color={REEL['pad_color']},fps={REEL['fps']}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(f)], check=True)
            parts.append(f)
        lst = Path(td) / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-t", str(REEL["seconds"]),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(b / "bottom.mp4")], check=True)
    (b / "reel.json").write_text(json.dumps(reel, indent=1))
    print(f"reel: {len(reel)} plays, {sum(p['td'] for p in reel)} TDs, first: {first['yards']} yds td={first['td']}")


if __name__ == "__main__":
    main()
