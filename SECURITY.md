# Security

This repo is public on purpose: its Actions run free and the gallery is served by GitHub Pages. It holds no secrets and needs none.

- **No secrets in the repo or in Actions.** Workflows use only the built-in `GITHUB_TOKEN`, read-only by default; the Pages deploy job alone gets `pages: write` and `id-token: write`.
- **Pinned actions.** Every action is pinned to a full commit SHA (the tag is in a comment). Update by changing the SHA, never to a floating tag.
- **No `pull_request_target`, no self-hosted runners**, checkout without persisted credentials.
- **Render workflow (`render.yml`):** `workflow_dispatch` only, no secrets, read-only token in every job except `release`, which gets `contents: write` only to create a GitHub Release and upload files to it (it never commits or pushes). The one free-text input, video ids, reaches shell only through env vars after `tools/render_plan.py` checks each id against a strict pattern and the videos folder; the release tag must match `football-batch-*`. Kokoro models come from the kokoro-onnx GitHub release and must match `football/engine/models.sha256`; Python deps install with `--require-hashes` from fully locked files, npm deps from `package-lock.json`. The listen-back speech-to-text model (Hugging Face) runs in its own read-only job that never touches the released files. The fact check prints only pass/fail and at most 15 words per source, never page text.
- **Gallery videos** play from this site or from this repo's GitHub Releases only: the CSP `media-src` allows `github.com` and `release-assets.githubusercontent.com`, and `app.js` drops any other video URL.
- **Gallery page:** loads nothing from other origins (CSP `default-src 'self'`), writes data only with `textContent`, links only to https sources with `noopener noreferrer`.
- Report a vulnerability privately with GitHub's **Report a vulnerability** button (Security tab, private vulnerability reporting); never with exploit details in a public issue.
