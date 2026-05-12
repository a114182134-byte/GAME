import json
import streamlit as st
import os
import requests
import google.generativeai as genai
import subprocess
import datetime
import random
import shutil
from PIL import Image
from dotenv import load_dotenv
from pathlib import Path

# ==========================================
# 核心開發公約 v3.2.1 - 穩定性修復與自癒同步
# 認證：小白龍 - 核心邏輯架構師
# ==========================================

# 1. 環境初始化
BASE_PATH = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_PATH / ".env")

ai_key = os.getenv("ai_key")
github_token = os.getenv("github_token")

DATA_ROOT = "all_projects"
CONFIG_FILE = os.path.join(DATA_ROOT, "projects_config.json")

# 2. 核心功能函數
def init_system():
    if not os.path.exists(DATA_ROOT): os.makedirs(DATA_ROOT)
    if not os.path.exists(CONFIG_FILE):
        init = {"餘燼航路": {"theme_color": "#D4AF37", "bg_color": "#1A1A1A", "prompt": "你是架構師", "local_script_path": "", "keys_list": []}}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(init, f, indent=4, ensure_ascii=False)
        return init
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(projects_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(projects_data, f, indent=4, ensure_ascii=False)

def secure_auto_push(commit_message):
    """
    自癒同步系統：自動配置 Git 身份並處理 Status 128 錯誤
    """
    try:
        # 自動配置身份
        subprocess.run(["git", "config", "--global", "user.email", "zzz961011@gmail.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "zzz961011"], check=True)

        if not os.path.exists(BASE_PATH / ".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/a114182134-byte/GAME.git"], check=True)

        # 維護排除清單
        ignore_content = ".env\n__pycache__/\nall_projects/media/\nall_projects/logs/"
        with open(BASE_PATH / ".gitignore", "w") as f: f.write(ignore_content)

        if not os.getenv("github_token"):
            return False, "❌ 未配置 github_token"

        subprocess.run(["git", "add", "."], check=True)
        
        # 檢查變更
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if not status:
            return True, "✨ 雲端已是最新狀態。"

        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        token = os.getenv("github_token")
        repo_url = f"https://{token}@github.com/a114182134-byte/GAME.git"
        subprocess.run(["git", "push", repo_url, "main", "--force"], check=True)
        return True, "✅ 進化同步成功！"
    except Exception as e:
        return False, f"❌ 同步失敗: {str(e)}"

# 3. UI 構建
st.set_page_config(page_title="小白龍核心母站 v3.2.1", layout="wide", page_icon="⚓")
PROJECTS = init_system()

with st.sidebar:
    st.title("⚙️ 核心中控台")
    current_p_name = st.selectbox("核心專案切換", list(PROJECTS.keys()))
    config = PROJECTS[current_p_name]
    
    st.divider()
    st.subheader("🔑 金鑰管理")
    saved_keys = config.get("keys_list", [])
    sel_key = st.selectbox("記憶清單", ["手動輸入"] + saved_keys)
    input_key = st.text_input("API Key", value="" if sel_key == "手動輸入" else sel_key, type="password")
    
    if st.button("🔐 記憶鎖定"):
        if input_key and input_key not in saved_keys:
            PROJECTS[current_p_name].setdefault("keys_list", []).append(input_key)
            save_config(PROJECTS)
        st.session_state.active_key = input_key

    AI_MODEL = st.selectbox("AI 模型", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"])
    channel = st.radio("功能頻道", ["💡 媒體採集", "📜 AI 寫腳本", "📂 檔案修復", "📖 答案之書", "🛠️ 管理部署"])

# 獲取當前有效 Key
FINAL_KEY = st.session_state.get("active_key", ai_key if ai_key else input_key)
if FINAL_KEY: genai.configure(api_key=FINAL_KEY)

# 建立資源目錄
LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
for d in [LOG_DIR, MEDIA_DIR]: 
    if not os.path.exists(d): os.makedirs(d)

# 4. 頻道實作 (精簡核心邏輯)
if channel == "💡 媒體採集":
    st.title("💡 媒體採集與分析")
    u_text = st.text_input("分析指令")
    u_img = st.file_uploader("🖼️ 儲存圖片", type=['png', 'jpg'])
    if st.button("🚀 執行與儲存"):
        if u_img:
            img = Image.open(u_img)
            img.save(os.path.join(MEDIA_DIR, f"save_{datetime.datetime.now().strftime('%H%M%S')}.png"))
            st.success("圖片已入庫")

elif channel == "📜 AI 寫腳本":
    st.title("📜 AI 自動寫腳本")
    task = st.text_area("🔧 需求描述")
    if st.button("🪄 生成"):
        model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
        res = model.generate_content(task)
        st.code(res.text, language="gdscript")

elif channel == "📂 檔案修復":
    st.title("📂 自動修復")
    p = config.get("local_script_path", "")
    if p and os.path.exists(p):
        files = [f for f in os.listdir(p) if f.endswith('.gd')]
        sel_f = st.selectbox("選擇檔案", files)
        if sel_f and st.button("🔥 AI 重構"):
            st.info("執行重構中...")
    else: st.warning("請先設定路徑")

elif channel == "📖 答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 啟示"):
        st.write(random.choice(["代碼如火，邏輯如鋼。", "鏽蝕之中，方見重生。", "保持航向，莫入虛空。"]))

elif channel == "🛠️ 管理部署":
    st.title("🛠️ 專案管理與同步")
    
    with st.expander("🔑 燃料庫 (.env) 配置"):
        new_ai = st.text_input("ai_key", value=os.getenv("ai_key", ""), type="password")
        new_gh = st.text_input("github_token", value=os.getenv("github_token", ""), type="password")
        if st.button("🚀 物理寫入"):
            with open(BASE_PATH / ".env", "w", encoding="utf-8") as f:
                f.write(f"ai_key={new_ai}\ngithub_token={new_gh}\n")
            os.environ["ai_key"] = new_ai
            os.environ["github_token"] = new_gh
            st.success("燃料庫已更新")

    with st.expander("📝 專案修改與刪除"):
        # 修改邏輯
        p_path = st.text_input("Godot 路徑", config.get("local_script_path", ""))
        if st.button("💾 儲存路徑"):
            PROJECTS[current_p_name]["local_script_path"] = p_path
            save_config(PROJECTS)
        
        # 刪除邏輯
        if st.button("🗑️ 刪除此專案"):
            if len(PROJECTS) > 1:
                del PROJECTS[current_p_name]
                save_config(PROJECTS)
                st.rerun()

    st.divider()
    st.subheader("🚀 雲端同步")
    c_msg = st.text_input("Commit Message", value="Update " + datetime.datetime.now().strftime("%m%d"))
    if st.button("🔥 啟動同步"):
        success, msg = secure_auto_push(c_msg)
        if success: st.success(msg)
        else: st.error(msg)