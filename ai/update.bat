@echo off
chcp 65001
title 小白龍開發母站 - 自動更新引擎
cls

echo ============================================
echo      ⚓ 小白龍開發母站：核心同步系統 ⚓
echo ============================================
echo.
echo 正在連線至 GitHub 獲取最新「旗艦完全體」代碼...
echo.

:: 設定你的 GitHub Raw 網址 (請把下面的網址換成你剛才複製的)
set "https://raw.githubusercontent.com/a114182134-byte/GAME/refs/heads/main/ai/master_hub.py"

:: 使用 PowerShell 下載檔案並覆蓋
powershell -Command "(New-Object Net.WebClient).DownloadFile('%RAW_URL%', 'master_hub.py')"

if %errorlevel% equ 0 (
    echo.
    echo [✅ 成功] 代碼已物理同步至最新版本！
    echo [提示] 正在檢查是否有更新的說明書...
    echo.
    timeout /t 2 >nul
    echo 更新完成，現在可以啟動母站了。
) else (
    echo.
    echo [❌ 錯誤] 同步失敗，請檢查網路連線或 GitHub 網址是否正確。
)

echo.
pause
