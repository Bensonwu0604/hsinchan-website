@echo off
chcp 65001 >nul
cd /d "d:\CLAUDE\欣晨網頁"

echo.
echo ======================================
echo   欣晨工業網站 — 一鍵部署
echo ======================================
echo.

:: 檢查是否有修改
git status --short > temp_status.txt
set /p STATUS=<temp_status.txt
del temp_status.txt

if "%STATUS%"=="" (
  echo 沒有任何修改，無需部署。
  echo.
  pause
  exit /b 0
)

:: 顯示修改的檔案
echo 偵測到以下修改：
git status --short
echo.

:: 詢問部署說明
set /p MSG=請輸入這次修改的說明（例如：更新FAQ、修改產品介紹）：

if "%MSG%"=="" set MSG=更新網站內容

:: 執行部署
echo.
echo 正在部署中...
git add -A
git commit -m "%MSG%"
git push origin main

echo.
echo ======================================
echo   部署完成！約 30 秒後網站自動更新
echo   網址：https://www.hsinchan.com
echo ======================================
echo.
pause
