#!/usr/bin/env bash
# Review pack for one finished video: a contact sheet (a frame every 2 s), loudness, and format.
#   engine/review.sh out/<set>/<id>.mp4      -> out/<set>/<id>.review.jpg and stats on stdout
set -euo pipefail
F="$1"; S="${F%.mp4}.review.jpg"
ffmpeg -v error -y -i "$F" -vf "fps=1/2,scale=216:-1,tile=6x5" -frames:v 1 "$S"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact=p=0 "$F"
ffmpeg -i "$F" -af ebur128=framelog=quiet -f null - 2>&1 | grep -E "^\s+(I|LRA|Peak):" || true
echo "contact sheet: $S"
