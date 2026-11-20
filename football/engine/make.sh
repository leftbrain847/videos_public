#!/usr/bin/env bash
# One video end to end: check -> narration -> stills -> story render -> gameplay reel -> final mp4.
#   engine/make.sh videos/<id> <index>          (run from football/)
# Stills land in videos/<id>/build/ for review; the final mp4 goes to out/<set>/<id>.mp4.
set -euo pipefail
cd "$(dirname "$0")/.."
VD="$1"; IDX="${2:-0}"; ID="$(basename "$VD")"; SET="${ID%%_*}"
MODELS="${KOKORO_MODELS:-$HOME/.cache/kokoro}"
python3 engine/check.py "$VD"
python3 engine/tts.py "$VD" --models "$MODELS"
STILLS=$(python3 -c "import json;t=json.load(open('$VD/build/timing.json'));print(','.join(str(round((l['start']+l['end'])/2,1)) for l in t['lines']))")
node engine/render.mjs "$VD" --stills "$STILLS"
node engine/render.mjs "$VD"
python3 engine/highlights.py "$VD" --index "$IDX"
[ -s engine/audio/sfx/whistle.wav ] || python3 engine/sfx.py
python3 engine/mix.py "$VD"
mkdir -p "out/$SET"
python3 engine/compose.py "$VD" --out "out/$SET/$ID.mp4"
