# PLAYBOOK: making a batch of videos without J in the loop

This is how 74 scripts were written and 100 videos rendered, checked and released overnight on 2026-11-20, with J asleep. An earlier attempt with the same goal produced nothing in 10 hours. Follow this file in order; everything here was learned the hard way.

## Roles
- **Orchestrator (you, the main session).** You write nothing yourself except fixes. You launch writers, merge queue PRs, watch renders, sweep contact sheets, and log timings in a timelog. Stay in your turn while work runs: long `sleep` + check loops of 5–10 minutes. If your turn ends, nothing coordinates.
- **Writers (background agents, fresh context).** At most 4 in parallel, each with its own `git clone` (worktree isolation may be denied) and 12–25 videos. They follow `football/WRITER_BRIEF.md`, push a PR every 3–5 videos, and merge their own PRs once `check` and `facts` are green.
- **Reviewers (fresh agents).** Required for every `.github/` or `site/` change: a short, specific prompt, a verdict and file:line fixes.

## The pipeline (all on GitHub, no human taps)
1. A script PR runs CI: `check` (strict script rules) and `facts`. Facts opens every source and needs 2 sources per claim.
2. Merge. Then a PR editing `football/render_queue.json` queues a render. Merging it starts `render.yml` through the push trigger, because Claude's token gets a 403 on `workflow_dispatch`.
3. Render: **at most 16 videos per run** (`max-parallel: 16`), so a batch is one wave and 4 of the 20 free runners stay open for PR checks. Use **one new release tag per run** (`football-batch-<n>`); two runs on one tag race.
4. Release gate is per video. A failed claim holds back only its own video (`tools/release_filter.py`).
5. Gallery: add posters plus `site/<channel>/releases.json` (id to tag) in one PR. Never commit mp4s.

## Gates
- **Before scaling:** one video (or one batch) goes end to end: script, facts, render, release, then you look at it.
- **Every video:** look at its contact sheet (`<id>.review.jpg` in the release). Fast way: crop the story rows of 4 sheets into one image, about 1.5k tokens each, so 100 videos is about 25 images. Tonight's sweep found 5 broken videos that every automated check passed:
  - camera inside an arm or a scrum (`low` shot inside a crowd);
  - `follow_high` on the ball ending on an empty end zone;
  - an over-the-shoulder shot blocked by Capy's head.

  Fix the shot, check stills, and re-render into `football-batch-fixes`.
- **Listen-back:** most flags are speech-to-text noise (plurals, compounds). Act only on names actually said wrong.

## Hard rules for agents
- **Never call WebFetch in a writer.** It prompts for permission, nobody answers at night, and the writer hangs forever. Writers use WebSearch; CI opens the pages.
- **`git push -f` is refused** by the permission classifier. Use fresh branches or cherry-picks.
- **Deleting scheduled tasks is refused**; that's fine. Schedule 2–3 one-shot wake-ups (`send_later`) as a backstop in case your turn ends.
- **Every human message interrupts** the running step, and has killed background writers. Before J sleeps, tell him: no messages until morning.
- **Plan for the 5-hour usage limit.** When it hits, every background agent dies mid-work, leaving PRs half-fixed. Afterwards, don't resume the dead writers (each resume replays a 300–580k context). Start one small fixer per series with a short brief: merge main into each open PR, swap dead sources, merge when green. Three fixers cleared 12 PRs in about 30 min for ~150k tokens each.
- **Only one render run at a time.** Detect a running render through `actions/workflows/render.yml/runs`, never through the last N runs of all workflows: busy PR checks push the render off that list and a second batch slips in.
- **Look at job conclusions, not just the release.** A release can hold all 16 videos while every listen-back job failed (2026-11-21: `upload-artifact` refuses paths containing `..`; story folders are now passed as repo-root paths).
- **Ask everything up front** (permissions, publishing, budget), then run with no further questions.

## Timings to expect (2026-11-21)
| Step | Time |
|---|---|
| One render job (free runner) | 25–50 min |
| A 16-video batch | ~50 min |
| A 20-video batch | ~75 min (two waves; don't) |
| One writer, 12–25 scripts including facts rounds | 65–75 min |
| A PR check (`check` + `facts`) | 3–5 min when runners are free; up to 20 min when renders hold them |
| 100 videos, scripts already written | ~4 h of wall clock, runner-bound |

## Known gaps
- The facts check proves words appear near each other on a page, not that a claim is true. It also rewards cutting true claims that have only one source. Writers list every cut claim in their report, and the orchestrator passes them to J.
- New on-field plays cause most broken frames. Writers should render one draft of each new play, not just stills.
- **Sources CI can't open.** Many news sites answer CI with 403 (paywalls, bot walls), Gutenberg sometimes with 503. Prefer Wikipedia (check the exact title), .gov/.edu, NASA/ESA and museum pages. A writer's sandbox can't reach the sites either, so CI's facts run is the only check.
- **Contact-sheet sweep findings (stories, 2026-11-21):** writers faked an animal with a person (Clever Hans as a dark-skinned human: never again; use `kind: "horse"` from kit.js `ANIMALS`, or keep the animal off screen), and `ots` shots framed the back of a head (now banned for story series in check.py).
- Gameplay variety: all reels come from 2 capture sessions.

## Standard for new series (decided 2026-11-21)
New series run **90 seconds** (`TIMING.target_s` in `football/engine/tts.py`; word limits in `check.py` scale with it). Capy stays the narrator, in an outfit matching the series theme.
