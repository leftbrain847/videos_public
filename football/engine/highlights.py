"""Bottom half: a 60 s Disk Football highlight reel from the shared capture pool.

python3 highlights.py <video_dir> [--pool ../gameplay] [--index N]
Writes <video_dir>/build/bottom.mp4 (1080x960, silent). Deterministic per --index, so every video gets a different reel.
"""
import argparse, json, random, subprocess, tempfile

import cv2
import numpy as np
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
    # tracking camera: follow the disks and zoom in, so they read on a phone
    "track": {
        "on": True,
        "min_h": 560, "max_h": 860,    # crop window height in capture px (width = h * 9/8); 640 = 1.5x zoom, 860 ~ 1.1x
        "margin": 1.25, "pad_px": 180, # window height >= the action's spread * margin + pad
        "core": [20, 80],              # frame the middle of the action: these percentiles of disk positions, not stragglers
        "smooth": 0.12,                # per-frame easing of center and size (lower = calmer camera)
        "bright": 110, "min_area": 30, # disk detection: brightness threshold, smallest blob
        "field": [110, 200, 970, 1820],# x0, y0, x1, y1: search area (skips the HUD and sidelines)
    },
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


def tracked(p, out):
    """One play through a smoothed camera that keeps every disk in frame, as close as it can."""
    T = REEL["track"]; cap = cv2.VideoCapture(p["clip"]); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_MSEC, p["start"] * 1000)
    x0, y0, x1, y1 = T["field"]; cx = cy = hh = None
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1080x960", "-r", str(fps), "-i", "-",
                           "-vf", f"fps={REEL['fps']}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)], stdin=subprocess.PIPE)
    for _ in range(int((p["end"] - p["start"]) * fps)):
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
        n, _, st, _ = cv2.connectedComponentsWithStats((g > T["bright"]).astype(np.uint8))
        b = [s for s in st[1:] if s[4] >= T["min_area"]]
        if b:
            xs = np.array([s[0] + s[2] / 2 for s in b]) + x0; ys = np.array([s[1] + s[3] / 2 for s in b]) + y0
            lo, hi = T["core"]
            bx0, bx1 = np.percentile(xs, lo), np.percentile(xs, hi)
            by0, by1 = np.percentile(ys, lo), np.percentile(ys, hi)
            tcx, tcy = (bx0 + bx1) / 2, (by0 + by1) / 2
            th = max((by1 - by0) * T["margin"] + T["pad_px"], (bx1 - bx0) * T["margin"] * 8 / 9 + T["pad_px"])
            th = min(max(th, T["min_h"]), T["max_h"])
            if cx is None:
                cx, cy, hh = tcx, tcy, th
            k = T["smooth"]; cx += (tcx - cx) * k; cy += (tcy - cy) * k; hh += (th - hh) * k
        if cx is None:
            cx, cy, hh = 540, 960, T["max_h"]
        h = int(hh); w = min(int(h * 9 / 8), 1080); h = int(w * 8 / 9)
        X = int(min(max(cx - w / 2, 0), 1080 - w)); Y = int(min(max(cy - h / 2, 0), 1920 - h))
        ff.stdin.write(cv2.resize(fr[Y:Y + h, X:X + w], (1080, 960), interpolation=cv2.INTER_AREA).tobytes())
    ff.stdin.close(); ff.wait(); cap.release()


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
            if REEL["track"]["on"]:
                tracked(p, f)
            else:
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
