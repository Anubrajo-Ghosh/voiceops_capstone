# ZentroMart VoiceOps agent - VoiceOps 2026 capstone

A support agent that answers from ZentroMart's documents, holds a conversation, uses `lookup_order` /
`create_ticket`, and listens and speaks through **Gnani STT/TTS only**.
No terminal is needed: everything below uses VS Code buttons.

## A. One-time setup (about 10 minutes)

1. **Open the project**: VS Code -> File -> Open Folder -> pick this `voiceops` folder. Click "Install" if VS Code
   suggests the Python extension.
2. **Add the dataset**: unzip `Capstone_Project_Dataset_FTTT_2026.zip` and drag the folder
   `Capstone_Project_Dataset_FTTT_2026` into this project (it must sit next to `run.py`). It is git-ignored, so it will
   not be uploaded.
3. **Create a Python environment**: press `Ctrl+Shift+P` -> `Python: Create Environment` -> `Venv` -> tick
   `requirements.txt` -> OK. (Wait for it to finish.)
4. **Add your keys**: in the Explorer, right-click `.env.example` -> Copy, then paste, and rename the copy to `.env`.
   Open `.env` and paste your keys after `GNANI_API_KEY=` and `ANTHROPIC_API_KEY=`. Keys live only in `.env`
   (git-ignored), never in the code. Using a different LLM? See the comments inside `.env.example`.
5. **Check**: left bar -> Run and Debug (play icon with a bug) -> choose **1 - Setup check** -> green play button.
   Fix anything it marks `[FIX]`.

## B. Daily workflow (pick from the Run and Debug dropdown, press the green play button)

| Button | What it does |
| --- | --- |
| **2 - Evaluate (Step 1 vs Step 2)** | Scores prompt-only vs RAG on the 52 practice questions, plus conversations and retrieval. Saves `sample_outputs/eval_summary.md`: copy these numbers into the report |
| **3 - Run agent on audio_input** | Full voice pipeline on every clip you drop into `audio_input/`. Results in `outputs/` (reply text, reply audio, retrieved chunks) |
| **4 - Demo web app** | Opens a hold-to-talk page in your browser. Use it with a screen recorder for the 2-minute demo |
| **Unit tests** | 10 offline tests |
| **Build submission zip** | Creates `<team>_voiceops.zip` (edit `TEAM_NAME` at the top of `make_submission.py` first) |

Recording clips: any phone voice recorder is fine; each clip under 30 seconds. English, Hindi and Hinglish all work.
Say order IDs digit by digit.

## C. Upload to GitHub (still no terminal)

1. Left bar -> **Source Control** (branch icon) -> **Initialize Repository** -> **Publish to GitHub** -> choose
   **public** -> sign in when asked.
2. Untick nothing: `.gitignore` already blocks `.env`, `.venv`, the dataset, `outputs/` and zip files.
3. Open the published repo on github.com and confirm there is **no `.env`** and no dataset folder. Paste its URL
   below and in your report.

GitHub URL: `[<paste here>](https://github.com/Anubrajo-Ghosh/voiceops_capstone)`

## D. Final submission

Put `report.pdf` (from `REPORT_TEMPLATE.md`) and `demo.mp4` in this folder, then run **Build submission zip**.

## How it works (for the report)

```
audio -> Gnani STT -> ASR cleanup -> verification state machine -> facts engine (dates, windows, fees, ESC-1)
      -> hybrid retrieval over KB sections -> LLM (grounded JSON reply) -> guardrails -> Gnani TTS -> spoken reply
```

| Module (`src/voiceops/`) | Job |
| --- | --- |
| `kb.py`, `retrieval.py` | Section-level chunks with ids; BM25 + Hindi/Hinglish glossary; policy > guide > help > FAQ > marketing precedence; superseded docs down-weighted; optional dense fusion (`USE_DENSE=1`) |
| `textnorm.py` | Spoken digits to IDs ("ele-zero zero one to" = ELE-0012), dates, payment method, language |
| `calendar_utils.py`, `facts.py` | All arithmetic in code: business days, refund ETAs, return windows incl. v3 legacy and festive sale, Rs 49 fee, warranty/Assured, ESC-1 triggers |
| `agent.py` | Session state, verification (one retry, then locked), tickets only claimed when `created=True`, guardrails against false action claims, AI introduction on first reply |
| `voice.py`, `speechfmt.py` | Gnani STT (Prisma v3.0 `indic-auto`, SDK fallback) and TTS (`timbre-v2.5`, named explicitly); replies written for the ear |

Batch command for the organisers (same code the button runs): `python run.py --audio-dir <folder> --out-dir outputs`.
Notes: Gnani STT clips are limited to 30 s (long WAVs are auto-split); accounts allow one active STT request at a time.
