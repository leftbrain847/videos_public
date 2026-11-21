# videos_public

Public repo for J's video channels (`football/` today). Read the channel's `GUIDELINES.md` before writing or rendering a video, and `SECURITY.md` before touching `.github/` or `site/`.

## Working rules for agents (shared across J's repos)

- **Public-safe always.** This repo IS public. No secrets, tokens or personal data anywhere, ever.
- **PRs, never pushes to `main`.** Claude merges once CI is green; J gets a short summary. Hold a PR for J only for decisions CI can't make.
- **Every PR opens with a risk tier and a 60-second check.** First line: `Risk: low | medium | high`. `.github/`, `site/` security headers and anything that changes what's published are high risk and get an independent review first.
- **Actions stay locked down:** SHA-pinned actions, read-only token by default, no `pull_request_target`.
- **Facts in videos are checked against two sources**, listed in each `video.json`.
- **New finished videos:** commit the script, then render by merging a PR that edits `football/render_queue.json` (one new release tag per run, max 16 videos). The render workflow uploads the master (1080x1920, for posting), the web copy (720x1280, CRF 28, for the gallery), poster and contact sheet to that GitHub Release. Then commit the poster (`site/<channel>/posters/<set>/<id>.jpg`) and the release tag in `site/<channel>/releases.json`. Never commit mp4s to git.

## Speech

Capy's voice (Kokoro `af_heart`) says `text` exactly as written. Before writing or editing any script, read "Writing for the voice" in `football/GUIDELINES.md`: spoken words only (no digits, symbols or abbreviations in `text`), 8 words max per sentence, one action each, every name in `football/engine/pronunciation.json`, and the narration must fit 60 s at speed 1.06. Mark rewritten scripts `"voice": "v2"` so `check.py` enforces all of it. A reported mispronunciation becomes a rule or a dictionary entry, never a one-off fix.
