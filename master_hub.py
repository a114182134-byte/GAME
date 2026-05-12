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
    st.title("📂 腳本監控與 AI 自動修復")
    st.markdown("---")
    
    # 從專案配置中獲取本地 Godot 腳本路徑
    script_path = config.get("local_script_path", "")
    
    if script_path and os.path.exists(script_path):
        # 掃描資料夾內所有的 GDScript 檔案
        files = [f for f in os.listdir(script_path) if f.endswith('.gd')]
        
        if not files:
            st.warning(f"⚠️ 在路徑 `{script_path}` 中找不到任何 .gd 檔案。")
        else:
            # 讓架構師選擇要干涉的目標
            selected_file = st.selectbox("🎯 選擇監控目標檔案", files)
            file_full_path = os.path.join(script_path, selected_file)
            
            # 讀取並顯示當前原始碼
            with open(file_full_path, "r", encoding="utf-8") as f:
                current_code = f.read()
            
            with st.expander("📄 查看當前原始碼內容"):
                st.code(current_code, language="gdscript")
            
            # 修復指令輸入區
            st.subheader("🔥 物理重構指令")
            fix_instruction = st.text_area("🔧 請輸入修復目標或重構需求", 
                                         placeholder="例如：修復魚叉發射的緩衝邏輯，或優化內存佔用...")
            
            if st.button("🚀 執行 AI 物理重構並覆寫"):
                if not FINAL_KEY:
                    st.error("❌ 缺少 API Key，無法啟動 AI 大腦。")
                elif not fix_instruction:
                    st.warning("請輸入重構指令。")
                else:
                    with st.spinner("AI 正在解析並重構代碼中..."):
                        # 呼叫 Gemini 進行代碼重寫
                        model = genai.GenerativeModel(AI_MODEL)
                        prompt = f"你現在是 Godot 4.x 專家。請根據以下需求重構代碼。\n需求：{fix_instruction}\n\n原始代碼：\n{current_code}"
                        
                        try:
                            response = model.generate_content(prompt)
                            # 嚴格清理 Markdown 標籤，確保寫入純代碼
                            clean_code = response.text.replace("```gdscript", "").replace("```python", "").replace("```", "").strip()
                            
                            # 執行物理覆寫
                            with open(file_full_path, "w", encoding="utf-8") as f:
                                f.write(clean_code)
                            
                            st.success(f"✅ {selected_file} 物理重構成功！已完成自動覆寫。")
                            st.balloons()
                            
                            # 存入開發日誌以供『答案之書』學習
                            with open(os.path.join(LOG_DIR, "fix_history.md"), "a", encoding="utf-8") as log_f:
                                log_f.write(f"\n## {datetime.datetime.now()} 修復檔案: {selected_file}\n- **需求**: {fix_instruction}\n")
                        
                        except Exception as e:
                            st.error(f"❌ 重構失敗: {str(e)}")
    else:
        # 導向路徑設定介面
        st.error(f"❌ 偵測不到路徑: `{script_path}`")
        st.info("請前往『🛠️ 管理部署』頻道設定正確的『Godot 腳本路徑』。")

elif channel == "📖 答案之書":
    st.title("📖 智慧答案之書")
    st.markdown("---")
    
    # 建立啟示抽取按鈕
    if st.button("🔮 擷取靈魂啟示"):
        # 建立備用啟示庫（當日誌不足時使用）
        backup_quotes = [
            "代碼如火，邏輯如鋼。",
            "鏽蝕之中，方見重生。",
            "保持航向，莫入虛空。",
            "黃銅的齒輪從不說謊。",
            "每一次崩潰，都是進化的契機。"
        ]
        
        pool = []
        # 嘗試從該專案的日誌資料夾中讀取內容
        if os.path.exists(LOG_DIR):
            for root, dirs, files in os.walk(LOG_DIR):
                for fn in files:
                    if fn.endswith('.md'):
                        with open(os.path.join(root, fn), "r", encoding="utf-8") as f:
                            # 讀取非空白且長度足夠的行作為啟示
                            lines = [l.strip() for l in f.readlines() if len(l.strip()) > 5]
                            pool.extend(lines)
        
        # 決定最終顯示內容
        if pool:
            # 優先從你的開發歷史中抽取啟示
            revelation = random.choice(pool)
            st.info(f"⚓ **來自開發日誌的啟示：**\n\n{revelation}")
        else:
            # 日誌庫空虛時的隨機語錄
            revelation = random.choice(backup_quotes)
            st.success(f"✨ **架構師語錄：**\n\n{revelation}")
            
    st.divider()
    st.caption("※ 答案之書會自動分析你的開發日誌，將你過去的思考轉化為未來的指引。")
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