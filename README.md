# videos_public

J's public video channels: the code that makes them, every script with its sources, and a gallery on GitHub Pages. Public on purpose so Actions and Pages run free; it holds no secrets (see `SECURITY.md`). Full-resolution masters stay in the private `videos` repo.

**Watch:** https://leftbrain847.github.io/videos_public/

| Channel | Folder | Gallery |
| --- | --- | --- |
| Capy's football shorts | `football/` | `site/football/` |

## Football shorts
60-second football stories hosted by **Capy**, a calm capybara referee: the story plays on top in smooth low-poly 3D, Disk Football highlights below, narration by Kokoro `af_heart`, music by the Comprehensible Input piano piece.
- `football/GUIDELINES.md`: script, accuracy, motion, play and sound rules.
- `football/videos/<id>/video.json`: each script with its sources; `football/engine/check.py` validates them.
- `football/engine/`: `bash setup.sh`, then from `football/`: `bash engine/make.sh videos/<id> <n>` → `out/<set>/<id>.mp4`.

**Credits:** piano sampled from Salamander Grand Piano V3 by Alexander Holm (CC BY 3.0). Inter font (SIL OFL). Narration voice: Kokoro (Apache 2.0).
