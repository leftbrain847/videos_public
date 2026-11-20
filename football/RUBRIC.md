# Quality rubric: every video must pass before it ships

Set by J on 2026-11-20 after UAT. Reference: the `bob.figures.it.out` shorts J shared (IMG_0683 and the pumpkin-patch recording). A video that fails any **gate** does not ship, whatever its score. The rest is scored; a video ships at **85/100 or more**.

## What makes the reference good

1. **Every frame looks like a finished illustration.** Warm, soft, directional light with gentle shadows and contact shading where things meet (ambient occlusion); a rich, specific set (a barn, a fence, hay, a framed picture) built from many props; color is warm and saturated but harmonious.
2. **Bodies read as people.** Big round head, but a real torso with shoulders, arms and legs with joints, mitten hands with a thumb, shoes, clothes with collars and folds; proportions are the same in every shot.
3. **Two characters, one look.** The same recurring cast in the same clothes; faces carry the emotion through brows and mouth alone.
4. **Composition is deliberate.** Subject large in frame, eye-level or slightly low, rule of thirds, nothing important cropped, background supports the beat; a new image every caption, so the eye never waits.
5. **Captions are a design element.** Two lines at most, bold italic white with a black stroke, one key word in a red box, always in the same place.
6. **Nothing distracts.** No motion is better than wrong motion; no sound effect is better than a cheap one. Restraint is why it reads as polished.

We keep motion and sound because they can beat stills, but only at that standard.

## Gates (any fail = does not ship)

| # | Gate | How it's checked |
| --- | --- | --- |
| G1 | Facts: every claim matches two sources opened and listed in `sources` | reviewer, against the sources |
| G2 | `engine/check.py` passes (length, keys, shots, Capy opens and closes, question at the end) | automatic |
| G3 | Exactly 60.0 s, 1080×1920, voice is Kokoro `af_heart` only | automatic (ffprobe, tts settings) |
| G4 | The story's key play is shown on the field (`play` lines), when the story is about a play | reviewer, stills |
| G5 | No broken frames: nobody clipping through anyone, cut in half by the frame edge in a close-up, floating, or walking into the camera; nothing blocks the subject | reviewer, contact sheet of every 2 s |
| G6 | No synthesized or cheap sound effects; only files in `engine/audio/sfx/` (recorded, CC0) | automatic (mix uses only that folder) |
| G7 | No logos, team marks or real-person likeness; nothing sexual; no story centered on a serious injury or death | reviewer |

## Score (100)

| Area | Points | Full marks when |
| --- | --- | --- |
| **Hook** | 15 | Line 1 states the most surprising fact in under 3 s; the first frame already shows the situation |
| **Story** | 15 | A new beat every 3–5 s; stakes rise; the payoff lands in the last third; the closing question has a one-word answer |
| **Look** | 20 | Every sampled frame could be a still from the reference: warm key light, soft shadows and contact shading, a set with depth and props, a clear focal subject, no empty or flat backgrounds |
| **Bodies and acting** | 15 | Moods match every line; one-shot gestures happen once and mean something; idle is still; walking and running read as natural (knees, elbows, arm swing opposite the legs, lean) |
| **Motion and camera** | 10 | Players move at believable speeds along clear paths, never overlapping; the camera follows smoothly, frames the action, and cuts at least every caption pair |
| **Sound** | 15 | Voice always clear (music ducks under it); effects land on the event within 2 frames (kick, catch, flight, touchdown crowd, scene cut, one reveal hit); no effect without an on-screen cause; −14 LUFS |
| **Captions** | 5 | Two lines max, key word boxed and aligned, never covering a face |
| **Gameplay half** | 5 | Reel opens on a touchdown; plays are readable at human speed; no pointless laterals; no carrier running out of bounds |

## Motion requirements

- Idle is still: breathing, blinks and a slight head drift only.
- Every gesture is one-shot, tied to its line, and holds: throw, kick, catch, point, cheer, shrug, facepalm. No loops, no throwing without a ball.
- Gait: walk and run come from `pose()` in `engine/kit.js` (knee flex in swing, straight leg at foot strike, elbows bent and arms opposite the legs, forward lean and bob). Speeds: walk 1.5–3 units/s, run 7–12.
- Plays follow real geometry: the field runs along x, the camera sits at +z, the action stays between z −10 and +6, people keep 1.5+ units apart.

## Sound requirements

- Music: the piano bed, ducked about 9 dB under the voice, faded in and out.
- Effects only for on-screen events, from `engine/audio/sfx/` (see `engine/audio/SOURCES.md`): kick, catch, ball flight, touchdown crowd, scene-change swish, and at most one reveal hit per video.
- Nothing synthesized. If a needed sound isn't in the library, the moment stays silent.

## Review process

1. `engine/make.sh` writes one still per line; the reviewer reads them and a 2-second contact sheet of the final mp4 (`engine/review.sh`).
2. A fresh agent that didn't make the video scores it against this rubric and lists every gate result. The score and notes go in `videos/<id>/review.md`.
3. Under 85 or any gate failed: fix and re-render, at most twice; then mark the video `blocked` in its slate with the reason.
