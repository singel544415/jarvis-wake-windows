from __future__ import annotations
import asyncio, math, queue
import numpy as np
import sounddevice as sd
SAMPLE_RATE=16000; CHANNELS=1; DTYPE="int16"; CHUNK_MS=80; CHUNK_FRAMES=int(SAMPLE_RATE*CHUNK_MS/1000)
class WakeModeController:
    def __init__(self): self.muted=False; self.status="wartet_auf_jarvis"
    @property
    def can_detect_wake(self): return not self.muted and self.status=="wartet_auf_jarvis"
    def set_status(self,s): self.status="mikrofon_aus" if self.muted else s
    def set_muted(self,v): self.muted=bool(v); self.status="mikrofon_aus" if self.muted else "wartet_auf_jarvis"
class UtteranceDetector:
    def __init__(self,sample_rate,speech_threshold,initial_timeout_seconds,silence_seconds,max_record_seconds):
        self.sample_rate=sample_rate; self.speech_threshold=speech_threshold; self.initial_timeout_seconds=initial_timeout_seconds; self.silence_seconds=silence_seconds; self.max_record_seconds=max_record_seconds
        self.started_at=None; self.last_speech_at=None; self.speech_started=False
    def observe(self,chunk,now):
        if self.started_at is None:self.started_at=now
        elapsed=now-self.started_at; usable=len(chunk)-(len(chunk)%2)
        a=np.frombuffer(chunk[:usable],dtype=np.int16) if usable else np.empty(0,dtype=np.int16)
        rms=float(np.sqrt(np.mean(a.astype(np.float32)**2))) if a.size else 0.0
        if rms>=self.speech_threshold:self.speech_started=True; self.last_speech_at=now
        elif self.speech_started and self.last_speech_at is not None and now-self.last_speech_at>=self.silence_seconds:return "stop"
        elif elapsed>=self.initial_timeout_seconds:return "timeout"
        if elapsed>=self.max_record_seconds:return "stop" if self.speech_started else "timeout"
        return "continue"
class InstructionCapture:
    def __init__(self,detector): self.detector=detector; self.started=False; self.finished=False
    def feed(self,chunk,now):
        if self.finished:return []
        d=self.detector.observe(chunk,now)
        if d=="timeout" and not self.started:self.finished=True; return [("abort",None)]
        out=[]
        if self.detector.speech_started and not self.started:self.started=True; out.append(("start",None))
        if self.started:out.append(("audio",chunk))
        if d=="stop" and self.started:self.finished=True; out.append(("stop",None))
        return out
def make_beep(sample_rate=SAMPLE_RATE,duration=.18,freq=880.0):
    t=np.linspace(0,duration,int(sample_rate*duration),endpoint=False); return (0.20*np.sin(2*math.pi*freq*t)).astype(np.float32)
def play_beep(output_device=None): sd.play(make_beep(),samplerate=SAMPLE_RATE,device=output_device,blocking=True)
def audio_callback_factory(q):
    def cb(indata,frames,time_info,status):
        try:q.put_nowait(bytes(indata))
        except queue.Full:
            try:q.get_nowait()
            except queue.Empty:pass
            try:q.put_nowait(bytes(indata))
            except queue.Full:pass
    return cb
def drain_audio_queue(q):
    while True:
        try:q.get_nowait()
        except queue.Empty:return
async def wait_for_turn_completion(turn_complete,stop_event):
    while not stop_event.is_set():
        try: await asyncio.wait_for(turn_complete.wait(),.2); return True
        except asyncio.TimeoutError: pass
    return False
