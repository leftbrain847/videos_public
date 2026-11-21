"""Offline tests for the render queue plan and the per-video release gate. python3 tools/test_tools.py"""
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_plan, release_filter


def expect_exit(fn):
    try:
        fn()
    except SystemExit:
        return
    raise AssertionError("expected a refusal")


def test_queue():
    d = Path(tempfile.mkdtemp()); q = d / "q.json"
    q.write_text(json.dumps({"mode": "render", "release": "football-batch-1", "videos": ["s4_01_music_city_miracle"]}))
    v, tag, listen, rep, mode = render_plan.settings({"EVENT": "push"}, q)
    assert (v, tag, listen, rep, mode) == ("s4_01_music_city_miracle", "football-batch-1", True, False, "render")
    for bad in ({"release": "x; rm -rf /", "videos": []}, {"mode": "deploy", "videos": []}, {"videos": "s4_01"}, {"evil": 1, "videos": []}):
        q.write_text(json.dumps(bad)); expect_exit(lambda: render_plan.settings({"EVENT": "push"}, q))
    v, tag, *_ = render_plan.settings({"EVENT": "workflow_dispatch", "VIDEOS": "a b", "TAG": ""}, q)
    assert v == "a b" and tag == ""
    expect_exit(lambda: render_plan.plan("s4_01_music_city_miracle $(id)"))
    assert render_plan.plan("s4_01_music_city_miracle")[0]["id"] == "s4_01_music_city_miracle"


def test_release_filter():
    d = Path(tempfile.mkdtemp()); facts, files = d / "facts", d / "files"; facts.mkdir(); files.mkdir()
    (facts / "s4_01_a.json").write_text(json.dumps([{"pass": True}, {"pass": True}]))
    (facts / "s4_02_b.json").write_text(json.dumps([{"pass": True}, {"pass": False}]))
    for vid in ("s4_01_a", "s4_02_b", "s4_03_c"):
        for suf in (".mp4", ".master.mp4", ".jpg", ".review.jpg"):
            (files / (vid + suf)).write_text("x")
    (files / "stray.txt").write_text("x")
    release_filter.main(facts, files)
    assert sorted(f.name for f in files.iterdir()) == ["s4_01_a.jpg", "s4_01_a.master.mp4", "s4_01_a.mp4", "s4_01_a.review.jpg"]


if __name__ == "__main__":
    test_queue(); test_release_filter(); print("tools tests passed")
