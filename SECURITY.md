# Security

This repo is public on purpose: its Actions run free and the gallery is served by GitHub Pages. It holds no secrets and needs none.

- **No secrets in the repo or in Actions.** Workflows use only the built-in `GITHUB_TOKEN`, read-only by default; the Pages deploy job alone gets `pages: write` and `id-token: write`.
- **Pinned actions.** Every action is pinned to a full commit SHA (the tag is in a comment). Update by changing the SHA, never to a floating tag.
- **No `pull_request_target`, no self-hosted runners**, checkout without persisted credentials.
- **Gallery page:** loads nothing from other origins (CSP `default-src 'self'`), writes data only with `textContent`, links only to https sources with `noopener noreferrer`.
- Report a vulnerability privately with GitHub's **Report a vulnerability** button (Security tab, private vulnerability reporting); never with exploit details in a public issue.
