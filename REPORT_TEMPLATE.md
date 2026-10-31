# VoiceOps 2026 - Report (max 4 pages)  [fill the <> from your own runs]

## 1. Step 1 - prompt-only LLM
Model <name>; system prompt in `src/voiceops/prompts.py::SYSTEM_BASELINE`. Practice questions passed: **<n>/52** (`python eval/question_eval.py step1`).
Typical failures: invented windows / refund times, ignored the Rs 49 fee, no business-day maths, FAQ-style "5 to 7 days".

## 2. Step 2 - RAG
Chunking by section id; BM25 + Hindi/Hinglish glossary (+ dense: <yes/no>); precedence weighting; computed facts.
Practice questions passed: **<n>/52** (Step 1 -> Step 2: <+x>). Retrieval recall@5 (gold evidence): **<x%>** (`eval/retrieval_eval.py`).
Offline reference (rule-only, no LLM; tuned on the practice set, so optimistic): 52/52 questions, 96/96 conversation turns (tools, decisions, must-include).

## 3. Step 3 - conversation
Verification state machine (one retry, then locked), coreference via session focus item, deferred question answered after verification,
ESC-1 floor + tickets (only claim handover on created=True), refusals (compensation, shipped cancellation, other customers' data).
Practice conversations: tools <n>/96, decisions <n>/96, must-include <n>/96 (`eval/conv_eval.py`).

## 4. Step 4 - voice
Gnani STT Prisma v3.0 `indic-auto` (SDK v2.5 fallback), TTS timbre-v2.5 with en/hi/Hinglish voices, replies written for the ear.
Tested with my own recordings: <n clips, languages, observed WER issues, unclear-audio recovery>.

## 5. What went wrong / what I would fix
<ASR on order IDs, Hinglish retrieval without a multilingual embedder, latency (STT+2 LLM calls+TTS), ...>

## 6. Bonus
<dense retrieval fusion, web demo, ...>
