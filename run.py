#!/usr/bin/env python
"""Batch run for the organisers.

    python run.py --audio-dir <folder with customer audio> --out-dir outputs

For every audio file: Gnani STT -> agent (RAG + tools) -> Gnani TTS. Saves, per file,
  <stem>.reply.txt   the reply text
  <stem>.reply.wav   the spoken reply
and one results.jsonl / results.csv with transcript, reply, decision, tool calls and the retrieved
document chunks (id, title, text) the answer was grounded on.

Each file is an independent customer (fresh session). Use --group-conversations to treat files named
<conversation>_<turn>.<ext> (e.g. PC002_t1.wav, PC002_t2.wav) as turns of one conversation.
--text-only reads .txt transcripts instead of audio and skips TTS (offline testing, no Gnani key).
"""
import argparse, csv, json, os, re, sys, traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from voiceops.agent import Agent  # noqa: E402
from voiceops.kb import chunk_by_id  # noqa: E402
from voiceops.voice import AUDIO_EXT, DIDNT_CATCH, Voice, voice_turn  # noqa: E402


def chunk_payload(ids):
    out = []
    for cid in ids:
        c = chunk_by_id(cid)
        out.append({"id": cid, "title": c.title if c else "", "text": c.text if c else ""})
    return out


def group_files(files, grouping):
    if not grouping:
        return [[f] for f in files]
    groups = {}
    for f in files:
        m = re.match(r"^(?P<c>.+?)[_-]t?(?P<n>\d+)$", f.stem)
        groups.setdefault(m.group("c") if m else f.stem, []).append((int(m.group("n")) if m else 0, f))
    return [[f for _, f in sorted(v)] for _, v in sorted(groups.items())]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-dir", default="audio_input")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--group-conversations", action="store_true")
    ap.add_argument("--text-only", action="store_true")
    a = ap.parse_args()

    src, out = Path(a.audio_dir), Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    exts = {".txt"} if a.text_only else AUDIO_EXT
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in exts)
    if not files:
        sys.exit(f"no {'.txt' if a.text_only else 'audio'} files in {src}")
    agent, voice = Agent(), (None if a.text_only else Voice())
    rows = []
    for group in group_files(files, a.group_conversations):
        agent.reset()
        for f in group:
            wav = out / f"{f.stem}.reply.wav"
            row = {"file": f.name, "ok": True}
            try:
                if a.text_only:
                    rep = agent.respond(f.read_text(encoding="utf-8"))
                    row.update(heard=f.read_text(encoding="utf-8").strip(), reply=rep.text, spoken=rep.spoken, lang=rep.lang,
                               decision=rep.decision, chunks=rep.chunks, tool_calls=rep.tool_calls, ticket=rep.ticket)
                else:
                    row.update(voice_turn(f, agent, voice, wav))
                row["reply_audio"] = wav.name if not a.text_only else ""
            except Exception as exc:  # never crash the batch: always leave a reply for the file
                traceback.print_exc()
                row.update(ok=False, error=str(exc), heard="", reply=DIDNT_CATCH["en"], spoken=DIDNT_CATCH["en"], lang="en",
                           decision="clarify", chunks=[], tool_calls=[], ticket=None, reply_audio="")
                if voice:
                    try: voice.synthesize(DIDNT_CATCH["en"], "en", wav); row["reply_audio"] = wav.name
                    except Exception: pass
            row["retrieved_chunks"] = chunk_payload(row["chunks"])
            (out / f"{f.stem}.reply.txt").write_text(row["reply"] + "\n", encoding="utf-8")
            rows.append(row)
            print(f"[{f.name}] {row['decision']}: {row['reply'][:90]}")
    with open(out / "results.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    with open(out / "results.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "heard", "reply", "decision", "language", "chunk_ids", "tool_calls", "reply_audio"])
        for r in rows:
            w.writerow([r["file"], r["heard"], r["reply"], r["decision"], r["lang"], ";".join(r["chunks"]),
                        json.dumps(r["tool_calls"], default=str), r["reply_audio"]])
    print(f"done: {len(rows)} file(s) -> {out}")


if __name__ == "__main__":
    main()
