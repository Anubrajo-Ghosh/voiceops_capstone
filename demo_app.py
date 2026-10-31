#!/usr/bin/env python
"""Browser demo: press the mic, speak, hear ZentroMart's reply.  python demo_app.py  ->  http://localhost:7860

The page records the microphone, converts it to 16 kHz mono WAV in the browser (Gnani accepts WAV),
posts it to /api/turn (Gnani STT -> agent -> Gnani TTS) and plays the returned audio. A text box
(/api/text) lets you test the agent without a microphone or Gnani key.
"""
import base64, os, sys, tempfile, uuid
from pathlib import Path
from flask import Flask, jsonify, request

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from voiceops.agent import Agent
from voiceops.kb import chunk_by_id
from voiceops.voice import Voice, voice_turn

app = Flask(__name__)
SESSIONS: dict[str, Agent] = {}
VOICE = None


def session(sid):
    if sid not in SESSIONS:
        SESSIONS[sid] = Agent()
    return SESSIONS[sid]


def payload(rep_dict):
    rep_dict["retrieved"] = [{"id": i, "title": (chunk_by_id(i).title if chunk_by_id(i) else "")} for i in rep_dict.get("chunks", [])]
    return rep_dict


@app.post("/api/turn")
def turn():
    global VOICE
    VOICE = VOICE or Voice()
    sid = request.form.get("sid", "default")
    f = request.files["audio"]
    tmp = Path(tempfile.gettempdir()) / f"{uuid.uuid4().hex}.wav"
    f.save(tmp)
    out = tmp.with_suffix(".reply.wav")
    r = voice_turn(tmp, session(sid), VOICE, out)
    r["audio_b64"] = base64.b64encode(out.read_bytes()).decode()
    return jsonify(payload(r))


@app.post("/api/text")
def text():
    sid = request.json.get("sid", "default")
    rep = session(sid).respond(request.json["text"])
    return jsonify(payload({"heard": request.json["text"], "reply": rep.text, "spoken": rep.spoken, "lang": rep.lang,
                            "decision": rep.decision, "chunks": rep.chunks, "tool_calls": rep.tool_calls}))


@app.post("/api/reset")
def reset():
    SESSIONS.pop(request.json.get("sid", "default"), None)
    return jsonify(ok=True)


PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>ZentroMart voice support</title>
<style>body{font:16px system-ui;max-width:720px;margin:2rem auto;padding:0 1rem;color:#222}
#log{border:1px solid #ddd;border-radius:10px;padding:1rem;min-height:260px;background:#fafafa}
.u{color:#0b57d0;margin:.4rem 0}.a{margin:.4rem 0}.m{color:#888;font-size:12px}
button{font:inherit;padding:.6rem 1.2rem;border-radius:999px;border:0;background:#222;color:#fff;cursor:pointer}
button.rec{background:#c5221f}input{font:inherit;padding:.5rem;width:60%}</style>
<h2>ZentroMart voice support</h2>
<p><button id=mic>Hold to talk</button> <button id=rst style="background:#666">New call</button></p>
<p><input id=t placeholder="or type (no microphone)"> <button id=send>Send</button></p>
<div id=log></div>
<script>
const sid=Math.random().toString(36).slice(2), log=document.getElementById('log');
const add=(c,t,m)=>{log.insertAdjacentHTML('beforeend',`<div class=${c}>${t}${m?`<div class=m>${m}</div>`:''}</div>`);log.scrollTop=log.scrollHeight};
const show=r=>{add('u','You: '+(r.heard||'(nothing heard)'));add('a','Agent: '+r.reply,`${r.decision} · ${r.lang} · sources: ${(r.chunks||[]).slice(0,8).join(', ')}`);
 if(r.audio_b64)new Audio('data:audio/wav;base64,'+r.audio_b64).play()};
function wav(buf,rate){const n=buf.length,b=new DataView(new ArrayBuffer(44+n*2));const w=(o,s)=>[...s].forEach((c,i)=>b.setUint8(o+i,c.charCodeAt(0)));
 w(0,'RIFF');b.setUint32(4,36+n*2,true);w(8,'WAVEfmt ');b.setUint32(16,16,true);b.setUint16(20,1,true);b.setUint16(22,1,true);b.setUint32(24,rate,true);b.setUint32(28,rate*2,true);b.setUint16(32,2,true);b.setUint16(34,16,true);w(36,'data');b.setUint32(40,n*2,true);
 for(let i=0;i<n;i++){const s=Math.max(-1,Math.min(1,buf[i]));b.setInt16(44+i*2,s<0?s*0x8000:s*0x7fff,true)}return new Blob([b],{type:'audio/wav'})}
let rec,chunks=[];
async function start(){const s=await navigator.mediaDevices.getUserMedia({audio:true});rec=new MediaRecorder(s);chunks=[];rec.ondataavailable=e=>chunks.push(e.data);
 rec.onstop=async()=>{s.getTracks().forEach(t=>t.stop());const ctx=new OfflineAudioContext(1,1,16000);const ab=await new AudioContext().decodeAudioData(await new Blob(chunks).arrayBuffer());
  const off=new OfflineAudioContext(1,Math.ceil(ab.duration*16000),16000);const src=off.createBufferSource();src.buffer=ab;src.connect(off.destination);src.start();
  const out=await off.startRendering();const fd=new FormData();fd.append('audio',wav(out.getChannelData(0),16000),'t.wav');fd.append('sid',sid);
  const r=await (await fetch('/api/turn',{method:'POST',body:fd})).json();show(r)};rec.start()}
const mic=document.getElementById('mic');
mic.onmousedown=mic.ontouchstart=()=>{mic.classList.add('rec');mic.textContent='Listening…';start()};
mic.onmouseup=mic.ontouchend=()=>{mic.classList.remove('rec');mic.textContent='Hold to talk';rec&&rec.state!=='inactive'&&rec.stop()};
document.getElementById('send').onclick=async()=>{const t=document.getElementById('t');if(!t.value)return;
 show(await (await fetch('/api/text',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid,text:t.value})})).json());t.value=''};
document.getElementById('rst').onclick=async()=>{await fetch('/api/reset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sid})});log.innerHTML=''};
</script>"""


@app.get("/")
def index():
    return PAGE


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "7860")))
