#!/usr/bin/env bash
# Once per session: Python and Node deps, the Kokoro model files (GitHub releases), fonts check.
set -euo pipefail
cd "$(dirname "$0")"
pip install -q --break-system-packages --require-hashes -r requirements.txt
npm ci --no-audit --no-fund
M="${KOKORO_MODELS:-$HOME/.cache/kokoro}"; mkdir -p "$M"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$M/$f" ] || curl -fsSL -o "$M/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
(cd "$M" && sha256sum -c "$OLDPWD/models.sha256") || { echo "Kokoro model checksum mismatch"; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
[ -x "${CHROME:-/opt/pw-browsers/chromium}" ] || echo "WARN: no chromium at /opt/pw-browsers/chromium; set CHROME and PWMOD"
node --check kit.js
echo "engine ready (models in $M)"
