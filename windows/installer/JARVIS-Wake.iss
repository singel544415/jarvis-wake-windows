#define MyAppName "JARVIS Wake"
#define MyAppVersion "1.1.0"
[Setup]
AppId={{C3B17132-8E48-4B6A-A21B-98F6F11F6A8E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\JARVIS Wake
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=JARVIS-Wake-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
[Files]
Source: "..\..\dist\JARVIS-Wake\*"; DestDir: "{app}\JARVIS-Wake"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\dist\JARVIS-Einstellungen\*"; DestDir: "{app}\JARVIS-Einstellungen"; Flags: ignoreversion recursesubdirs createallsubdirs
[Tasks]
Name: "autostart"; Description: "JARVIS bei Windows-Anmeldung starten"; Flags: checkedonce
[Icons]
Name: "{group}\JARVIS-Einstellungen"; Filename: "{app}\JARVIS-Einstellungen\JARVIS-Einstellungen.exe"
Name: "{userstartup}\JARVIS Wake"; Filename: "{app}\JARVIS-Wake\JARVIS-Wake.exe"; Tasks: autostart
[Run]
Filename: "{app}\JARVIS-Einstellungen\JARVIS-Einstellungen.exe"; Description: "Mikrofon, Lautsprecher und Access Code einrichten"; Flags: nowait postinstall skipifsilent
Filename: "{app}\JARVIS-Wake\JARVIS-Wake.exe"; Description: "JARVIS Wake starten"; Flags: nowait postinstall skipifsilent
