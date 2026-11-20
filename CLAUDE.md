# videos_public

Public repo for J's video channels (`football/` today). Read the channel's `GUIDELINES.md` before writing or rendering a video, and `SECURITY.md` before touching `.github/` or `site/`.

## Working rules for agents (shared across J's repos)

- **Public-safe always.** This repo IS public. No secrets, tokens or personal data anywhere, ever.
- **PRs, never pushes to `main`.** Claude merges once CI is green; J gets a short summary. Hold a PR for J only for decisions CI can't make.
- **Every PR opens with a risk tier and a 60-second check.** First line: `Risk: low | medium | high`. `.github/`, `site/` security headers and anything that changes what's published are high risk and get an independent review first.
- **Actions stay locked down:** SHA-pinned actions, read-only token by default, no `pull_request_target`.
- **Facts in videos are checked against two sources**, listed in each `video.json`.
- **New finished videos:** commit the script, add the web copy (`site/<channel>/media/<set>/<id>.mp4`, 720x1280, CRF 28) and poster (`site/<channel>/posters/<set>/<id>.jpg`, frame at 1.5 s, 360x640). Full-resolution masters go to the private `leftbrain847/videos` repo.

## Speech

Capy's voice (Kokoro `af_heart`) says `text` exactly as written. Before writing or editing any script, read "Writing for the voice" in `football/GUIDELINES.md`: spoken words only (no digits, symbols or abbreviations in `text`), 8 words max per sentence, one action each, every name in `football/engine/pronunciation.json`, and the narration must fit 60 s at speed 1.06. Mark rewritten scripts `"voice": "v2"` so `check.py` enforces all of it. A reported mispronunciation becomes a rule or a dictionary entry, never a one-off fix.
