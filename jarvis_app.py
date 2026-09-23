from __future__ import annotations
import asyncio,json,logging,queue,ssl,threading,time
from logging.handlers import RotatingFileHandler
import numpy as np
import sounddevice as sd
import websockets
from openwakeword.model import Model as WakeWordModel
from client import SAMPLE_RATE,CHANNELS,DTYPE,CHUNK_FRAMES,WakeModeController,UtteranceDetector,InstructionCapture,audio_callback_factory,play_beep,drain_audio_queue
from winconfig import load_config,resource_path,app_data_dir
from winsecret import load_token
LOG_DIR=app_data_dir()/"logs";LOG_DIR.mkdir(parents=True,exist_ok=True)
logger=logging.getLogger("jarvis");logger.setLevel(logging.INFO)
_h=RotatingFileHandler(LOG_DIR/"jarvis-wake.log",maxBytes=1000000,backupCount=3,encoding="utf-8");_h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"));logger.addHandler(_h)
class JarvisRuntime:
 def __init__(self):self.stop_requested=threading.Event();self.muted=False;self.state="VERBINDUNG GETRENNT";self.thread=None
 def set_state(self,s):self.state=s;logger.info("state=%s",s)
 def start(self):
  if self.thread and self.thread.is_alive():return
  self.stop_requested.clear();self.thread=threading.Thread(target=self._runner,daemon=True);self.thread.start()
 def stop(self):self.stop_requested.set();sd.stop()
 def set_muted(self,v):self.muted=bool(v);self.set_state("MIKROFON AUS" if v else "WARTE AUF JARVIS")
 def _runner(self):
  delay=1
  while not self.stop_requested.is_set():
   try:asyncio.run(self._session());delay=1
   except Exception as e:logger.exception("runtime error: %s",type(e).__name__);self.set_state("VERBINDUNG GETRENNT")
   if not self.stop_requested.wait(delay):delay=min(delay*2,30)
 async def _session(self):
  cfg=load_config();token=load_token()
  if not token:self.set_state("FEHLER");raise RuntimeError("Access Code fehlt")
  ctx=ssl.create_default_context(cafile=str(resource_path("jarvis-ca.crt")));q=queue.Queue(maxsize=200);controller=WakeModeController();controller.set_muted(self.muted)
  async with websockets.connect(cfg["server"],ssl=ctx,additional_headers={"X-Jarvis-Token":token},max_size=None,ping_interval=20,ping_timeout=20) as ws:
   inp=resolve_device(cfg.get("input_device"),"input");out=resolve_device(cfg.get("output_device"),"output")
   with sd.RawInputStream(samplerate=SAMPLE_RATE,blocksize=CHUNK_FRAMES,dtype=DTYPE,channels=CHANNELS,device=inp,callback=audio_callback_factory(q)):
    self.set_state("MIKROFON AUS" if self.muted else "WARTE AUF JARVIS");model=WakeWordModel(wakeword_models=[cfg.get("wake_model_file") or "hey_jarvis"])
    while not self.stop_requested.is_set():
     try:chunk=await asyncio.to_thread(q.get,True,.2)
     except queue.Empty:continue
     if self.muted:continue
     pred=model.predict(np.frombuffer(chunk,dtype=np.int16));score=float(pred.get("hey_jarvis",max(pred.values(),default=0.0)))
     if score<float(cfg.get("wake_threshold",.55)):continue
     self.set_state("JARVIS ERKANNT");await asyncio.to_thread(play_beep,out);drain_audio_queue(q);self.set_state("HÖRT ZU")
     cap=InstructionCapture(UtteranceDetector(SAMPLE_RATE,float(cfg.get("speech_threshold",500)),5,2,12));sent=False
     while not cap.finished and not self.stop_requested.is_set() and not self.muted:
      try:ch=await asyncio.to_thread(q.get,True,.2)
      except queue.Empty:continue
      for action,payload in cap.feed(ch,time.perf_counter()):
       if action=="start":await ws.send(json.dumps({"type":"start","sample_rate":SAMPLE_RATE,"format":"pcm_s16le","channels":CHANNELS,"conversation":"jarvis-main","partials":False}));sent=True
       elif action=="audio":await ws.send(payload)
       elif action=="stop":await ws.send(json.dumps({"type":"stop"}));self.set_state("VERARBEITET")
     if sent:
      pcm=bytearray()
      while not self.stop_requested.is_set():
       msg=await ws.recv()
       if isinstance(msg,bytes):pcm.extend(msg);continue
       ev=json.loads(msg)
       if ev.get("type")=="agent_status" and ev.get("state")=="speaking":self.set_state("SPRICHT")
       elif ev.get("type")=="done":
        if pcm:await asyncio.to_thread(sd.play,np.frombuffer(bytes(pcm[:len(pcm)-len(pcm)%2]),dtype=np.int16),SAMPLE_RATE,out,True)
        break
     if hasattr(model,"reset"):model.reset()
     self.set_state("MIKROFON AUS" if self.muted else "WARTE AUF JARVIS")
def resolve_device(saved,kind):
 if saved is None:return None
 try:
  d=sd.query_devices(int(saved));return int(saved) if d["max_input_channels" if kind=="input" else "max_output_channels"]>0 else None
 except Exception:return None
def connection_test():
 async def t():
  cfg=load_config();token=load_token()
  if not token:return False,"Access Code fehlt"
  try:
   ctx=ssl.create_default_context(cafile=str(resource_path("jarvis-ca.crt")))
   async with websockets.connect(cfg["server"],ssl=ctx,additional_headers={"X-Jarvis-Token":token},open_timeout=5) as ws:return True,"Verbindung, TLS und Access Code erfolgreich geprüft"
  except ssl.SSLError:return False,"TLS-Zertifikat passt nicht"
  except OSError:return False,"Commander nicht erreichbar"
  except Exception as e:return False,f"Verbindung fehlgeschlagen ({type(e).__name__})"
 return asyncio.run(t())
