"""Release gate per video: delete the files of any video whose fact check did not pass, so only checked videos ship.

python3 tools/release_filter.py <facts dir> <files dir>
A video passes when facts/<id>.json exists and every claim in it passed (two sources). Missing or unreadable facts = fail.
Files are named <id>.mp4, <id>.master.mp4, <id>.jpg, <id>.review.jpg. Prints what was kept and what was held back.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import videos  # noqa: E402
ID = re.compile(r"^(" + videos.ID_PATTERN + r")(\.master|\.review)?\.(mp4|jpg)$")


def passed(facts, vid):
    try:
        res = json.loads((facts / f"{vid}.json").read_text())
        return bool(res) and all(r.get("pass") is True for r in res)
    except (OSError, ValueError):
        return False


def main(facts, files):
    facts, files = Path(facts), Path(files)
    kept, held = set(), set()
    for f in sorted(files.iterdir()) if files.exists() else []:
        m = ID.match(f.name)
        vid = m.group(1) if m else None
        if vid and passed(facts, vid):
            kept.add(vid)
        else:
            held.add(vid or f.name); f.unlink()
    print("released: " + (" ".join(sorted(kept)) or "none"))
    print("held back (facts not passed): " + (" ".join(sorted(held)) or "none"))


if __name__ == "__main__":
    main(*sys.argv[1:3])
