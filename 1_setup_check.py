"""STEP 1 - press the Run (play) button on this file. It installs what is missing and tells you what to fix."""
import importlib, importlib.util, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import voiceops  # noqa: F401  (sets UTF-8 console)

NEED = {"anthropic": "anthropic", "openai": "openai", "gnani": "gnani-vachana", "requests": "requests", "dotenv": "python-dotenv", "flask": "flask"}
ok = lambda m: print(f"  [OK]   {m}")
bad = lambda m: print(f"  [FIX]  {m}")

print(f"Python {sys.version.split()[0]} ({sys.executable})")
missing = [pip for mod, pip in NEED.items() if importlib.util.find_spec(mod) is None]
if missing and not os.getenv("VOICEOPS_SKIP_INSTALL"):
    print("Installing:", ", ".join(missing))
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        importlib.invalidate_caches()
        missing = [pip for mod, pip in NEED.items() if importlib.util.find_spec(mod) is None]
    except Exception:
        pass
if missing:
    bad(f"could not install {missing}. In VS Code: Ctrl+Shift+P -> 'Python: Create Environment' -> Venv -> tick requirements.txt, then run this again.")
else:
    ok("all packages installed")

from voiceops import config  # noqa: E402

try:
    d = config.find_dataset_dir()
    ok(f"dataset found: {d}")
    from voiceops.kb import load_kb_chunks
    ok(f"knowledge base loaded: {len(load_kb_chunks())} sections")
except FileNotFoundError:
    bad("dataset not found. Unzip Capstone_Project_Dataset_FTTT_2026.zip INTO this project folder (so you see a folder named "
        "Capstone_Project_Dataset_FTTT_2026 next to run.py).")

env = ROOT / ".env"
if not env.exists():
    bad("no .env file yet. In the VS Code Explorer: right-click '.env.example' > Copy, paste it, rename the copy to '.env', then paste your keys inside.")
llm_key = "OPENAI_API_KEY" if os.getenv("LLM_PROVIDER", "anthropic").lower() == "openai" else "ANTHROPIC_API_KEY"
for key, what in ((llm_key, "LLM answers"), ("GNANI_API_KEY", "voice (speech-to-text / text-to-speech)")):
    (ok if os.getenv(key) else bad)(f"{key} {'set' if os.getenv(key) else 'missing -> needed for ' + what}")

print("\nTesting the LLM with one tiny request ...")
try:
    from voiceops.llm import LLM
    _l = LLM()
    if not _l.available:
        bad("LLM client not available (check LLM_PROVIDER / key in .env)")
    else:
        _r = _l.complete("Reply with the single word OK.", [{"role": "user", "content": "ping"}], max_tokens=50)
        ok(f"LLM works: model '{_l.model}' answered: {_r.strip()[:40]!r}")
        if _l.model != config.LLM_MODEL:
            bad(f"add this line to .env so it is permanent:  LLM_MODEL={_l.model}")
except Exception as exc:
    bad(f"LLM call failed -> {exc}")
    print("      Gemini: key must be from Google AI Studio; .env needs LLM_PROVIDER=openai, OPENAI_API_KEY=<key>, "
          "OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ and LLM_MODEL=gemini-flash-latest")

print("\nDone. Next: Run and Debug panel -> '2 - Evaluate (Step 1 vs Step 2)'.")
