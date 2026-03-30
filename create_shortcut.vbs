Set ws = CreateObject("WScript.Shell")
Set s = ws.CreateShortcut(ws.SpecialFolders("Desktop") & "\Deploy.lnk")
s.TargetPath = "d:\CLAUDE\" & Chr(27431) & Chr(26228) & Chr(32178) & Chr(39292) & "\deploy.bat"
s.WorkingDirectory = "d:\CLAUDE\" & Chr(27431) & Chr(26228) & Chr(32178) & Chr(39292)
s.IconLocation = "shell32.dll,23"
s.Save
