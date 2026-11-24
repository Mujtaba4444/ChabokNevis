; ============================================================
; ChabokNevis - Windows Installer
; Developer: Mohammad Mujtaba Mohammadi
; ============================================================

#define MyAppName "ChabokNevis"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Mohammad Mujtaba Mohammadi"
#define MyAppExeName "ChabokNevis.exe"

[Setup]

; Unique application identifier - keep unchanged for future updates
AppId={{C998FC93-6708-4349-97B7-49513F003D89}

; Application information
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Installation directory
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; Supported architecture: 64-bit Windows
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Installer interface
DisableProgramGroupPage=yes
WizardStyle=modern dynamic

; Output configuration
OutputDir=installer
OutputBaseFilename=ChabokNevis_Setup

; Installer icon (Path relative to project root)
SetupIconFile=app\resources\icons\ChabokNevis.ico

; Compression
SolidCompression=yes

; Installer version information
VersionInfoVersion=1.0.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=ChabokNevis Windows Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]

Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]

Name: "desktopicon"; \
    Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; \
    Flags: unchecked

[Files]

; Copy the complete PyInstaller application from the dist folder
; Includes executable, Python runtime, dependencies and resources
Source: "dist\ChabokNevis\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]

; Start Menu shortcut
Name: "{autoprograms}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"

; Optional Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; \
    Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon

[Run]

; Launch ChabokNevis after installation
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent
