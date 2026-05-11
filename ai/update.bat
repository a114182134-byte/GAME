@echo off
chcp 65001
title ⚓ 小白龍開發母站 - 自動更新引擎
cls

echo ============================================
echo      ⚓ 小白龍開發母站：核心同步系統 ⚓
echo ============================================
echo.
echo [狀態] 正在連線至 GitHub 獲取最新「旗艦完全體」代碼...
echo.

:: 核心網址 (建議將倉庫設為 Public 以確保此連結永久有效)
set "RAW_URL=https://raw.githubusercontent.com/a114182134-byte/GAME/main/ai/master_hub.py"

:: 下載檔案並覆蓋舊的 master_hub.py
powershell -Command "(New-Object Net.WebClient).DownloadFile('%RAW_URL%', 'master_hub.py')"

if %errorlevel% equ 0 (
    echo.
    echo [✅ 成功] 物理同步完成！代碼已更新至最新狀態。
    echo.
    timeout /t 3 >nul
    echo 正在啟動母站...
    :: 下行可自動幫她啟動，如果不想要自動啟動可刪除
    streamlit run master_hub.py
) else (
    echo.
    echo [❌ 錯誤] 同步失敗！
    echo 可能原因：
    echo 1. 網路連線中斷。
    echo 2. 倉庫為私人狀態且 Token 已過期 (建議將倉庫設為 Public)。
    echo.
    pause
)
