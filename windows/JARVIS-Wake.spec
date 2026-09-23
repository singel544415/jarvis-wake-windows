# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

oww_data, oww_bins, oww_hidden = collect_all('openwakeword')
ort_data, ort_bins, ort_hidden = collect_all('onnxruntime')
common_datas = oww_data + ort_data + [(r'..\jarvis-ca.crt', '.')]
common_bins = oww_bins + ort_bins
common_hidden = oww_hidden + ort_hidden

def onedir(name, script):
    a = Analysis(
        [script],
        pathex=['..'],
        binaries=common_bins,
        datas=common_datas,
        hiddenimports=common_hidden,
        hookspath=[],
        runtime_hooks=[],
        excludes=['sklearn'],
        noarchive=False,
    )
    pyz = PYZ(a.pure)
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
    )
    return COLLECT(
        exe, a.binaries, a.datas,
        strip=False,
        upx=False,
        name=name,
    )

wake = onedir('JARVIS-Wake', r'..\tray_app.py')
settings = onedir('JARVIS-Einstellungen', r'..\settings_gui.py')
