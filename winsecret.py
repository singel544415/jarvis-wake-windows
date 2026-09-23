from __future__ import annotations
import base64,ctypes,os
from ctypes import wintypes
from winconfig import app_data_dir
class DATA_BLOB(ctypes.Structure): _fields_=[("cbData",wintypes.DWORD),("pbData",ctypes.POINTER(ctypes.c_byte))]
def _blob(data):
    buf=ctypes.create_string_buffer(data); return DATA_BLOB(len(data),ctypes.cast(buf,ctypes.POINTER(ctypes.c_byte))),buf
def protect(text):
    if os.name!="nt":raise RuntimeError("DPAPI ist nur unter Windows verfügbar")
    inp,keep=_blob(text.encode()); out=DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(inp),"JARVIS",None,None,None,0,ctypes.byref(out)):raise ctypes.WinError()
    try:return ctypes.string_at(out.pbData,out.cbData)
    finally:ctypes.windll.kernel32.LocalFree(out.pbData)
def unprotect(data):
    inp,keep=_blob(data); out=DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(inp),None,None,None,None,0,ctypes.byref(out)):raise ctypes.WinError()
    try:return ctypes.string_at(out.pbData,out.cbData).decode()
    finally:ctypes.windll.kernel32.LocalFree(out.pbData)
def save_token(token):
    if len(token)<16 or any(c.isspace() for c in token):raise ValueError("Access Code muss mindestens 16 Zeichen ohne Leerzeichen haben")
    (app_data_dir()/"token.dpapi").write_bytes(base64.b64encode(protect(token)))
def load_token():
    try:return unprotect(base64.b64decode((app_data_dir()/"token.dpapi").read_bytes()))
    except FileNotFoundError:return None
