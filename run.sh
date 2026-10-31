#!/usr/bin/env bash
# usage: ./run.sh <audio_dir> [out_dir]
set -euo pipefail
cd "$(dirname "$0")"
python run.py --audio-dir "$1" --out-dir "${2:-outputs}"
