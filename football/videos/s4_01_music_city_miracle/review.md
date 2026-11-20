# Review: s4_01_music_city_miracle (v3)

Independent reviewer, 2026-11-20, scored against `RUBRIC.md`. I checked frames every 0.5 s from 0 to 4 s and from 22 to 38 s, every 2 s elsewhere, plus full-resolution crops at 0.3, 2.0, 25.3, 32.8, 36.2 and 37.3 s. I also ran `check.py`, ffprobe and ebur128, and found every effect in `mix.wav` with a matched filter (narration subtracted). I compared those times with `timing.json` and the play keyframes in `video.json`.

## Gates

| # | Result | Evidence |
| --- | --- | --- |
| G1 | **UNVERIFIED (counts as not passed)** | My WebFetch calls to both listed sources (Wikipedia, AP via KSL) were refused (approval not available), so I opened neither. I did not use memory to check the facts. One definite problem doesn't need sources: line 1 says the return "started with a throw backwards", but line 6 shows it started with Neal fielding the kick and handing off. The video contradicts itself. Suspicions I couldn't verify: that Dyson "rarely practiced special teams" (it may have been the play he hadn't practiced), and why "the top 2 returners were out". |
| G2 | PASS | `check.py`: OK, 148 words. |
| G3 | PASS | 60.000 s, 1080x1920, 24 fps, voice `af_heart` (timing.json, tts.py). |
| G4 | PASS | Kick, Neal's catch, handoff, cross-field throw, Dyson's catch, sideline run and end-zone entry are all on the field (22–37 s, and the cold open 0–4.5 s). |
| G5 | **FAIL** | 0.0–0.5 s, the very first frame: Neal's and Wycheck's bodies overlap (they start 1.7 units apart). 25.0–25.5 s: at the handoff their heads clip into each other. 22.0–23.0 s: a red player is cut in half by the bottom edge. 36.5–37.5 s: t1 is cut by the left edge at full height, right beside the TD. 2.0 s: Wycheck is cut by the bottom edge behind the caption. |
| G6 | PASS | `mix.py` loads only `engine/audio/sfx/*.wav`. Measured: kick ×1, catch ×3, whoosh ×3, roar ×1, cut ×4, hit ×1. |
| G7 | PASS | Generic team colors, no logos or likeness, not an injury story. |

## Score

| Area | Pts | Reason |
| --- | --- | --- |
| Hook | 9/15 | It now opens on the play (good), but line 1 runs 4.4 s, "BACKWARDS" lands at about 2.5 s, frame 1 is two players overlapping on an empty field, and it isn't the most surprising fact (16 s left, down 1, it was ruled legal). |
| Story | 12/15 | A beat every 3–5 s, the ruling lands at 45–48 s, and the question has a one-word answer. But the question is asked twice (lines 11 and 16), and line 1 contradicts line 6. |
| Look | 12/20 | The stands are warm and full. Play shots are flat green with no props and little contact shading. Score boards are cropped at the frame edge at 5–9, 11–13, 19–21 and 53–55 s. The office (43–48 s) is a bare wall and a desk. |
| Bodies/acting | 10/15 | Gait reads well. Two clipping moments (0 s, 25 s). Dyson's TD `celebrate` doesn't read: he stands with his back to the camera at 36.5–37.5 s. Moods otherwise fit. |
| Motion/camera | 5/10 | Line 10: Dyson covers 8 units in 0.59 s (13.6 u/s, limit 12). b3 and t2 run at z 6.5–9 in lines 1, 6 and 7 (limit +6). During the run, the Bills chasers are mostly out of frame, so it reads as three teammates jogging. The ball isn't visible on the carrier. |
| Sound | 11/15 | −14.3 LUFS integrated, voice clear, ducking fine. In sync: whooshes on release (1.47, 22.52, 27.80 s), Neal's catch on arrival (23.81 s), roar 0.07 s after the goal-line crossing (36.08 vs 36.01 s), one hit (45.39 s). Off: Dyson's catch sound plays 0.57 s early in the cold open (2.00 vs ball arrival 2.57 s) and 0.53 s early on the real play (28.28 vs 28.81 s); the frames confirm the ball is still mid-air. The kick sound (22.62 s) plays with the kicker off screen, 0.57 s after his kick action. |
| Captions | 3/5 | Two lines max. The red key box sits offset from its word every time ("WYCHECK.", "SIDELINE.", "TOUCHDOWN.", "LEGAL."). At 2.0 s the caption sits over Wycheck. |
| Gameplay | 3/5 | Opens on a 100-yard TD. The disks are tiny and the top of the panel is mostly empty. Two 1-lateral plays gain only 27–28 yards. |

**Total: 65/100. NO SHIP** (G1 unverified, G5 failed, score under 85).

## v2 findings: status

| v2 finding | Status |
| --- | --- |
| Kicker idle or in the foreground during the run (30–32 s) | Fixed |
| Red defenders clipping into Dyson (33 s) | Fixed (the chasers are now mostly off frame, which costs Motion) |
| Wycheck cut by the bottom edge at 29.7 s | Fixed there; new edge cuts at 2.0, 22–23 and 36.5–37.5 s |
| Line 1 too long, "ended" wrong | Partly. "ended" is gone, but the line is still 4.4 s and "started with a throw" is wrong |
| Boards cropped | Not fixed |
| Kicker happy face during the TD | Fixed (kicker not in the play) |
| `speaker: wycheck` in line 5 | Fixed |
| Ball jump at the handoff | Partly. The gap is 1.7 units, which now shows up as head clipping |
| Defenders at z −11 to −13 | Fixed. New: z +6.5 to +9 in lines 1, 6 and 7 |
| Dyson at 14.3 u/s in line 9 | Fixed (11.6). Line 10 is now 13.6 |
| Neal's catch sound 0.46 s late | Fixed (exact) |
| Double roar | Fixed (one roar) |
| "Touchdown" vs crossing out of sync | Fixed (crossing at 36.0 s inside the word, roar +0.07 s) |
| Key box off its word | Not fixed |
| Gameplay disks tiny | Not fixed |
| G1 sources not opened | Still not opened (tool blocked) |

## Top 5 fixes (points gained per effort)

1. **Dyson's catch timing (lines 1 and 7):** move his `catch` action from 0.42 to 0.55, where the ball arrives. That's two numbers, and the catch gesture and sound land on the ball. About +2 Sound.
2. **Spacing (lines 1, 6, 7):** start Neal 2+ units from Wycheck in line 1, end Neal's line 6 path about 2 units from Wycheck (for example 1.6, 3.6) so the handoff doesn't clip, and clamp b3 and t2 to z ≤ 6. Keep t1 inside the frame at the TD. This clears the G5 failure and gains about +2 Motion/Bodies.
3. **Line 1 rewrite:** under 3 s, accurate, and the biggest fact first (e.g. "Down one, sixteen seconds left. They threw it backwards."). This fixes the contradiction. About +3 Hook, +1 Story. Then drop the duplicate question in line 11, or reword it as a setup.
4. **Captions:** fix the key-box offset in the engine (it's off on every key word). This one engine fix carries over to every video. About +2.
5. **Boards and TD shot:** pull the camera back or move the boards inside the frame. Turn Dyson toward the camera for `celebrate`. Slow line 10 to 12 u/s or less. About +2 to +3 Look and Motion.

Even with all five, this lands around 75–78. Reaching 85 needs Look work: props and contact shading on the field, and a dressed office set. G1 also needs both sources actually opened before shipping.
