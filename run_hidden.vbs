' run_hidden.vbs
' Launches launcher.py using pythonw (no console window at all).
' Users never see a terminal.

Dim objShell
Set objShell = CreateObject("WScript.Shell")

' Get the folder this VBS file lives in
Dim scriptDir
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run pythonw (GUI-mode Python — no console window)
objShell.Run "pythonw """ & scriptDir & "\launcher.py""", 0, False

Set objShell = Nothing
