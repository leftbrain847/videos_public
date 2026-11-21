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
    for bad in ({"release": "x; rm -rf /", "videos": []}, {"mode": "deploy", "videos": []}, {"videos": "s4_01"}, {"evil": 1, "videos": []}, {"replace": "false", "videos": []}):
        q.write_text(json.dumps(bad)); expect_exit(lambda: render_plan.settings({"EVENT": "push"}, q))
    v, tag, *_ = render_plan.settings({"EVENT": "workflow_dispatch", "VIDEOS": "a b", "TAG": ""}, q)
    assert v == "a b" and tag == ""
    expect_exit(lambda: render_plan.plan("s4_01_music_city_miracle $(id)"))
    assert render_plan.plan("s4_01_music_city_miracle")[0] == {"id": "s4_01_music_city_miracle", "index": render_plan.videos.all_ids().index("s4_01_music_city_miracle"), "dir": "videos/s4_01_music_city_miracle"}
    import videos
    assert videos.channel("myth_01_medusa") == "stories" and videos.channel("s1_01_tuck_rule") == "football" and videos.channel("myth_1_x") is None
    assert videos.video_dir("space_03_voyager").parts[-3:] == ("stories", "videos", "space_03_voyager")
    assert videos.tag_ok("stories-myth-1") and videos.tag_ok("football-batch-2") and not videos.tag_ok("stories-cats-1") and not videos.tag_ok("stories-myth-1;x")
    q.write_text(json.dumps({"release": "stories-heist-2", "videos": []}))
    assert render_plan.settings({"EVENT": "push"}, q)[1] == "stories-heist-2"


def test_release_filter():
    d = Path(tempfile.mkdtemp()); facts, files = d / "facts", d / "files"; facts.mkdir(); files.mkdir()
    (facts / "s4_01_a.json").write_text(json.dumps([{"pass": True}, {"pass": True}]))
    (facts / "s4_02_b.json").write_text(json.dumps([{"pass": True}, {"pass": False}]))
    (facts / "myth_01_x.json").write_text(json.dumps([{"pass": True}]))
    for vid in ("s4_01_a", "s4_02_b", "s4_03_c", "myth_01_x"):
        for suf in (".mp4", ".master.mp4", ".jpg", ".review.jpg"):
            (files / (vid + suf)).write_text("x")
    (files / "stray.txt").write_text("x")
    release_filter.main(facts, files)
    assert sorted(f.name for f in files.iterdir()) == ["myth_01_x.jpg", "myth_01_x.master.mp4", "myth_01_x.mp4", "myth_01_x.review.jpg",
                                                        "s4_01_a.jpg", "s4_01_a.master.mp4", "s4_01_a.mp4", "s4_01_a.review.jpg"]


if __name__ == "__main__":
    test_queue(); test_release_filter(); print("tools tests passed")
