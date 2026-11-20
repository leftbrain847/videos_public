# Review: s4_01_music_city_miracle (v4)

Independent reviewer, 2026-11-20, scored against `RUBRIC.md` and `GUIDELINES.md`. I did not make this video.

What I checked:
- Frames every 0.5 s from 0 to 4.5 s and from 22 to 39.5 s, and every 2 s elsewhere.
- Full-resolution top-half crops at 0.0, 1.0, 2.0, 2.2–2.35, 2.5, 3.5, 4.0, 4.6–13.0, 22.6–23.3, 25.8–26.25, 28.95–29.1, 36.2–36.55, 47.0 and 48.0 s.
- `check.py`, ffprobe and ffmpeg ebur128.
- Every effect in `mix.wav`, found with a matched filter after subtracting the narration (resampled to 44.1 kHz, fitted gain 1.000). I compared those times with the play keyframes in `video.json` times `timing.json`.
- Player spacing, speeds and z range, computed from every `play` path.

## Gates

| # | Result | Evidence |
| --- | --- | --- |
| G1 | **UNVERIFIED: sources could not be opened (counts as not passed)** | This environment blocks WebFetch to both listed sources (Wikipedia, AP via KSL). I did not use memory to verify anything. The claims to check are listed below. |
| G2 | PASS | `check.py`: `OK (153 words, voice v2)`. It flags "Wycheck" as an unconfirmed pronunciation, so listen to it at 0.15–1.35 s. |
| G3 | PASS | ffprobe: 60.000 s video and audio, 1080x1920, 24 fps. `timing.json` voice is `af_heart` at speed 1.03, and `tts.py` `VOICE` is locked to `af_heart`. |
| G4 | PASS | The whole play is on the field: the short kick, Neal fielding it, the handoff to Wycheck, the cross-field throw, Dyson's catch, the sideline run and the end-zone entry (22.5–37.5 s, plus the cold open at 0–4 s). |
| G5 | **FAIL** | (a) 13.7–17.9 s (line 4, `low` shot on Dyson): Wycheck's face is cut in half by the right frame edge (frames 14, 16). (b) 22.6–23.3 s (line 6, the kick): the kicker is hidden behind b3 and b1. The four red players stack into one blob, and the ball appears from behind b3 at 23.2 s with no kicking leg visible, so the subject is blocked. (c) 32.0–33.0 s (line 8, `follow`): t2, a large foreground figure, is cut by the left edge at 32.5 and 33.0 s and covers t1 and Dyson on screen. (d) 6.5–9.0 s: the kicker's `cheer` hand passes across the ref's face. (e) 48.0 s: Dyson's cheering arms reach into Wycheck's head and the kicker's face. None of these are true 3D intersections: path spacing is at least 1.81 units everywhere. They are screen overlaps and edge cuts. |
| G6 | PASS | `mix.py` loads only `engine/audio/sfx/*.wav`. Measured onsets (correlation 0.85–1.00): whoosh 1.332, 23.206, 28.128; catch 2.317, 24.420, 29.044; kick 23.296; roar 36.555; cut 13.662, 22.482, 40.775, 45.868; hit 43.329. Nothing else is in the effects bus. |
| G7 | PASS | Generic figures in team colors, no logos or marks, nothing sexual. The "Hurt." in line 3 is one line, not the center of the story. The jersey numbers 87 and 89 are plain numerals, not likenesses. |

### G1: claims that need two opened sources

1. Frank Wycheck threw the backward, cross-field pass.
2. The Titans trailed by one (Bills 16, Titans 15) before the return.
3. Buffalo had just kicked a field goal to take that lead.
4. Sixteen seconds were left.
5. The Titans' best kick returner was hurt and out.
6. Kevin Dyson was a receiver who had barely practiced kick returns. The previous reviewer flagged this; it may instead be that he hadn't practiced *this play*.
7. The play was called "Home Run Throwback".
8. The kick came short and Lorenzo Neal fielded it.
9. Neal handed the ball to Wycheck.
10. Dyson caught it and ran down the sideline.
11. The run was 75 yards.
12. Three seconds were left after the touchdown.
13. Buffalo's case was that the throw went forward.
14. Referee Phil Luckett reviewed the replay.
15. The call stood: lateral, touchdown.
16. The final score was Titans 22, Bills 16 (so the extra point was good).
17. "Twenty six years later": this depends on the game date, which the `setOpts` board says is Jan 2000.
18. Tennessee calls it the Music City Miracle.

## Score

| Area | Pts | Reason |
| --- | --- | --- |
| Hook | 10/15 | Line 1 no longer contradicts the play, which is good. But it runs 3.94 s, and the key word "BACKWARDS" only starts at 2.50 s. The first frame is two blue players overlapping on an empty green field: no score, no clock, nothing that shows "down one, seconds left". The strongest facts (16 s left, ruled legal) aren't in line 1. |
| Story | 11/15 | Beats mostly land every 3–5 s, but line 2 runs 6.2 s. The ruling lands at 43–46 s, in the last third, and the closing question has a one-word answer. Against that: the question is still asked twice (line 11 "Was that throw forward?", line 16 "Lateral or forward pass?"). Line 3 says "your best kick returner? Hurt." over a smug close-up of the *Bills* kicker. Line 8 says "Dyson catches it" at 30.69 s, but the catch was shown at 29.04 s, and line 8 shows him already running. Line 7 replays the line 1 animation exactly. |
| Look | 12/20 | The stands are warm and full, and the field boards are now inside the frame (lines 2 and 14). The play shots (0–4, 22–30 s) are still flat green with nothing but yard lines. The locker board is cropped to "HO / THRO" at 18–22.5 s. The `RETURNER: DYSON?` and `REPLAY REVIEW` boards never appear in frame. The office (40.8–45.9 s) is a bare wall, a desk and half a plant cut by the edge. In the TD wide shot (37 s), the figures are small. |
| Bodies and acting | 10/15 | Dyson's TD `celebrate` now faces the camera, which is fixed. Problems: in lines 1, 6 and 7, players animate a full run while moving 1.3–2.8 u/s (Neal 2.1, b1 1.8, b2 and b3 1.3, the kick coverage 1.3–1.6), so it reads as slow motion or running in place. The `cheer` arms rise slowly over about 1.5 s (5.5→7.0 s and 47.0→48.0 s) and sweep through the neighbours' faces. Capy's `shrug` in line 11 doesn't read. The kicker's `cross` in line 15 is fists up, not crossed arms. The ref's `point` in line 13 is out of frame in the close-up. |
| Motion and camera | 5/10 | Fixed: the run speeds are 10.2, 10.0 and 10.0 u/s in lines 8–10, and every z is within −10..+6. Not fixed: run-gait speeds of 1.3–2.8 u/s in the play lines. The kicker is invisible at the kick. In lines 1 and 7, Neal sits right behind Wycheck in screen space (0.0–1.0 s and 27.5 s). The handoff (26.0 s) shows Wycheck's head over Neal's arm and the ball moving at hip height with no receive gesture. No Bills chasers are visible during the run (31–36 s), so it reads as teammates jogging. In line 9, t1 is cut by the left edge (34.0–35.0 s). |
| Sound | 12/15 | −14.3 LUFS integrated, −1.1 dBTP, voice clear, the music ducks under it. In sync to the frame: whooshes on release (1.332, 23.206, 28.128 s), all three catches on the ball's arrival (2.317, 24.420, 29.044 s; the v3 Dyson catch timing is fixed), cuts 50 ms before each set change, and one hit on "The call stands" (43.329 s). Off: the **roar is 0.28 s late** (Dyson crosses the goal line at 36.28 s and the roar starts at 36.555 s, about 7 frames; it is keyed to `celebrate`, not to the crossing). The **kick** sound is 0.09 s after the ball leaves (just over 2 frames), the kicker's `kick` action starts 0.45 s before the ball moves, and the kicker can't be seen. |
| Captions | 5/5 | Two lines max. The red key box now sits on its word in every frame I checked (BACKWARDS., CUTE., HURT., BARELY., SKETCHY., YOU., HOPEFULLY., SIDELINE., 75, TOUCHDOWN., FORWARD?, REPLAY., STANDS., MAD.), so the v3 offset is fixed. No caption covers a face. |
| Gameplay half | 3/5 | `reel.json` is unchanged. It opens on a 100-yard TD, but the disks are tiny, and at 22–28 s they sit in the top quarter of the panel with the rest empty. Plays 4 and 5 are one-lateral plays that gain 28 and 27 yards, and play 2 has 2 laterals for 57 yards with no TD. |

**Total: 68/100. NO SHIP.** G1 is unverified, G5 fails and the score is under 85.

## v3 findings: status

| v3 finding | Status |
| --- | --- |
| Dyson's catch sound early (lines 1 and 7) | **Fixed** (2.317 and 29.044 s, on the ball's arrival) |
| Line 1 contradicts line 6 | **Fixed** (now "You're Frank Wycheck... You throw it backwards") |
| Neal and Wycheck clipping at 0 s and 25 s | Partly. Path spacing is now ≥2.6, but they still overlap on screen at 0.0–1.0, 26.0 and 27.5 s |
| b3 and t2 at z > 6 | **Fixed** |
| Line 10 at 13.6 u/s | **Fixed** (10.0) |
| TD `celebrate` with his back to the camera | **Fixed** |
| Key box off its word | **Fixed** |
| Boards cropped | Field boards fixed; the locker board is still cropped at 18–22.5 s |
| Duplicate question (lines 11 and 16) | Not fixed |
| Line 1 over 3 s | Not fixed (3.94 s) |
| Chasers out of frame during the run | Not fixed |
| Office bare, field without props | Not fixed |
| Gameplay disks tiny, weak lateral plays | Not fixed |
| G1 sources not opened | Still not opened (tool blocked) |

## Top fixes (points gained per effort)

1. **Roar on the crossing (line 10), one line of JSON:** add `"sfx": [[0.41, "roar"]]` to line 10. `mix.py` puts a line's own cues first and keeps only one roar per line, so this replaces the `celebrate`-keyed roar at 0.55. The roar moves from 36.555 to about 36.27 s, on the goal-line crossing. About +1 Sound.
2. **Line 4 frame edge (G5a):** set `place.wycheck` to `false` in line 4, or move him to about `[2.6, -0.5]` so he sits fully in frame behind Dyson. That's one value. Clears part of G5 and gains about +0.5 Look.
3. **The kick (line 6, G5b and sound):** move b3 off the camera line to the kicker, e.g. b3 `[[0,25.5,-1.5],[1,19,-1]]`, and b1 to z −0.5, so the kicker at (24, 2) stands alone. Then set the kicker's `kick` action to `0.03`. `mix.py` adds 0.12, so the sound lands at u=0.15, the frame the ball leaves. Turn the kicker to face about −60 so the leg swing shows. About +1 Sound, +1 Motion; clears G5b.
4. **Line 8 foreground (G5c):** t2 at z −4.5 sits between the camera and Dyson. Trail him behind, e.g. start `[0, -1, -6]`, or keep z ≤ −6. Bring one Bills chaser into frame behind Dyson (b1 start x 0 rather than −2, still ≥1.5 apart). Change line 8 to "Dyson has it. He takes off down the sideline." so the words match the catch already shown at 29.04 s. About +1 Motion, +1 Story.
5. **Cheer clearance (G5d/e):** line 2: kicker to `[1.8, 0]` or ref to `[-0.6, -3]`. Line 14: Wycheck to `[-2.6, 0.3]`, kicker to `[3.0, -1.0]`. Four numbers. Clears the rest of G5 and gains about +1 Bodies.
6. **Slow "runs" (lines 1, 6, 7):** any player moving under 3 u/s gets `walk` or `idle`, not the default run gait (Neal and b1–b3 in lines 1 and 7, b1–b3 and the kicker after his kick in line 6). Or shorten those lines' paths so the movers really run 7+ u/s. About +1 Bodies, +1 Motion.
7. **Script tightening:** cut line 1 under 3 s with the stakes in it, e.g. "Sixteen seconds left. Down one. You throw it backwards." Show a scoreboard in frame 1 (the field board is already set in `setOpts`, but the `follow_high` camera never sees it). Change line 11 to a setup instead of a second question: "Buffalo has one hope left. The replay." In line 3, show the Titans side (Dyson, worried) instead of the smug Bills kicker. About +2 Hook, +1 Story.
8. **Boards and sets:** pull the locker camera back or move the board left so "HOME RUN / THROWBACK" fits (18–22.5 s). Make the `RETURNER: DYSON?` and `REPLAY REVIEW` boards visible. About +1 Look.
9. **Bigger effort:** field props (pylons, benches, a down marker, a sideline crowd strip), visible contact shading on the field, a dressed replay booth, and a larger disk scale in the gameplay panel. Needed to get Look above about 15/20 and Gameplay to 5/5.

With fixes 1–8, I estimate about 78–80. Reaching 85 needs fix 9 as well. G1 also needs both sources actually opened, with the claims above checked, before this can ship.
