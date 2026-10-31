"""STEP 2 - runs every evaluation and saves the numbers for your report to sample_outputs/eval_summary.md."""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import voiceops  # noqa: F401, E402
from voiceops import config  # noqa: E402
from voiceops.llm import LLM  # noqa: E402

has_llm = LLM().available
jobs = [("Retrieval recall (gold evidence, no LLM needed)", ["eval/retrieval_eval.py"]),
        ("Step 2 - RAG agent on 52 practice questions", ["eval/question_eval.py", "step2"]),
        ("Practice conversations (96 turns)", ["eval/conv_eval.py"])]
if has_llm:
    jobs.insert(1, ("Step 1 - prompt-only LLM on 52 practice questions", ["eval/question_eval.py", "step1"]))
else:
    print("No LLM key found -> Step 1 is skipped and Step 2 runs in rule-only mode. Add ANTHROPIC_API_KEY to .env for the real numbers.\n")
    os.environ["LLM_PROVIDER"] = "none"

lines = ["# Evaluation summary", "", f"LLM: {'%s (%s)' % (config.LLM_PROVIDER, config.LLM_MODEL) if has_llm else 'none (rule-only fallback)'}", ""]
for title, cmd in jobs:
    print(f"== {title}")
    out = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                         env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    txt = (out.stdout + out.stderr).strip()
    print(txt[-1500:], "\n")
    last = [l for l in txt.splitlines() if re.search(r"pass|turns=|recall", l)]
    lines += [f"## {title}", "", "```", *(last[-3:] or [txt[-300:]]), "```", ""]
(ROOT / "sample_outputs").mkdir(exist_ok=True)
(ROOT / "sample_outputs" / "eval_summary.md").write_text("\n".join(lines), encoding="utf-8")
print("Saved sample_outputs/eval_summary.md  <- copy these numbers into your report")
