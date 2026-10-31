"""LAST STEP - builds <team>_voiceops.zip with only the allowed files (no .env, no venv, no dataset copy).

Put report.pdf and demo.mp4 in this folder first. Edit TEAM_NAME below, then press Run."""
import zipfile
from pathlib import Path

TEAM_NAME = "team_name"   # <-- change this

ROOT = Path(__file__).resolve().parent
INCLUDE = ["README.md", ".env.example", "requirements.txt", "run.py", "run.sh", "report.pdf", "demo.mp4",
           "src", "sample_outputs", "eval", "tests", "demo_app.py", "1_setup_check.py", "2_evaluate.py", "3_run_audio.py", "4_demo_app.py"]
SKIP = {"__pycache__", ".venv", ".git", "outputs", ".env"}

out = ROOT / f"{TEAM_NAME}_voiceops.zip"
n = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name in INCLUDE:
        p = ROOT / name
        if not p.exists():
            print(f"  [missing] {name}" + ("  <- the organisers require this" if name in ("report.pdf", "demo.mp4") else ""))
            continue
        for f in ([p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())):
            if SKIP & set(f.relative_to(ROOT).parts) or f.suffix == ".pyc":
                continue
            z.write(f, f.relative_to(ROOT).as_posix()); n += 1
print(f"\nCreated {out.name} with {n} files. Check it contains NO .env or keys before uploading.")
