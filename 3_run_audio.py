"""STEP 3 - runs the full voice pipeline (Gnani STT -> agent -> Gnani TTS) on every clip in the audio_input folder."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "--audio-dir", str(ROOT / "audio_input"), "--out-dir", str(ROOT / "outputs")]
sys.path.insert(0, str(ROOT))
import run  # noqa: E402

run.main()
print("\nOpen the 'outputs' folder: *.reply.wav = spoken reply, results.csv = transcript, reply and document chunks used.")
