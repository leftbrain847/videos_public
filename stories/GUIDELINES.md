# stories: five 90-second story series narrated by Capy

Same engine, layout and voice as football (`football/GUIDELINES.md` and `football/RUBRIC.md` apply in full): split screen with the story on top and a Disk Football reel below, Kokoro `af_heart`, captions, the "Writing for the voice" rules. Differences:

- **Length: 90 s.** Set `"target_s": 90`. The checker scales its limits to it: 15–27 lines, 203–258 spoken words, Capy in 7+ shots.
- **Ids:** `stories/videos/<series>_<nn>_<slug>/video.json`, with `nn` from 01 to 32.
- **Release tags:** `stories-<series>-1` (videos 01–16) and `stories-<series>-2` (17–32). One series per tag, so each series can be grabbed and posted as a group.
- **Every series is true.** Real events, real people and real science, with 2 sources per claim, checked by CI exactly like football. That includes `scary`.
- **Tone is the channel's.** Open on "you" (the viewer is in the story). Capy's dry, petty roast in a calm delivery. Tease bad decisions, never a real person's character. No gore and no mocking victims. One moment per video worth sending to a friend, and end on a comment question.

| Series | Capy outfit | Default set | What it is | Structure |
|---|---|---|---|---|
| `scary` | `raincoat` (flashlight) | `haunted` | True eerie events: unexplained disappearances, strange signals, haunted-place history, odd ships and lighthouses. Nothing gory. | Absurd/Heist: the setup, the wrong detail, it escalates, what's still unexplained |
| `heist` | `detective` (magnifier) | `vault` | Real heists, cons and frauds, told from the planner's side: Antwerp diamonds, the Mona Lisa theft, D. B. Cooper, Frank Abagnale's claims (and the doubts). | Heist: the target, the plan, the one flaw, the twist |
| `myth` | `toga` | `temple` | Myths and legends from many cultures, as what the stories actually say. Sources are encyclopedias and museum pages. | Heist or Absurd: a god's bad decision and its consequences |
| `space` | `astronaut` | `space` | True space and science stories: missions, near-disasters, strange objects, the weirdest numbers. | Heist (missions) or Absurd (facts) |
| `mind` | `cardigan` (notepad) | `study` | Psychology: famous studies and effects (Milgram, Stanford Prison, the marshmallow test, the bystander effect), including what replications found. | Loophole: the experiment, the twist, what it says about you |

**Sets** (`setOpts.boardText` puts a title on each set's sign): `haunted`, `vault`, `temple`, `space` and `study`, plus all the football sets. **People outfits:** `robe` (myth; give it `sash`), `spacesuit`, `coat`, `suit`, `tee`, `hoodie`, `polo`. **New props:** `flashlight`, `magnifier`, `notepad`, `goldbar`, `bag`, `candle`, `scroll`, `lyre`.

**Original characters only.** No copyrighted characters and no real person's likeness beyond a generic bean with a name tag in the caption. Mythological figures are public domain, but draw them as our beans, not as any film's design.
