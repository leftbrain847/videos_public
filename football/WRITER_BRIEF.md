# Writer brief: football shorts scripts (voice v2)

Give this file to each writer agent with its letter, its own clone directory, and its list of video ids (see PLAYBOOK.md).
Written for unattended runs: nobody answers questions or permission prompts.

Repo: leftbrain847/videos_public (public). You work only in your own clone of it. Push with git, use `gh api` (REST only; GraphQL
and `gh pr create` are blocked) for PRs/merges/CI. Never touch .github/, site/, football/render_queue.json, engine code, or app_builder.

## Read first (in this order)
CLAUDE.md (root: Speech section), football/GUIDELINES.md (esp. "Writing for the voice"), football/RUBRIC.md, football/engine/check.py,
tools/fact_check.py (claims format), and 3 finished v2 examples: football/videos/s4_25_seven_nine_champs, s4_01_music_city_miracle,
s1_02_holy_roller. Match their quality and structure exactly.

## Each video you're assigned: rewrite football/videos/<id>/video.json to v2
- Tone (locked by J): open on "you" (viewer is the player/coach/team), Capy's dry petty roast, calm. Tease fan bases and bad calls,
  never a real person's character. Structure by story type: Heist (plays), Loophole (rules), Absurd (oddities). One moment per video
  people would send to a friend. End with a comment-prompt question.
- "voice": "v2" and pass `python3 football/engine/check.py football/videos/<id>/` with zero failures (strict): spoken words only in
  `text` (digits only in `cap`), max 8 words per sentence, one action each, punch word last, every capitalized name in
  football/engine/pronunciation.json (check espeak: `espeak-ng -v en-us -q -x --ipa "<word>"`; add a phoneme override if wrong,
  else mark it ok as the file's existing entries do), fits 60 s at speed <= 1.06 (run `python3 football/engine/tts.py
  football/videos/<id> --models /home/claude/work/models` to confirm the speed it needs).
- NEVER call WebFetch (it needs a permission nobody will answer tonight and you will hang). WebSearch only.
- Facts: every factual statement in `text` has a `claims` entry with `terms` (see fact_check.py docstring). Sources: https URLs from
  reputable outlets (Wikipedia, AP, ESPN, NFL.com, team sites, major papers); give 3-5 so two still support each claim if one dies.
  You cannot fetch pages here; CI does. Use WebSearch to find real URLs and confirm the facts. A claim you can't support: cut it.
- Visuals: keep the existing cast/sets/shots/plays where they fit; adjust `place`, `act`, `shot` per line so the picture shows what's
  said. Rules from review history: people at least 2 units apart, everyone at z <= 6, runs <= 12 units/s, the play is shown on the field,
  no 3 identical shot types in a row, Capy on screen at least 5 lines. Spot-check with
  `cd football && node engine/render.mjs videos/<id> --stills 2,15,30,45 --draft` (outputs videos/<id>/build/still_*.jpg; Read them)
  only when you changed a play; it costs ~1-2 min.

## Shipping (push as you go; work must survive if you're cut off)
- Every 3-5 finished videos: `git fetch origin && git rebase origin/main` (pronunciation.json conflicts: keep both sides' entries),
  push a branch `claude/v2-<your-letter>-<n>`, open a PR via
  `gh api repos/leftbrain847/videos_public/pulls -f title=... -f head=... -f base=main -F body=@file`
  Body first line "Risk: low", then a 3-line 60-second check (which videos, anything odd), end with:
  "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nhttps://claude.ai/code/session_01VWC6vDbFH78qHzFBPZRXbh"
  Commits end with:
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01VWC6vDbFH78qHzFBPZRXbh"
- Wait for CI (poll every ~3 min: `gh api repos/leftbrain847/videos_public/commits/<branch>/check-runs`). Jobs `check` and `facts`.
  If facts fails, read its log: `gh api repos/leftbrain847/videos_public/actions/jobs/<job id>/logs` (lines starting FAIL), fix terms
  (they must literally appear near each other on the page; digits as the page writes them, e.g. "34-28"), swap sources, or cut the
  claim. Max 3 rounds per PR; then drop the still-failing videos from the PR (revert those files) and list them in your final report.
- When both checks pass, merge: `gh api -X PUT repos/leftbrain847/videos_public/pulls/<n>/merge -f merge_method=squash`.
- Then continue with the next videos. Don't wait for anyone.

## Final report (under 150 words)
Merged video ids, blocked ids with the reason, new pronunciation entries, EVERY claim you cut (J reviews these), and anything a human should look at.
