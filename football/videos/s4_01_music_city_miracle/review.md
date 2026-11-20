# Review: s4_01_music_city_miracle (v5)

Independent reviewer, 2026-11-20, scored against `RUBRIC.md` and `GUIDELINES.md`. I did not make this video. Every number below was measured fresh on the rebuilt render (out/s4 mp4 22:53, `mix.wav` 22:52, `timing.json` 22:27, `video.json` 22:35).

What I checked:
- Frames every 0.5 s from 0 to 4.5 s and from 21 to 40 s, and every 2 s elsewhere.
- Extra frames on every event: 1.0 and 1.764 s; 21.7–22.9 s, every frame around the kick; 24.9–25.5 s; 28.361 s; 35.55–35.7 s; 6.5–8 s; 47.5–49 s.
- Full-resolution top-half crops of the kick (22.0–22.5 s) and of 6.8, 29.9 and 34.4 s.
- `check.py`, ffprobe and ffmpeg ebur128.
- Effect onsets in `mix.wav`, found with a matched filter on the mix minus the narration (narration loaded through `mix.load`, fitted gain 1.0006). I compared them with the `video.json` keyframes times the new `timing.json`.
- Spacing, speeds and z range, computed from every `play` path.
- The one-shot pose code in `engine/kit.js`.

## Gates

| # | Result | Evidence |
| --- | --- | --- |
| G1 | **UNVERIFIED: sources could not be opened (counts as not passed)** | This environment cannot open either source (Wikipedia, AP via KSL). I did not use memory to verify anything. The script now lists 14 `claims`; each needs two opened sources. The list is below. |
| G2 | PASS | `check.py`: `OK (154 words, voice v2)`. It flags "Wycheck" as an unconfirmed pronunciation (spoken at 26.05–27.19 s). |
| G3 | PASS | ffprobe: 60.000 s video and audio, 1080x1920, 24 fps. `timing.json` voice is `af_heart` at speed 1.0, and `tts.py` `VOICE` is locked to `af_heart`. |
| G4 | PASS | The whole play is on the field: the short kick (22.2 s), Neal fielding it (23.4 s), the handoff (25.1 s), the cross-field throw (27.3 s), Dyson's catch (28.4 s), the sideline run (30.3–34.7 s) and the end-zone entry (35.6 s). |
| G5 | PASS (narrowly) | The five v4 failures are gone. Line 4 no longer has Wycheck at the frame edge. The kicker stands alone, fully visible at the kick (22.0–22.5 s). There's no foreground t2 in line 8. The kicker's cheer clears the ref's face (6.8 s crop). Dyson's cheer clears his neighbours (47.5–49 s). Leftovers, none in a close-up and no 3D intersections (path spacing is at least 1.81 units): Neal sits right behind Wycheck in screen space at 0.0–0.5 s; Wycheck's head overlaps Neal's arm at the handoff, 25.1–25.5 s; red b2 and blue t2 touch silhouettes at 29.5–30.0 s; t1's shoulder is cut by the left edge in the `follow_high` shot at 34.0–34.5 s. |
| G6 | PASS | `mix.py` loads only `engine/audio/sfx/*.wav`. Measured onsets (correlation 0.86–1.00): whoosh 1.030, 22.225, 27.309; catch 1.764, 23.439, 28.361; kick 22.225; roar 35.591; cut 12.682, 21.501, 40.505, 45.593; hit 43.048. Nothing else is in the effects bus. |
| G7 | PASS | Generic figures in team colors, no logos or marks, nothing sexual. The "Hurt." in line 3 is one line, not the center of the story. |

### G1: claims to verify (from `video.json` `claims`)

1. Wild card playoff game, January 8, 2000.
2. Buffalo's field goal put the Bills up 16–15.
3. Sixteen seconds were left after the field goal.
4. The usual kick returner, Derrick Mason, was hurt (concussion). The video says only "your best kick returner? Hurt."
5. Kevin Dyson, a wide receiver, took the return. The spoken line also says kick return practice: "Barely". That isn't in `claims`, so add it or verify it too.
6. The play was called Home Run Throwback.
7. Lorenzo Neal fielded the short kick and handed it to Frank Wycheck.
8. Wycheck threw it across the field to Dyson.
9. Dyson ran 75 yards for the touchdown.
10. Three seconds were left after the touchdown.
11. Referee Phil Luckett reviewed the replay.
12. The call stood: a legal lateral, touchdown.
13. Final score Titans 22, Bills 16.
14. It is known as the Music City Miracle.

Two spoken claims are also not in `claims`: "Twenty six years later" (a date check) and "They say that throw went forward" (Buffalo's argument).

## Score

| Area | Pts | Reason |
| --- | --- | --- |
| Hook | 12/15 | Line 1 is now 2.93 s and "BACKWARDS" starts at 1.58 s, under 3 s. Against that: the first frame is still two blue players overlapping on an empty green field, with no score, no clock and nothing showing "down one, seconds left". "Sixteen seconds left", the strongest stake, isn't in line 1. |
| Story | 13/15 | The duplicate question is gone (line 11 is now a setup). Line 3 now shows a worried Wycheck for "Hurt." Line 8 matches the picture ("Dyson has it"). The ruling lands at 43–46 s, in the last third, and the closing question has a one-word answer. Still off: line 2 is a 6.2 s beat and line 14 is 5.3 s. Line 7 replays the line 1 animation shot for shot. The run (30.3–34.7 s) has no pursuer in frame, so the stakes flatten at the peak. |
| Look | 13/20 | Better: the locker board "HOME RUN / THROWBACK" is fully in frame (17–21.5 s), and the office has a window, plant and desk. Not better: the play shots (0–3, 21.5–30.3 s) are still bare green with only yard lines, with no props or visible contact shading. The `RETURNER: DYSON?` and `REPLAY REVIEW` boards never appear. The office is still mostly empty wall. In the TD shot (35–36.8 s), the figures are small against a wall of crowd. |
| Bodies and acting | 11/15 | Fixed: slow movers now walk (`walkBelow: 3`), and both cheers clear their neighbours. Still wrong, mostly from the engine: one-shot poses are driven by the *line's* u from 0.15 to 0.45 (`MOTION.oneShot`), not from when the action starts. So **the kick**, cued at u 0.03, keeps the leg cocked back when the ball leaves at 22.225 s. The swing peaks at u 0.30 (about 22.9 s), after the camera has left with the ball, so the foot never meets the ball on screen (crops 22.0–22.5 s). **The catches** at u 0.55 snap to the full catch pose in one frame (k is already 1). Capy's `shrug` (36.8–40.5 s) doesn't read. The kicker's `cross` (50.9–55.4 s) is fists up, not crossed arms. The ref's `point` (43–45.6 s) is out of the close-up frame. The cheers take about 1–2 s to rise. |
| Motion and camera | 7/10 | Speeds are now right: runs at 9.5–10.2 u/s in lines 8–10, chasers at 7.9–9.6 u/s, everything under 3 u/s walks, all z within −9.5..+5.8, and spacing at least 1.81. The camera follows smoothly. Still off: the line 8 run has nobody else in frame. t1's shoulder is cut by the left edge at 34.0–34.5 s. The handoff (25.1 s) is a ball floating at hip height with no receive gesture from Wycheck. t1 and t2 jump position across the line 7→8 and 8→9 cuts (t2 goes from z −9.5 to −4.0). |
| Sound | 14/15 | −14.3 LUFS integrated, −1.0 dBTP, voice clear, music ducked. Every cue is within 1 frame of its event: whooshes on release (1.030, 22.225, 27.309 s), catches on the ball's arrival (1.764, 23.439, 28.361 s), kick on the ball's launch (22.225 s), **roar 35.591 s against the goal-line crossing at 35.600 s** (fixed, was 0.28 s late), one hit on "The call stands" (43.048 s), and cuts 50 ms before each set change. The −1: the kick sound plays with no on-screen foot strike (see Bodies). |
| Captions | 5/5 | Two lines max. The key box sits on its word in every frame I checked (BACKWARDS., CUTE., HURT., BARELY., SKETCHY., YOU., HOPEFULLY., SIDELINE., 75, TOUCHDOWN., FORWARD., REPLAY., STANDS., MAD., ELSE.). No caption covers a face. |
| Gameplay half | 3/5 | `reel.json` is unchanged. It opens on a 100-yard TD, but the disks are tiny and often sit in a corner of the panel. Play 2 has 2 laterals for 57 yards with no TD, and plays 4 and 5 are one-lateral plays for 28 and 27 yards. |

**Total: 78/100. NO SHIP.** G1 is unverified and the score is under 85. All other gates pass.

## Changes since 68/100

| v4 finding | Now |
| --- | --- |
| G5: Wycheck half out of frame in line 4 | **Fixed** (not in the shot) |
| G5: kicker blocked at the kick | **Fixed** (b1–b3 moved to z −1.5..−6.5) |
| G5: t2 foreground cut in line 8 | **Fixed** (t2 behind, at z −9.5) |
| G5: cheers through faces (lines 2 and 14) | **Fixed** |
| Roar 0.28 s late | **Fixed** (35.591 vs crossing 35.600) |
| Kick sound 0.09 s after the ball | **Fixed** in the audio (22.225 = ball launch). The leg swing is still late (engine) |
| Run gait at 1.3–2.8 u/s | **Fixed** (engine walks anything under 3 u/s) |
| Line 1 over 3 s | **Fixed** (2.93 s) |
| Duplicate closing question | **Fixed** |
| Line 3 shows the Bills kicker for "Hurt." | **Fixed** (worried Wycheck) |
| Line 8 says "catches" after the catch | **Fixed** ("Dyson has it") |
| Locker board cropped | **Fixed** |
| No score or clock in the first frame | Not fixed |
| Field and office props, contact shading | Office slightly better; field not fixed |
| Returner and replay boards not visible | Not fixed |
| No chaser in frame during the run | Not fixed (t2 moved out, nobody moved in) |
| Shrug, cross and point don't read | Not fixed |
| Gameplay reel | Not fixed |
| G1 | Still unverified (tool blocked); `claims` list added |

Points gained: Hook +2, Story +2, Look +1, Bodies +1, Motion +2, Sound +2 = **+10**.

## Gap to 85 (7 points), ranked by points per effort

1. **Engine one-shot timing (+2: Bodies +1, Sound +1).** In `kit.js` `pose()`, measure `k` from the action's own start u, not from the line's u. For example, pass `u - actionStartU` and use a fixed window of about 0.4 s. Then the kick's swing peaks on the frame the ball leaves (22.225 s), and the catches ease in over 3–4 frames instead of snapping. It's one engine change, and it carries over to every video.
2. **Hook frame (+2 Hook).** Get the score and clock into frame 1. Either frame the line 1 `follow_high` so the board (already set in `setOpts`) is visible, or cut the first 0.5 s to the board. Say "Sixteen seconds left. Down one. You throw it backwards." (still under 3 s at speed 1.0, by the checker's estimate).
3. **Gameplay (+2).** Raise the disk scale in the bottom panel, and have `highlights.py` drop non-TD plays with laterals under 40 yards (plays 2, 4 and 5 here). Then fill with TDs.
4. **Readable gestures (+1 Bodies).** Line 13: use a `medium` shot so the ref's `point` is in frame. Line 15: fix `cross` in `kit.js` (the forearms need to fold across the chest, not stand up as fists). Line 11: a bigger shrug (shoulders and palms up).
5. **Run tension (+1 Motion, maybe +1 Story).** In line 8, bring one Bills chaser into frame about 3 units behind Dyson, e.g. b1 path from x 2.5 → 30, z −6.5 (still at least 1.5 apart). Keep t1 inside the frame at 34.0–34.5 s, e.g. t1 z −6.3 → −7.
6. **Look (+3–4, the biggest effort).** Field props (pylons, a down marker, a team bench or sideline strip at z −10) and visible contact shading in the play shots. Make the `RETURNER: DYSON?` and `REPLAY REVIEW` boards appear in shot. Dress the office (monitors for the replay, a second prop group).

Fixes 1–5 are worth about +8 to +9 and would reach about 86–87 without the big Look work. That margin is thin: one fix that lands short leaves it under 85, so fix 6 is the safe route. Separately, G1 must be verified by opening both sources before the video can ship at any score.
