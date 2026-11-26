; ============================================================
; ChabokNevis - Windows Installer
; Developer: Mohammad Mujtaba Mohammadi
; ============================================================

#define MyAppName "ChabokNevis"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Mohammad Mujtaba Mohammadi"
#define MyAppExeName "ChabokNevis.exe"

[Setup]

; Application identity
AppId={{C998FC93-6708-4349-97B7-49513F003D89}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Installation settings
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Installer output
OutputDir=installer
OutputBaseFilename=ChabokNevis_Setup

; Installer appearance
SetupIconFile=app\resources\icons\ChabokNevis.ico
WizardStyle=modern
DisableProgramGroupPage=yes

; Compression
Compression=lzma2
SolidCompression=yes

; Version information
VersionInfoVersion=1.0.1.0
VersionInfoCompany=Mohammad Mujtaba Mohammadi
VersionInfoDescription=ChabokNevis Windows Installer
VersionInfoProductName=ChabokNevis
VersionInfoProductVersion=1.0.1

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ChabokNevis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch ChabokNevis"; Flags: nowait postinstall skipifsilent
