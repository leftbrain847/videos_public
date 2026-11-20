# Review: s4_01_music_city_miracle

Independent reviewer, 2026-11-20, scored against `RUBRIC.md`. I checked the contact sheet, 30+ extra frames from 23 to 38 s, `mix.py`, `reel.json`, `check.py`, ffprobe and ebur128.

## Gates

| # | Result | Evidence |
| --- | --- | --- |
| G1 | **FAIL (not verified)** | My WebFetch calls to both listed sources (Wikipedia, AP via KSL) were blocked pending approval, so I opened neither. From memory, the claims match the known record, but that doesn't meet the gate. Line 1 also says the game "ended on a kickoff return", which is wrong: 3 s were left, and the Titans kicked off again. |
| G2 | PASS | `check.py`: OK, 157 words. |
| G3 | PASS | 60.000 s, 1080x1920, `af_heart` in timing.json. |
| G4 | PASS | Kick, catch, handoff, cross-field throw, sideline run and TD are all shown on the field (23–38 s). |
| G5 | **FAIL** | At 30–32 s the Bills kicker (#2) stands idle and smiling mid-play, and at 32.0 s he's large in the foreground with Dyson behind him. At 33.0–33.6 s, three red defenders clip into each other and into Dyson. At 29.7 s, Wycheck is cut off by the bottom edge. |
| G6 | PASS | `mix.py` loads only `engine/audio/sfx/*.wav`. |
| G7 | PASS | Generic team colors, no logos, no likeness, no injury story. |

## Score

| Area | Pts | Note |
| --- | --- | --- |
| Hook | 8/15 | Line 1 runs 6.4 s and the twist ("wasn't") only lands at about 4.1 s. Frame 1 is two people standing, not the return. |
| Story | 12/15 | A clear beat every 3–5 s, the ruling lands at 46 s, and the question has a one-word answer. |
| Look | 13/20 | Warm light and full stands, but boards are cropped top-right (0–6, 20–23, 38–52 s). The field shots are flat green with little contact shading. |
| Bodies/acting | 10/15 | The kicker keeps a happy face during the TD play. Wycheck is set as `speaker` in line 5, so his mouth moves to Capy's voice. Gait reads well. |
| Motion/camera | 5/10 | The ball jumps about 5 units at the handoff (Neal at (3.3, 1.2), Wycheck at (-0.5, 5)). Defenders run at z −11 to −13, past the −10 limit. Dyson runs about 14.3 units/s in line 9. |
| Sound | 10/15 | −14.3 LUFS and ducking are fine. Neal's catch sound is 0.46 s late (25.74 vs 25.28 s). Two crowd roars stack (37.40 and 37.58 s). The voice says "Touchdown" at 35.75 s, but he crosses at about 37.3 s. |
| Captions | 4/5 | Clean and two lines at most. Some red boxes sit off their word ("WYCHECK.", "SIDELINE."). |
| Gameplay | 3/5 | Opens on a TD, but the disks are tiny and half the panel is empty. The reel includes a 15-yard play with 1 lateral. |

**Total: 65/100. NO SHIP** (G1 and G5 failed, and the score is under 85).

## Top 5 fixes

1. **32–34 s:** take the kicker out of lines 7–8 (`place: {kicker: false}`) and space b1–b3 1.5+ units apart, within z ≥ −10.
2. **0–6 s:** shorten line 1 to under 3 s and drop "ended". Open on the kick or the throwback.
3. **35.7–37.3 s:** sync "Touchdown" with the goal-line crossing by moving the crossing earlier, and keep Dyson at 12 units/s or less.
4. **25.3 s:** move Neal's catch cue onto the ball's arrival and close the handoff gap. Remove the second roar (t1's `celebrate`).
5. **Whole video:** pull the camera back or move the boards so they aren't cropped. Remove `speaker: wycheck` from line 5. Re-run G1 with both sources actually opened.
