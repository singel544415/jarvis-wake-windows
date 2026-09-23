from __future__ import annotations
import json,os,sys
from pathlib import Path
DEFAULT={"server":"wss://192.168.178.111:8766/ws","input_device":None,"output_device":None,"wake_threshold":0.55,"speech_threshold":500.0,"wake_model_file":None}
def app_data_dir():
    p=Path(os.environ.get("LOCALAPPDATA",Path.home()/"AppData/Local"))/"JARVIS Wake"; p.mkdir(parents=True,exist_ok=True); return p
def config_path(): return app_data_dir()/"settings.json"
def load_config():
    d=DEFAULT.copy()
    try:d.update(json.loads(config_path().read_text(encoding="utf-8")))
    except (FileNotFoundError,json.JSONDecodeError):pass
    return d
def save_config(d):config_path().write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def resource_path(name):return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))/name
