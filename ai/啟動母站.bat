@echo off
title 小白龍母站啟動器
echo ? [小白龍架構師] 正在透過物理環境啟動母站...
echo ------------------------------------------

:: 使用 python 執行 streamlit 啟動主程式
python -m streamlit run master_hub.py --global.developmentMode=false

pause