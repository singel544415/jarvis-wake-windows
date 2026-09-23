$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
python -m venv .buildvenv
& .\.buildvenv\Scripts\python.exe -m pip install --upgrade pip
& .\.buildvenv\Scripts\python.exe -m pip install -r windows\requirements-build.txt
& .\.buildvenv\Scripts\python.exe -c "from openwakeword.utils import download_models; download_models(['hey_jarvis'])"
& .\.buildvenv\Scripts\python.exe -m pytest -q
Remove-Item dist,build -Recurse -Force -ErrorAction SilentlyContinue
& .\.buildvenv\Scripts\pyinstaller.exe --clean --noconfirm windows\JARVIS-Wake.spec
$iscc=(Get-Command ISCC.exe -ErrorAction SilentlyContinue)
if(-not $iscc){$p='C:\Program Files (x86)\Inno Setup 6\ISCC.exe';if(Test-Path $p){$iscc=$p}else{throw 'Inno Setup 6 fehlt.'}}
& $iscc windows\installer\JARVIS-Wake.iss
$hash=(Get-FileHash dist\JARVIS-Wake-Setup.exe -Algorithm SHA256).Hash.ToLower()
"$hash  JARVIS-Wake-Setup.exe"|Set-Content dist\SHA256SUMS.txt -Encoding ascii
