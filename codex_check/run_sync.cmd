@echo off
setlocal
cd /d "%~dp0.."
"C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m codex_check.sync_tool %*
exit /b %ERRORLEVEL%
