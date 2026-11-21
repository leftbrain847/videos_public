"""Where a video id lives. One place for the id and release-tag rules every tool and workflow uses.

football shorts: football/videos/s<set>_<nn>_<slug>        release tags football-batch-<x>
story series:    stories/videos/<series>_<nn>_<slug>        release tags stories-<series>-<x>   (one series per tag, so
                 each series can be grabbed and posted as a group)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERIES = ("scary", "heist", "myth", "space", "mind")
CHANNELS = {
    "football": {"dir": ROOT / "football" / "videos", "id": re.compile(r"^s[1-4]_\d\d_[a-z0-9_]{1,60}$"),
                 "tag": re.compile(r"^football-batch-[0-9a-z-]{1,30}$")},
    "stories": {"dir": ROOT / "stories" / "videos", "id": re.compile(r"^(?:" + "|".join(SERIES) + r")_\d\d_[a-z0-9_]{1,60}$"),
                "tag": re.compile(r"^stories-(?:" + "|".join(SERIES) + r")-[0-9a-z-]{1,20}$")},
}
ID_PATTERN = r"(?:s[1-4]|" + "|".join(SERIES) + r")_\d\d_[a-z0-9_]{1,60}?"


def channel(vid):
    """The channel a video id belongs to, or None if the id matches no channel's pattern."""
    return next((c for c, C in CHANNELS.items() if C["id"].fullmatch(vid)), None)


def video_dir(vid):
    c = channel(vid)
    if not c:
        raise ValueError(f"not a video id: {vid!r}")
    return CHANNELS[c]["dir"] / vid


def tag_ok(tag):
    return any(C["tag"].fullmatch(tag) for C in CHANNELS.values())


def all_ids():
    return sorted(p.name for C in CHANNELS.values() if C["dir"].exists() for p in C["dir"].iterdir() if (p / "video.json").exists())
