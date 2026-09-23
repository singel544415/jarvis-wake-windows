import os,subprocess,sys
from pathlib import Path
import pystray
from PIL import Image,ImageDraw
from jarvis_app import JarvisRuntime,connection_test,LOG_DIR
def icon_image():
 im=Image.new("RGB",(64,64),"black");d=ImageDraw.Draw(im);d.ellipse((8,8,56,56),outline="white",width=5);d.ellipse((27,27,37,37),fill="white");return im
rt=JarvisRuntime();rt.start()
def settings(icon,item):subprocess.Popen([str(Path(sys.executable).with_name("JARVIS-Einstellungen.exe"))])
def logs(icon,item):os.startfile(LOG_DIR)
def test(icon,item):
 ok,msg=connection_test();icon.notify(msg,"JARVIS Verbindungstest")
def mute(icon,item):rt.set_muted(not rt.muted)
def quit_(icon,item):rt.stop();icon.stop()
menu=pystray.Menu(pystray.MenuItem(lambda item:rt.state,None,enabled=False),pystray.MenuItem("Mikrofon stummschalten",mute,checked=lambda i:rt.muted),pystray.MenuItem("Einstellungen",settings),pystray.MenuItem("Verbindung testen",test),pystray.MenuItem("Protokollordner öffnen",logs),pystray.MenuItem("Beenden",quit_))
pystray.Icon("jarvis-wake",icon_image(),"JARVIS Wake",menu).run()
