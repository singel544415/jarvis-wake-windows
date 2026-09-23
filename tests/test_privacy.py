import numpy as np
from client import UtteranceDetector,InstructionCapture,WakeModeController
def pcm(v,n=1280):return (np.ones(n,dtype=np.int16)*v).tobytes()
def test_silence_before_speech_never_emits_audio():
 c=InstructionCapture(UtteranceDetector(16000,500,5,2,12));assert c.feed(pcm(10),0)==[];assert c.feed(pcm(10),1)==[]
def test_no_instruction_aborts_without_start():
 c=InstructionCapture(UtteranceDetector(16000,500,5,2,12));c.feed(pcm(10),0);assert c.feed(pcm(10),5.1)==[("abort",None)]
def test_speech_starts_once_and_stops_after_silence():
 c=InstructionCapture(UtteranceDetector(16000,500,5,2,12));assert [x[0] for x in c.feed(pcm(1000),0)]==["start","audio"];assert [x[0] for x in c.feed(pcm(10),2.1)]==["audio","stop"]
def test_mute_blocks_detection():
 c=WakeModeController();c.set_muted(True);assert not c.can_detect_wake;assert c.status=="mikrofon_aus"
