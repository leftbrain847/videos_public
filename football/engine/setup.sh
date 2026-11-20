#!/usr/bin/env bash
# Once per session: Python and Node deps, the Kokoro model files (GitHub releases), fonts check.
set -euo pipefail
cd "$(dirname "$0")"
pip install -q --break-system-packages kokoro-onnx soundfile numpy
npm ci --no-audit --no-fund
M="${KOKORO_MODELS:-$HOME/.cache/kokoro}"; mkdir -p "$M"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$M/$f" ] || curl -sSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
[ -x "${CHROME:-/opt/pw-browsers/chromium}" ] || echo "WARN: no chromium at /opt/pw-browsers/chromium; set CHROME and PWMOD"
node --check kit.js
echo "engine ready (models in $M)"
