#define PythonInstaller "python-3.14.8-amd64.exe"

[Setup]
AppName=Research Buddy Dependencies Installer
AppVersion=1.0
DefaultDirName={tmp}\ARBinstaller
DisableDirPage=yes
Uninstallable=no
PrivilegesRequired=admin

OutputDir=..
OutputBaseFilename=SetupAndRun

[Files]
Source: "{#PythonInstaller}"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Code]

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  ProjectDir: String;
  RequirementsFile: String;
  WebhostDir: String;
begin
  if CurStep = ssInstall then
  begin
  //Python installation
    Exec(ExpandConstant('{tmp}\{#PythonInstaller}'),
      '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0',
      '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
   //Install dependencies
   ProjectDir := ExtractFileDir(ExpandConstant('{srcexe}'));
   RequirementsFile := ProjectDir + '\requirements.txt';
   
   Exec('py.exe', 
   '-3.14 -m pip install -r "' + RequirementsFile + '"',
   ProjectDir, SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode);
    
   //Start Flask
   WebhostDir := ProjectDir + '\webhost';
    
   Exec('py.exe', '-3.14 -m flask --app main run --port 42555',
   WebhostDir, SW_SHOWNORMAL, ewWaitUntilIdle, ResultCode);
   
   //Open website
   ShellExec('', 'http://localhost:42555', '', '',
   SW_SHOWNORMAL, ewNoWait, ResultCode);
  end;
end;
