# Football shorts: guidelines

The rules every script and animation follows. `engine/check.py` enforces the measurable ones; the rest is judgment, so read this before writing a video. J's decisions (2026-11-20) are marked **(J)**.

## The format

- **1080×1920, exactly 60 s.** Top half: the story, in the low-poly 3D style. Bottom half: Disk Football highlights (the reel ranks touchdowns first; laterals only count when the play gains real yards). **(J)**
- **Voice: Kokoro `af_heart`, locked. (J)** It's the Mastery Field Guide voice. No other voice, ever. Settings live in `engine/tts.py` `VOICE`.
- **Narrator: Capy. (J)** A calm, unbothered capybara referee with headphones and an orange on her head. She is who the audience attaches to: she opens and closes every video and appears whenever she can guide the viewer (a turn, a reveal, the payoff). Characters in the story never take her place as host.
- **Look: smooth and human-shaped. (J)** Every surface is smooth and curving (no faceted "Minecraft with curves"), bright warm studio light, soft shadows, clean full sets. Reference: J's screenshot of the low-poly store scene (IMG_0683). Build with `engine/kit.js` parts only, so every video matches.
- **Not sexual, ever. (J)** Characters are mascots, animals, objects or fully clothed everyday people.

## Theme and sets **(J)**

Fascinating football moments and rules, with recency encouraged: stories people may remember stick better. Four sets of 25:

| Set | Name | What goes in it |
| --- | --- | --- |
| s1 | Wait, that's the rule? | Real rules, loopholes and the games that exposed them (tuck rule, fair catch kick, catch rule, overtime changes, playoff tiebreak math). |
| s2 | This season | The 2026 season's wildest moments, rulings and records, while people still remember them. Verify everything against coverage from this season. |
| s3 | The strange years | Seasons and games that should not have happened: the 2020 COVID season (Kendall Hinton, empty stadiums, Tuesday games), strikes and replacement players, fog, snow and blackout games. |
| s4 | Endings nobody forgets | Final-minute chaos: lateral miracles (Music City Miracle, River City Relay), 13 seconds, the Raiders–Chargers tie scenario, Minneapolis Miracle. |

No story in two sets. Leave out stories whose center is a serious injury or a death.

## Tone **(chosen 2026-11-20)**

**Deadpan calm about chaos.** Capy narrates the most absurd football in the steadiest voice; the comedy is the gap between how wild the facts are and how unbothered she is. Short sentences, concrete numbers, one dry aside per video at most. Respectful about people: laugh at situations, never at a player.

## Script rules

- **Hook in the first line (0–3 s):** open on the single most surprising fact, said plainly ("In 2020, an NFL team played a real game with zero quarterbacks."). No "did you know", no greeting, no throat-clearing.
- **A new beat every 3–5 s:** a number, a turn, a reveal or a consequence. Cut any line that doesn't move the story.
- **Escalate:** each beat raises the stakes or the absurdity; the biggest number or twist comes in the last third.
- **End with a question people can answer in one word or a number** ("Could you play quarterback on one night's notice?"). Capy says it. It's the comment bait.
- **Length:** 10–18 lines, 135–172 spoken words (about 2.6 words a second fits 60 s).
- **Numbers:** write them as words in `text` (that's what the voice reads) and as digits in `cap` (that's what viewers read). See "Writing for the voice".
- **Key words:** 1–2 per line, highlighted in red. Pick the word that carries the line (the number, the twist).

## Accuracy (non-negotiable)

- Every factual claim is checked against **at least two sources, opened with WebFetch** (not just search snippets), listed in `sources` with title and URL. Prefer the league, team sites, AP, ESPN, NFL.com, Pro Football Reference, major papers.
- When sources disagree, use the version they agree on or leave the detail out. Never invent a quote. A paraphrase of what someone said is fine when a source reports it.
- Real names are fine for public facts. Characters never imitate a real person's likeness: they are generic figures in team colors, with no logos or team marks on screen.

## Show the play (J, 2026-11-20 UAT)

The moment the story is about plays out **on the field**, not as people standing and talking. Any video about a play (a return, a catch, a fumble, a kick) uses `play` on the lines that narrate it: players run real paths (`path`), the ball flies (`ball`) or is carried (`carry`), the camera follows like a broadcast (`follow`, `follow_high`). The template is `videos/s4_01_music_city_miracle`.

- Field coordinates: the field runs along x (left to right on screen), goal lines at ±`endZone` (set in `setOpts`), the stands behind at −z. Keep the action between z −10 and +6 so nobody walks into the camera.
- Players never overlap: keep 1.5+ units between people in the same frame.
- Speed reads as running: 7–12 units a second; compress distance rather than speeding past 14.

## Motion (J, 2026-11-20 UAT)

Every move must mean something. Idle is still: breathing, blinks, a small head drift. `talk` is a small hand beat for whoever speaks. One-shot moves (`throw`, `kick`, `catch`, `point`, `cheer`, `shrug`, `facepalm`) play once at the start of the line and hold. No looping arm waves, no throwing motion without a ball, no celebrating unless something was won.

## Sound (J, 2026-11-20 UAT)

- **Music:** the Comprehensible Input piano piece (`engine/audio/piano.mp3`, Salamander Grand Piano V3 by Alexander Holm, CC BY 3.0: credit it in every post's description), ducked under Capy's voice.
- **Effects:** recorded, professionally made CC0 sounds only (`engine/audio/sfx/`, from wyzowl/sfx-kit; see `engine/audio/SOURCES.md`). Cued automatically from plays (kick, catch, ball flight, touchdown crowd) and scene changes; a line can add the one reveal hit with `"sfx": [[u, "hit"]]`. Never synthesized: no sound beats a cheap one.
- Final loudness: −14 LUFS (`engine/compose.py`).

**Every video must pass `RUBRIC.md`** (gates plus a score of 85+), reviewed by a fresh agent.

## Animation rules

- **Sets:** `locker`, `field`, `press`, `office`, `living`, `tunnel` (see `SETS` in `engine/kit.js`). Use the set that fits each beat; change sets 2–4 times per video.
- **Shots:** at least 5 distinct shots, never the same shot type 3 times in a row. Types: `wide`, `medium`, `close`, `low`, `high`, `two`, `ots`, and for plays `follow` / `follow_high` (on a cast id or `ball`).
- **Acting:** every line sets a mood that matches what's said (`shocked` for the reveal, `sad` for the loss) and an action where it helps (`point`, `facepalm`, `cheer`, `shrug`...). Whoever speaks gets `speaker` (their mouth moves).
- **Boards:** use `board` text for numbers worth seeing (scores, stat lines, "QB: ???").
- **Capy:** `"capy": {"kind": "capy"}` in the cast; speaker on the first and last lines; on screen for at least one guide moment in the middle.
- **Review before rendering:** look at the stills `make.sh` writes (one per line). Fix anything clipped, hidden, off-frame, or a character in the wrong set before the full render.

## Files

```
football/
  GUIDELINES.md           this file
  SLATE.md                the 100 stories: id, title, one-line hook, status
  engine/                 kit.js (characters, props, sets), page.html (scene player), render.mjs, tts.py,
                          highlights.py, compose.py, check.py, make.sh, setup.sh
  gameplay/               the shared Disk Football capture pool (clips + events)
  videos/<id>/video.json  one script: cast, lines (text, cap, key, shot, act, place, set, board), sources
  out/<set>/<id>.mp4      finished videos
```

Make one: `engine/setup.sh` once, then `engine/make.sh videos/<id> <index>` from `football/`.

## Writing for the voice (Kokoro af_heart) **(J, 2026-11-20)**

Kokoro reads `text` exactly as written and picks its own emphasis and pauses, so the script is the only lever. These rules make whole classes of misreads impossible instead of patching them one by one. `engine/voice.py` holds them; `engine/check.py` fails any script marked `"voice": "v2"` that breaks one (older scripts get a count until they're rewritten). Every rewritten script gets `"voice": "v2"`.

1. **`text` is exactly what is spoken.** No digits, symbols or abbreviations: "nineteen seventy eight", "thirty one to three", "fourth and twenty five", "number one pick", "the forty niners", "Saint Louis". Letters only when they're said as letters, spaced: "N F L". Accents are spelled plainly ("Maracana") with the name in the dictionary. Digits live only in `cap`, the on-screen caption. The checker fails on any `0-9 % $ & / # @ +`, any all-caps word, abbreviations (`vs`, `St`, `Jr`...) and non-ASCII letters, and suggests the spoken form ("1978" → "nineteen seventy eight").
2. **8 words max per sentence, one action each, punch word last.** Measured on 90 of our sentences: 9+ words got a mid-sentence pause 57% of the time, 8 or fewer 9%. "And" joining two actions almost always breaks the line, so any "and" in a sentence of 4+ words fails (except inside a number, "fourth and twenty five"): write "You turn. You throw it across the field." Put the punch word last, in its own short sentence: "Kick return practice? Barely." Colons only for a deliberate beat, one per line at most; Kokoro always pauses there.
3. **Every name is in `engine/pronunciation.json`.** Any capitalized word in `text` (mid-sentence, or starting a sentence when it isn't an ordinary word from `engine/words.txt`) must be listed: with Kokoro phonemes when espeak reads it wrong, or `"ok"` after you've checked its IPA with `python3 engine/ipa.py <word>` (Kokoro's own espeak-ng; same as `espeak-ng -v en-us -q -x --ipa`). All 32 teams, their cities and every person in the 100 scripts are pre-filled. Names whose real pronunciation isn't confirmed are in `_unsure`: the checker lists them so you listen for them.
4. **Fit: narration fits 60 s at Kokoro speed 1.06 or less.** `tts.py` stops above that and the fix is cutting words, never speeding up. `check.py` estimates the length from letter count so CI catches long scripts before a render.

Before rendering, run `python3 engine/ipa.py videos/<id>` and read every line's phonemes for misread numbers, names or run-together letters. Each pronunciation or cadence problem J reports becomes a checker rule or a dictionary entry, never a one-off fix.
