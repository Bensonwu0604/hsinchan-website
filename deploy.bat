@echo off
cd /d "d:\CLAUDE\XINCHAN-WEB"
if not exist ".git" cd /d "d:\CLAUDE\欣晨網頁"

echo.
echo ======================================
echo   Hsin-Chan Website - Deploy
echo ======================================
echo.

set HAS_CHANGES=0
for /f "tokens=*" %%i in ('git status --porcelain 2^>nul') do set HAS_CHANGES=1

if "%HAS_CHANGES%"=="0" (
  echo [OK] Nothing to deploy. No changes detected.
  echo.
  pause
  exit /b 0
)

echo [INFO] Changes detected:
git status --short
echo.

set MSG=
set /p MSG=Commit message (e.g. update FAQ):
if "%MSG%"=="" set MSG=update website

echo.
echo [INFO] Pushing to GitHub...
git add -A
git commit -m "%MSG%"
git push origin main

if %ERRORLEVEL%==0 (
  echo.
  echo ======================================
  echo   [DONE] Site updates in ~30 seconds
  echo   https://www.hsinchan.com
  echo ======================================
) else (
  echo.
  echo [ERROR] Push failed. Check network.
)
echo.
pause
