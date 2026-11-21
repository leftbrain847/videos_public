"""Tests for the speech rules (voice.py) and the pronunciation dictionary. No dependencies.

python3 engine/test_voice.py      (also run by check.py before every check, so CI runs them on every PR)
pytest engine/test_voice.py       (works too)
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import voice  # noqa: E402

ROOT = Path(__file__).parent


def has(text, needle):
    return any(needle in m for m in voice.lint_text(text))


# rule 1: text is exactly what is spoken
def test_digits_fail_with_spoken_suggestion():
    assert has("You're in 1978.", "nineteen seventy eight")
    assert has("Final score 31-3.", "thirty one to three")
    assert has("Fourth and 25.", "twenty five")
    assert has("The 49ers win.", "forty niners")
    assert has("It's the 1st pick.", "first")


def test_symbols_and_caps_fail():
    for t in ("Ninety % of fans.", "Bills & Titans.", "Win/loss.", "The NFL said no.", "One TD."):
        assert voice.lint_text(t), t


def test_spaced_letters_and_words_pass():
    assert voice.lint_text("The N F L said no.") == []
    assert voice.lint_text("Nineteen seventy eight. Thirty one to three.") == []
    assert voice.lint_text("Fourth and twenty five.") == []    # "and" inside a number is fine


def test_and_rule():
    assert has("You turn and throw it.", "'and'")
    assert not has("Salt and pepper.", "'and'")          # 3 words: a pair, not two actions


def test_abbreviations_and_accents_fail():
    assert has("They played in St Louis.", "abbreviation")
    assert has("Bills vs Titans.", "abbreviation")
    assert has("At the famous Maracanã.", "non-ASCII")


def test_years():
    assert voice.say("1978") == "nineteen seventy eight"
    assert voice.say("2005") == "two thousand five"
    assert voice.say("2016") == "twenty sixteen"
    assert voice.say("1900") == "nineteen hundred"
    assert voice.say("1905") == "nineteen oh five"
    assert voice.say("2,000") == "two thousand"


# rule 2: sentence length, colons
def test_sentence_length():
    assert has("One two three four five six seven eight nine.", "9 words")
    assert not has("One two three four five six seven eight.", "words in one sentence")


def test_colons():
    assert has("Score: sixteen. Time: three.", "colons")
    assert not has("Final score: sixteen.", "colons")


# rule 3: names
def test_unlisted_names_fail_listed_pass():
    assert has("You meet Zxqwerty.", "unlisted name 'Zxqwerty'")
    assert not has("You meet Kevin Dyson.", "unlisted")
    assert not has("Buffalo's kicker.", "unlisted")          # possessive of a listed name
    assert not has("Laurent Duvernay-Tardif plays.", "unlisted")
    assert has("Then Zxqwerty runs.", "unlisted")             # a name mid-sentence
    assert has("Zxqwerty runs.", "unlisted")                  # a name that starts the sentence
    assert not has("Meanwhile, you wait.", "unlisted")        # an ordinary word that starts the sentence


def test_dictionary_covers_teams_and_cities():
    teams = "Bears Bengals Bills Broncos Browns Buccaneers Cardinals Chargers Chiefs Colts Commanders Cowboys Dolphins Eagles Falcons Niners Giants Jaguars Jets Lions Packers Panthers Patriots Raiders Rams Ravens Saints Seahawks Steelers Texans Titans Vikings".split()
    cities = "Arizona Atlanta Baltimore Buffalo Carolina Chicago Cincinnati Cleveland Dallas Denver Detroit Green Bay Houston Indianapolis Jacksonville Kansas City Las Vegas Los Angeles Miami Minnesota New England Orleans York Philadelphia Pittsburgh San Francisco Seattle Tampa Tennessee Washington".split()
    assert len(teams) == 32
    missing = [w for w in teams + cities if w not in voice.PRON]
    assert not missing, missing


def test_dictionary_entries_are_well_formed():
    raw = json.loads((ROOT / "pronunciation.json").read_text())
    for w, v in raw.items():
        if w.startswith("_"):
            continue
        assert isinstance(v, str) and v, w
        assert v == "ok" or not any(c.isdigit() for c in v), w     # phonemes, never digits
    assert set(raw["_unsure"]) <= set(voice.PRON)
    assert not ({w.lower() for w in voice.PRON} & voice.COMMON - {"covid"}), "a name is also listed as a common word"


# pronunciation lookups (what tts.py sends Kokoro)
def test_overrides_are_spliced_in():
    parts = voice.split_overrides("Larry Csonka runs.")
    assert (True, voice.OVERRIDES["Csonka"]) in parts
    assert parts[0] == (False, "Larry ")


def test_override_possessive():
    parts = voice.split_overrides("Csonka's hip.")
    assert parts[0] == (True, voice.OVERRIDES["Csonka"] + "z")
    assert voice.possessive("bˈɛɾɪs") == "ɪz"
    assert voice.possessive("kˈʊk") == "s"


def test_overrides_are_case_sensitive_whole_words():
    assert all(not p for p, _ in voice.split_overrides("the nike of it"))       # lowercase: not the brand
    assert all(not p for p, _ in voice.split_overrides("Tatumville"))           # inside a longer word


def test_phonemize_whole_line():
    fake = lambda chunk: chunk.strip().upper()   # stands in for espeak
    assert voice.phonemize("Larry Csonka runs.", fake) == "LARRY " + voice.OVERRIDES["Csonka"] + " RUNS."
    assert voice.phonemize("No names here.", fake) == "NO NAMES HERE."


def test_ok_entries_are_not_overridden():
    assert "Dyson" in voice.PRON and "Dyson" not in voice.OVERRIDES


# rule 4: fit
def test_fit_estimate():
    short = {"lines": [{"text": "Short line."}] * 12}
    long = {"lines": [{"text": "word " * 60}] * 16}
    assert not any("fit" in m for _, m in voice.lint_script(short))
    assert any("fit" in m for _, m in voice.lint_script(long))


def test_strict_is_per_script():
    import check
    assert check.strict({"voice": "v2"}) and not check.strict({})


def test_v2_script_with_a_year_fails_check():
    import check, tempfile
    with tempfile.TemporaryDirectory() as d:
        S = {"voice": "v2", "locked": True, "lines": [{"text": "You're in 1978. Kevin Dyson waits."}]}
        (Path(d) / "video.json").write_text(json.dumps(S))
        _, errs, _ = check.voice_errors(d)
        assert any("nineteen seventy eight" in e for e in errs), errs
        S["lines"][0]["text"] = "You're in nineteen seventy eight. Kevin Dyson waits."
        (Path(d) / "video.json").write_text(json.dumps(S))
        assert check.voice_errors(d)[1] == []


def test_play_geometry_rules():
    import check
    S = {"lines": [{"play": {"cast": {"a": {"path": [[0, 0, 0], [1, 30, 0]]}, "b": {"path": [[0, 1, 0], [1, 1, 8]]}}}}]}
    errs = check.play_errors(S, {"lines": [{"start": 0, "end": 2}]})
    assert any("b at z" in e for e in errs), errs              # walked toward the camera
    assert any("a runs" in e for e in errs), errs              # 30 units in 2 s
    assert any("closer than" in e for e in errs), errs         # start 1 unit apart
    ok = {"lines": [{"play": {"cast": {"a": {"path": [[0, 0, 0], [1, 10, 0]]}, "b": {"path": [[0, 0, -3], [1, 10, -3]]}}}}]}
    assert check.play_errors(ok, {"lines": [{"start": 0, "end": 2}]}) == []


def test_capy_must_be_featured():
    import check, tempfile
    with tempfile.TemporaryDirectory() as d:
        S = {"voice": "v2", "lines": [{"text": "Short line.", "shot": {"type": "two", "on": "capy"}}] * 4}
        (Path(d) / "video.json").write_text(json.dumps(S))
        assert any("Capy is the subject of 4" in e for e in check.voice_errors(d)[1])
        S["lines"] = S["lines"] * 2
        (Path(d) / "video.json").write_text(json.dumps(S))
        assert not any("Capy" in e for e in check.voice_errors(d)[1])


def test_listen_back_diff():
    import listen
    assert listen.diff("You're in nineteen seventy eight.", "You're in 1978.") == []      # digits spoken back
    assert listen.diff("Larry Csonka runs.", "Larry Sonka runs.") == [("csonka", "sonka")]
    assert listen.diff("Bills sixteen, Titans fifteen.", "Bills 16, Titans 15") == []


def test_render_plan_rejects_bad_ids():
    sys.path.insert(0, str(ROOT.parent.parent / "tools"))
    import render_plan
    m = render_plan.plan("s4_01_music_city_miracle")
    assert m[0]["id"] == "s4_01_music_city_miracle" and isinstance(m[0]["index"], int)
    for bad in ("../etc", "s1_01_x;rm", " ".join(["s4_01_music_city_miracle"] * 21)):
        try:
            render_plan.plan(bad); assert False, bad
        except SystemExit:
            pass


def test_fact_check_matching_and_snippets():
    sys.path.insert(0, str(ROOT.parent.parent / "tools"))
    import fact_check as f
    w = "The Titans won 22 16 when Kevin Dyson ran 75 yards down the sideline for a touchdown with three seconds left".split()
    assert f.find(w, ["Dyson", "75|seventy-five", "yard"])            # all terms close together
    assert f.find(w, ["Neal"]) is None                                 # missing term: no support
    assert f.find(w, ["Titans", "three seconds"], window=5) is None    # too far apart
    assert len(f.snippet(w, f.find(w, ["Dyson", "75"])).split()) <= 15  # never more than 15 words of a source
    assert f.find(w, ["22-16"]) and f.find(w, ["22–16"])                # scores match pages split at the dash
    assert f.find(w, ["three second"]) and f.find(w, ["Dyson", "sideline"])
    assert f.find(w, ["16-22"]) is None and f.find(w, ["7"]) is None    # order matters; digits never prefix-match


def test_gallery_reads_release_links():
    sys.path.insert(0, str(ROOT.parent.parent / "tools"))
    import build_site
    assert build_site.TAG.fullmatch("football-batch-1") and not build_site.TAG.fullmatch("v1; rm -rf /")


def run():
    fails = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except AssertionError as e:
                fails.append(f"{name}: {e}")
    if fails:
        sys.exit("speech-rule self-test failed:\n  " + "\n  ".join(fails))


if __name__ == "__main__":
    run(); print("speech-rule tests passed")
