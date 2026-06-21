#!/usr/bin/env bash
# Render the participant reference guide (reference_guide.html) to a print-quality PDF using
# headless Chrome. Run from the repo root:  bash build/make_pdf.sh
# Prereqs: the light-theme charts must exist first (python3 build/make_print_figs_textspeech.py).
set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || true)"
[ -n "$CHROME" ] || { echo "No Chrome/Chromium found"; exit 1; }

"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --user-data-dir=/tmp/chrome_pdf_profile \
  --virtual-time-budget=15000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="$(pwd)/Predictive-AI-Field-Guide.pdf" \
  "file://$(pwd)/reference_guide.html"

echo "wrote Predictive-AI-Field-Guide.pdf"
