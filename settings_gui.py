import tkinter as tk
from tkinter import ttk,messagebox
import sounddevice as sd
from winconfig import load_config,save_config
from winsecret import save_token
from jarvis_app import connection_test
def devices(kind):
    out=[]
    for i,d in enumerate(sd.query_devices()):
        if d["max_input_channels" if kind=="in" else "max_output_channels"]>0:out.append((i,f"{d['name']} ({i})"))
    return out
class App(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("JARVIS-Einstellungen"); self.geometry("620x410"); self.resizable(False,False); self.cfg=load_config(); self.ins=devices("in"); self.outs=devices("out"); self.build()
    def build(self):
        p=ttk.Frame(self,padding=18);p.pack(fill="both",expand=True)
        ttk.Label(p,text="JARVIS Wake",font=("Segoe UI",18,"bold")).pack(anchor="w")
        ttk.Label(p,text="Das Standardmodell reagiert am zuverlässigsten auf ‘Hey Jarvis’.").pack(anchor="w",pady=(0,15))
        ttk.Label(p,text="Mikrofon").pack(anchor="w");self.iv=tk.StringVar(value=self._name(self.ins,self.cfg.get("input_device")));ttk.Combobox(p,textvariable=self.iv,values=[x[1] for x in self.ins],state="readonly").pack(fill="x")
        ttk.Button(p,text="Mikrofon testen",command=self.mic).pack(anchor="w",pady=(4,10))
        ttk.Label(p,text="Lautsprecher").pack(anchor="w");self.ov=tk.StringVar(value=self._name(self.outs,self.cfg.get("output_device")));ttk.Combobox(p,textvariable=self.ov,values=[x[1] for x in self.outs],state="readonly").pack(fill="x")
        ttk.Button(p,text="Testton",command=self.beep).pack(anchor="w",pady=(4,10))
        ttk.Label(p,text="JARVIS-HUD-Access-Code").pack(anchor="w");self.tv=tk.StringVar();ttk.Entry(p,textvariable=self.tv,show="●").pack(fill="x")
        b=ttk.Frame(p);b.pack(fill="x",pady=16);ttk.Button(b,text="Speichern",command=self.save).pack(side="left");ttk.Button(b,text="Verbindung testen",command=self.test).pack(side="left",padx=8);ttk.Button(b,text="Schließen",command=self.destroy).pack(side="right")
    def _name(self,a,idx):return next((n for i,n in a if i==idx),"")
    def _idx(self,a,n):return next((i for i,x in a if x==n),None)
    def mic(self):
        try:
            x=sd.rec(16000,samplerate=16000,channels=1,dtype="float32",device=self._idx(self.ins,self.iv.get()),blocking=True);messagebox.showinfo("Mikrofontest",f"Mikrofon erkannt. Pegel: {float(abs(x).max()):.2f}")
        except Exception:messagebox.showerror("Mikrofontest","Mikrofonzugriff verweigert oder Gerät nicht verfügbar.")
    def beep(self):
        from client import play_beep
        try:play_beep(self._idx(self.outs,self.ov.get()))
        except Exception:messagebox.showerror("Lautsprechertest","Lautsprecher nicht verfügbar.")
    def save(self):
        self.cfg["input_device"]=self._idx(self.ins,self.iv.get());self.cfg["output_device"]=self._idx(self.outs,self.ov.get());save_config(self.cfg)
        if self.tv.get():
            try:save_token(self.tv.get());self.tv.set("")
            except ValueError as e:return messagebox.showerror("Access Code",str(e))
        messagebox.showinfo("JARVIS","Einstellungen gespeichert.")
    def test(self):self.save();ok,msg=connection_test();(messagebox.showinfo if ok else messagebox.showerror)("Verbindungstest",msg)
if __name__=="__main__":App().mainloop()
