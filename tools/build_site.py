"""Build site/<channel>/videos.json for a channel gallery from its scripts and the web copies in site/<channel>/media.

python3 tools/build_site.py [channel]      (default: football; run from the repo root; the Pages workflow runs it too)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETS = {
    "s1": "Wait, that's the rule?",
    "s2": "This season",
    "s3": "The strange years",
    "s4": "Endings nobody forgets",
}


def main():
    ch = sys.argv[1] if len(sys.argv) > 1 else "football"
    site = ROOT / "site" / ch
    items = []
    for vj in sorted((ROOT / ch / "videos").glob("*/video.json")):
        v = json.loads(vj.read_text())
        vid = v.get("id", vj.parent.name)
        if not re.fullmatch(r"s\d_\d+_[a-z0-9_]+", vid) or vid != vj.parent.name:
            raise SystemExit(f"bad video id {vid!r} in {vj}")
        s = vid.split("_")[0]
        media = site / "media" / s / f"{vid}.mp4"
        if not media.exists():
            continue
        hook = v["lines"][0].get("cap", v["lines"][0]["text"]) if v.get("lines") else ""
        items.append({
            "id": vid, "set": s, "n": int(re.match(r"s\d_(\d+)", vid).group(1)),
            "title": v.get("title", vid), "hook": hook,
            "video": f"media/{s}/{vid}.mp4", "poster": f"posters/{s}/{vid}.jpg",
            "sources": [{"title": x.get("title", ""), "url": x["url"]} for x in v.get("sources", []) if x.get("url", "").startswith("https://")],
        })
    items.sort(key=lambda x: (x["set"], x["n"]))
    out = {"sets": SETS, "videos": items}
    (site / "videos.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"site/{ch}/videos.json: {len(items)} videos")


if __name__ == "__main__":
    main()
