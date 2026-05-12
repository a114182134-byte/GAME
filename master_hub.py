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

if channel == "💡 媒體採集":
    st.title("💡 媒體採集與跨模態分析")
    st.markdown("---")
    
    # 1. 指令輸入與麥克風組件
    u_text = st.text_area("🧠 分析指令 (或用語音輸入後自動填充)", placeholder="描述需求...")
    
    st.subheader("🎤 語音靈感捕捉")
    # 使用 streamlit 自帶的錄音組件 (需安裝 streamlit-audio-recorder 或使用以下標準錄音方案)
    from audio_recorder_streamlit import audio_recorder
    audio_bytes = audio_recorder(
        text="點擊圖示開始/停止錄音",
        recording_color="#e74c3c",
        neutral_color="#D4AF37",
        icon_name="microphone",
        icon_size="2x",
    )

    st.divider()
    
    # 2. 檔案上傳區
    col1, col2 = st.columns(2)
    with col1:
        u_img = st.file_uploader("🖼️ 儲存並分析圖片", type=['png', 'jpg', 'jpeg'])
    with col2:
        u_audio = st.file_uploader("🎵 上傳現有音訊檔", type=['mp3', 'wav', 'ogg'])
    
    # 3. 執行執行與儲存邏輯
    if st.button("🚀 啟動跨模態採集"):
        if not (u_img or u_audio or u_text or audio_bytes):
            st.warning("請提供素材或進行錄音。")
        else:
            with st.spinner("核心引擎處理媒體中..."):
                model = genai.GenerativeModel(AI_MODEL)
                content_payload = []
                timestamp = datetime.datetime.now().strftime('%m%d_%H%M%S')
                
                # --- 處理麥克風錄音 ---
                if audio_bytes:
                    mic_name = f"mic_{timestamp}.wav"
                    mic_path = os.path.join(MEDIA_DIR, mic_name)
                    with open(mic_path, "wb") as f:
                        f.write(audio_bytes)
                    content_payload.append({"mime_type": "audio/wav", "data": audio_bytes})
                    st.toast(f"🎙️ 麥克風錄音已入庫: {mic_name}")

                # --- 處理圖片 ---
                if u_img:
                    img = Image.open(u_img)
                    img_name = f"img_{timestamp}.png"
                    img_path = os.path.join(MEDIA_DIR, img_name)
                    img.save(img_path)
                    content_payload.append(img)
                    st.toast(f"🖼️ 圖片已入庫: {img_name}")

                # --- 處理上傳音訊 ---
                if u_audio:
                    a_data = u_audio.read()
                    a_path = os.path.join(MEDIA_DIR, u_audio.name)
                    with open(a_path, "wb") as f: f.write(a_data)
                    content_payload.append({"mime_type": u_audio.type, "data": a_data})
                    st.toast(f"🎵 音訊檔已入庫: {u_audio.name}")

                # 組合最終指令
                final_prompt = u_text if u_text else "請分析以上媒體內容。如果是語音錄音，請先將其轉錄為文字並總結重點。"
                content_payload.insert(0, final_prompt)

                try:
                    if FINAL_KEY:
                        response = model.generate_content(content_payload)
                        st.markdown("### 📝 AI 綜合分析報告")
                        st.write(response.text)
                        
                        # 存入日誌，供『答案之書』未來調用
                        with open(os.path.join(LOG_DIR, "media_log.md"), "a", encoding="utf-8") as f:
                            f.write(f"\n## {datetime.datetime.now()} [多模態採集]\n- **分析內容**: {response.text}\n")
                    else:
                        st.info("⚠️ 檔案已物理存檔至 media 資料夾，但未配置 API Key 進行分析。")
                except Exception as e:
                    st.error(f"❌ 跨模態解析失敗: {str(e)}")

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
    st.title("📖 智慧答案之書：多模態啟示")
    st.markdown("---")
    
    if st.button("🔮 擷取靈魂啟示"):
        # 1. 準備啟示池
        text_pool = []
        img_pool = []
        audio_pool = []
        
        # 2. 物理打撈：從日誌與媒體資料夾中獲取素材
        if os.path.exists(LOG_DIR):
            for fn in os.listdir(LOG_DIR):
                if fn.endswith('.md'):
                    with open(os.path.join(LOG_DIR, fn), "r", encoding="utf-8") as f:
                        text_pool.extend([l.strip() for l in f.readlines() if len(l.strip()) > 10])
        
        if os.path.exists(MEDIA_DIR):
            for fn in os.listdir(MEDIA_DIR):
                full_p = os.path.join(MEDIA_DIR, fn)
                if fn.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_pool.append(full_p)
                elif fn.lower().endswith(('.mp3', '.wav', '.ogg')):
                    audio_pool.append(full_p)

        # 3. 隨機觸發啟示邏輯
        st.subheader("⚓ 來自虛空的指引")
        
        # 隨機抽取一段文字
        if text_pool:
            revelation = random.choice(text_pool)
            st.info(f"📜 **文字啟示：**\n\n{revelation}")
        else:
            st.info("📜 **文字啟示：**\n\n『航道尚未開啟，請先在開發頻道留下足跡。』")

        # 隨機抽取一張圖片 (50% 機率出現)
        if img_pool and random.random() > 0.5:
            st.image(random.choice(img_pool), caption="🖼️ 過去的視覺殘影", use_column_width=True)
            
        # 隨機抽取一段音訊 (30% 機率出現)
        if audio_pool and random.random() > 0.7:
            target_audio = random.choice(audio_pool)
            st.write(f"🎵 **聽見迴聲：** {os.path.basename(target_audio)}")
            st.audio(target_audio)

    st.divider()
    st.caption("※ 答案之書會隨機連結你的開發記憶，幫助你找回《餘燼航路》的初心。")
elif channel == "🛠️ 管理部署":
    st.title("🛠️ 專案管理與同步")
    st.markdown("---")
    
    # 1. 燃料庫 (.env) 配置：直接物理寫入 Token 與 Key
    with st.expander("🔑 燃料庫 (.env) 配置"):
        st.info("若顯示『未配置 github_token』，請在此輸入並點擊物理寫入。")
        # 讀取當前環境變數
        curr_ai = os.getenv("ai_key", "")
        curr_gh = os.getenv("github_token", "")
        
        new_ai = st.text_input("填入 ai_key", value=curr_ai, type="password")
        new_gh = st.text_input("填入 github_token", value=curr_gh, type="password")
        
        if st.button("🚀 物理寫入 .env 燃料庫"):
            # 直接寫入檔案以確保持久化
            with open(BASE_PATH / ".env", "w", encoding="utf-8") as f:
                f.write(f"ai_key={new_ai}\ngithub_token={new_gh}\n")
            # 同步更新當前運行的環境變數，避免重啟
            os.environ["ai_key"] = new_ai
            os.environ["github_token"] = new_gh
            st.success("✅ 燃料庫已重新注入，環境變數已即時刷新！")

    # 2. 專案修改、新增與刪除
    with st.expander("📝 專案架構管理"):
        st.subheader(f"當前專案：{current_p_name}")
        
        # 修改當前專案路徑
        new_path = st.text_input("Godot 腳本資料夾路徑", config.get("local_script_path", ""))
        new_prompt = st.text_area("AI 架構師公約 (System Prompt)", config.get("prompt", ""))
        
        if st.button("💾 儲存專案修改"):
            PROJECTS[current_p_name]["local_script_path"] = new_path
            PROJECTS[current_p_name]["prompt"] = new_prompt
            save_config(PROJECTS)
            st.success("專案設定已同步至 projects_config.json")

        st.divider()
        
        # 新增專案
        new_p_name = st.text_input("➕ 建立新專案名稱")
        if st.button("🏗️ 啟動新專案架構"):
            if new_p_name and new_p_name not in PROJECTS:
                PROJECTS[new_p_name] = {
                    "theme_color": "#D4AF37", 
                    "bg_color": "#1A1A1A", 
                    "prompt": "你是架構師", 
                    "local_script_path": "", 
                    "keys_list": []
                }
                save_config(PROJECTS)
                st.rerun()
        
        # 刪除專案 (危險區)
        st.divider()
        if st.button("🗑️ 刪除當前專案 (慎用)"):
            if len(PROJECTS) > 1:
                # 移除配置與實體資料夾
                del PROJECTS[current_p_name]
                save_config(PROJECTS)
                shutil.rmtree(os.path.join(DATA_ROOT, current_p_name), ignore_errors=True)
                st.warning(f"已物理刪除專案：{current_p_name}")
                st.rerun()
            else:
                st.error("至少需保留一個核心專案。")

    st.divider()
    
    # 3. 雲端進化同步 (Git Push)
    st.subheader("🚀 雲端進化同步 (Git Push)")
    
    # 檢查 Token 狀態
    if not os.getenv("github_token"):
        st.error("⚠️ 偵測不到 GitHub Token，同步功能已鎖定。")
    
    commit_msg = st.text_input("進化紀錄訊息 (Commit Message)", 
                             value=f"v{datetime.datetime.now().strftime('%m%d')} 小白龍架構進化")
    
    if st.button("🔥 啟動全域同步"):
        if not os.getenv("github_token"):
            st.error("請先在上方寫入 github_token")
        else:
            with st.spinner("正在穿越虛空同步至 GitHub..."):
                # 執行自癒型同步函數
                success, msg = secure_auto_push(commit_msg)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)