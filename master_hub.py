import json
import streamlit as st
import os
import requests
import google.generativeai as genai
import subprocess
import datetime
import random
import shutil
import PyPDF2
from PIL import Image
from dotenv import load_dotenv
from pathlib import Path

# ==========================================
# 核心開發公約 v3.3.0 - 隱私防禦與路徑自癒
# 認證：小白龍 - 核心邏輯架構師
# ==========================================

# --- 1. 物理路徑定義 (全域統一座標) ---
DATA_ROOT = "all_projects" 
LOG_DIR = os.path.join(DATA_ROOT, "logs")      
MEDIA_DIR = os.path.join(DATA_ROOT, "media")   
CONFIG_FILE = os.path.join(DATA_ROOT, "projects_config.json")
BASE_PATH = Path(__file__).resolve().parent

# 加載環境變數
load_dotenv(dotenv_path=BASE_PATH / ".env")
ai_key = os.getenv("ai_key")
github_token = os.getenv("github_token")

# --- 2. 環境自癒與系統初始化 ---
def init_system():
    """
    自動導航修復版：
    1. 讀取現有 JSON。
    2. 掃描 all_projects 資料夾下的實體子目錄。
    3. 如果發現有資料夾不在 JSON 裡，自動將其掛載回來。
    """
    if not os.path.exists(DATA_ROOT): 
        os.makedirs(DATA_ROOT)
    
    # --- [1] 載入現有配置 ---
    projects_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                projects_data = json.load(f)
        except Exception as e:
            print(f"⚠️ 讀取設定檔異常: {e}")

    # --- [2] 掃描實體資料夾 ---
    # 排除 logs, media 這些系統資料夾
    excluded_folders = ['logs', 'media', '__pycache__', '.git']
    
    # 遍歷 all_projects 裡的所有資料夾
    found_folders = [f for f in os.listdir(DATA_ROOT) 
                     if os.path.isdir(os.path.join(DATA_ROOT, f)) and f not in excluded_folders]
    
    # --- [3] 比對並修復座標 ---
    updated = False
    for folder in found_folders:
        if folder not in projects_data:
            # 發現失蹤的專案資料夾，自動建立基礎座標
            projects_data[folder] = {
                "theme_color": "#4A90E2", # 預設藍色
                "bg_color": "#1A1A1A",
                "prompt": f"從實體資料夾 {folder} 自動恢復的專案",
                "local_script_path": "",
                "keys_list": []
            }
            updated = True
            print(f"✅ 成功打撈失蹤專案：{folder}")

    # --- [4] 如果 JSON 為空且沒掃描到資料夾，才建立預設「餘燼航路」 ---
    if not projects_data:
        projects_data = {"餘燼航路": {"theme_color": "#D4AF37", "bg_color": "#1A1A1A", "prompt": "你是架構師", "local_script_path": "", "keys_list": []}}
        updated = True

    # --- [5] 存檔 ---
    if updated:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(projects_data, f, indent=4, ensure_ascii=False)
            
    return projects_data

def save_config(projects_data):
    """保存專案配置到實體硬碟"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(projects_data, f, indent=4, ensure_ascii=False)

# --- 3. 安全同步系統 (Git 保險箱) ---
def secure_auto_push(commit_message):
    """
    自癒型同步系統 v3.0：
    1. 強制排除金鑰 JSON。
    2. 自動清理 Git 快取防止『肥回來』。
    3. 保持媒體與日誌同步。
    """
    try:
        # [1] 身份動態識別
        user_email = os.getenv("git_email", "zzz961011@gmail.com")
        user_name = os.getenv("git_name", "zzz961011")
        subprocess.run(["git", "config", "--global", "user.email", user_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user_name], check=True)

        if not os.path.exists(BASE_PATH / ".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", "https://github.com/a114182134-byte/GAME.git"], check=True)

        # [2] 建立防禦壁壘 (.gitignore) - 核心修正
        # 強制加入排除 JSON 的規則，防止金鑰上傳
        ignore_content = [
            ".env",
            "__pycache__/",
            "*.pyc",
            ".streamlit/",
            "*.json",               # 排除根目錄所有 JSON
            "all_projects/*.json",   # 排除專案資料夾內的 JSON
            "all_projects/projects_config.json" # 二重保險
        ]
        with open(BASE_PATH / ".gitignore", "w", encoding="utf-8") as f: 
            f.write("\n".join(ignore_content))

        # [3] 執行物理脫離 (這行能解決妳說的「肥回來」問題)
        # 強制從 Git 的暫存區移除所有 JSON (但不刪除妳電腦的檔案)
        subprocess.run(["git", "rm", "-r", "--cached", "*.json", "--ignore-unmatch"], capture_output=True)
        subprocess.run(["git", "rm", "-r", "--cached", "all_projects/*.json", "--ignore-unmatch"], capture_output=True)

        token = os.getenv("github_token")
        if not token:
            return False, "❌ 未配置 github_token，燃料不足無法發射。"

        repo_url = f"https://{token}@github.com/a114182134-byte/GAME.git"

        # [4] 執行安全同步
        subprocess.run(["git", "add", "."], check=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if status:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        st.caption("🔄 正在嘗試與遠端航道對接 (Pull Rebase)...")
        pull_res = subprocess.run(["git", "pull", repo_url, "main", "--rebase"], capture_output=True, text=True)
        
        if pull_res.returncode != 0:
            return False, f"❌ 航道衝突！請手動處理：\n{pull_res.stderr}"

        push_res = subprocess.run(["git", "push", repo_url, "main"], capture_output=True, text=True)
        
        if push_res.returncode == 0:
            return True, "✅ 航道對接成功！日誌與媒體已送達，私密 JSON 已過濾。"
        else:
            return False, f"❌ 推送失敗：{push_res.stderr}"

    except Exception as e:
        return False, f"❌ 系統自癒失敗: {str(e)}"

# --- 4. 啟動系統 ---
# 確保每次執行都會抓到最新的專案狀態
PROJECTS = init_system()

# 3. UI 構建
st.set_page_config(page_title="小白龍核心母站 v3.2.1", layout="wide", page_icon="⚓")
PROJECTS = init_system()

# --- [側邊欄：核心中控台] ---
with st.sidebar:
    st.title("⚙️ 核心中控台")
    
    # 1. 優先獲取專案名稱
    current_p_name = st.selectbox("核心專案切換", list(PROJECTS.keys()))
    config = PROJECTS[current_p_name]
    
    st.divider()
    
    # 2. 金鑰管理邏輯
    st.subheader("🔑 金鑰管理")
    saved_keys = config.get("keys_list", [])
    sel_key = st.selectbox("記憶清單", ["手動輸入"] + saved_keys)
    input_key = st.text_input("API Key", value="" if sel_key == "手動輸入" else sel_key, type="password")
    
    if st.button("🔐 記憶鎖定"):
        if input_key:
            # ✨ 核心自癒：點擊瞬間立即配置，確保後續頻道調用不中斷
            try:
                genai.configure(api_key=input_key)
                st.session_state.active_key = input_key
                
                if input_key not in saved_keys:
                    PROJECTS[current_p_name].setdefault("keys_list", []).append(input_key)
                    save_config(PROJECTS)
                
                st.success("✅ Gemini 2.5 Flash 引擎燃料注入成功")
            except Exception as e:
                st.error(f"❌ 引擎初始化失敗：{str(e)}")

    # 3. 指定真實 2.5 Flash 引擎
    # 3. 引擎規格與自動對接
    st.divider()
    st.subheader("🤖 引擎規格")
    
    # ✨ 這裡的清單文字必須與下方 model_map 的 Key 完全一模一樣
    AI_MODEL_DISPLAY = st.selectbox("核心版本", [
        "Gemini 2.5 Flash ", 
        "Gemini 2.0 Flash ", 
        "Gemini 3.1 Flash ",
        "Gemini Flash "
    ])
    
    # ✨ 建立精準映射，避免 KeyError
    # ✨ 根據 2026 掃描報告精確對接
    model_map = {
        "Gemini 2.5 Flash ": "models/gemini-2.5-flash", 
        "Gemini 2.0 Flash ": "models/gemini-2.0-flash", 
        "Gemini 3.1 Flash ": "models/gemini-3.1-flash-lite",
        "Gemini Flash ": "models/gemini-flash-latest"
    }
    
    # 從字典獲取對應的 API 字串
    AI_MODEL = model_map[AI_MODEL_DISPLAY]
    
    # 從字典獲取對應的 API 字串
    AI_MODEL = model_map[AI_MODEL_DISPLAY]
    
    channel = st.radio("功能頻道", [
        "📸 素材打撈 (Media)", "🔧 齒輪重組 (Script)", 
        "🧪 結構修復 (Patch)", "🔮 虛空啟示 (Oracle)",
        "📜 航行日誌 (Log)", "📜 航道啟示錄 (Oracle's Compass)",
        "📚 封存圖書館 (Library)", "⚙️ 核心維護 (System)"
    ])

# ==========================================
# 核心路徑動態定義 (解決 NameError 的關鍵)
# ==========================================

# 獲取當前有效 Key
FINAL_KEY = st.session_state.get("active_key", input_key)
if FINAL_KEY: 
    genai.configure(api_key=FINAL_KEY)

# ✨ 這裡才開始定義路徑，因為此時 current_p_name 絕對有值
LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
ARCHIVE_DIR = os.path.join(DATA_ROOT, current_p_name, "archives") # 🏛️ 封存圖書館路徑

# 物理空間自癒建立
for d in [LOG_DIR, MEDIA_DIR, ARCHIVE_DIR]: 
    if not os.path.exists(d): 
        os.makedirs(d)
        print(f"🛠️ 物理空間已重構：{d}")
if channel == "📸 素材打撈 (Media)":
    st.title("📸 殘留影像與波形打撈")
    st.markdown("---")

    # ⚡ 核心優化：發射站與設備識別
    ua = st.context.headers.get("User-Agent", "").lower()
    dev_type = "行動裝置" if "mobile" in ua else "核心主機"
    
    col_loc, col_info = st.columns([1, 2])
    with col_loc:
        # 地點選擇，影響後續所有存檔的前綴
        station_origin = st.selectbox("📍 當前發射站", ["總部 (acer)", "台北站", "新竹站", "台南站"])
    with col_info:
        st.caption(f"📡 偵測設備類型：`{dev_type}`")
        st.caption(f"🌍 接入網址：`{st.context.headers.get('Host')}`")

    # 1. 指令輸入區域
    u_text = st.text_area("🧠 分析指令 (或用語音輸入後自動填充)", placeholder="描述你的開發需求、二姊的畫作靈感...", help="這些文字會連同媒體一起交給 AI 處理。")
    
    st.subheader("🎤 語音靈感捕捉")
    from audio_recorder_streamlit import audio_recorder
    audio_bytes = audio_recorder(
        text=f"來自【{station_origin}】的通訊 (點擊開始/停止)",
        recording_color="#e74c3c",
        neutral_color="#D4AF37",
        icon_name="microphone",
        icon_size="2x",
    )

    # ---------------------------------------------------------
    # ⚡ [自動入庫監聽器] - 錄音攔截
    # ---------------------------------------------------------
    if audio_bytes:
        if "last_mic_data" not in st.session_state or st.session_state.last_mic_data != audio_bytes:
            timestamp = datetime.datetime.now().strftime('%m%d_%H%M%S')
            mic_name = f"mic_{station_origin}_{timestamp}.wav"
            mic_path = os.path.join(MEDIA_DIR, mic_name)
            
            with open(mic_path, "wb") as f:
                f.write(audio_bytes)
            
            st.session_state.last_mic_data = audio_bytes 
            st.session_state.current_mic_path = mic_path
            st.sidebar.success(f"🎙️ 聲波已從 {station_origin} 入庫")

        st.write(f"🎵 來自 **{station_origin}** 的即時聲波：")
        st.audio(audio_bytes, format="audio/wav")

    st.divider()
    
    # 2. 檔案上傳區 (核心改進：強化圖片存檔與預覽)
    col1, col2 = st.columns(2)
    with col1:
        u_img = st.file_uploader("🖼️ 影像打撈 (二姊的畫作)", type=['png', 'jpg', 'jpeg', 'webp'])
        if u_img:
            # 檔名處理：[地點]_[原始檔名]
            img_filename = f"{station_origin}_{u_img.name}"
            img_path = os.path.join(MEDIA_DIR, img_filename)
            
            from PIL import Image
            img = Image.open(u_img)
            st.image(img, caption="🚀 待上傳影像預覽", use_column_width=True)
            
            if not os.path.exists(img_path):
                img.save(img_path)
                st.sidebar.success(f"🖼️ 影像已存入 {station_origin} 倉庫")

    with col2:
        u_audio = st.file_uploader("🎵 音訊打撈 (BGM/音樂素材)", type=['mp3', 'wav', 'ogg', 'm4a'])
        if u_audio:
            audio_filename = f"{station_origin}_{u_audio.name}"
            a_path = os.path.join(MEDIA_DIR, audio_filename)
            if not os.path.exists(a_path):
                with open(a_path, "wb") as f:
                    f.write(u_audio.getbuffer())
                st.sidebar.success(f"🎵 音訊已存入 {station_origin} 倉庫")
            st.audio(u_audio)

    st.markdown("---")
    
    # 3. 執行 AI 分析按鈕 (強化日誌連結能力)
    if st.button("🚀 啟動跨模態解析 (AI 思考)"):
        if not (u_img or u_audio or u_text or audio_bytes):
            st.warning("📡 偵測不到感測器數據，請先提供素材或錄音。")
        else:
            with st.spinner(f"正在連線至 {station_origin} 進行解析..."):
                now = datetime.datetime.now()
                timestamp = now.strftime('%m%d_%H%M%S')
                log_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                
                model = genai.GenerativeModel(AI_MODEL)
                content_payload = []
                
                # 處理上傳的圖片
                img_ref_name = "無"
                if u_img:
                    img_ref_name = f"{station_origin}_{u_img.name}"
                    img = Image.open(u_img)
                    content_payload.append(img)
                
                # 處理即時語音
                mic_ref_name = f"mic_{station_origin}_{timestamp}.wav" if audio_bytes else "無"
                if audio_bytes:
                    content_payload.append({"mime_type": "audio/wav", "data": audio_bytes})
                
                # 處理上傳音訊
                audio_ref_name = f"{station_origin}_{u_audio.name}" if u_audio else "無"
                if u_audio:
                    u_audio.seek(0) # 重新讀取
                    content_payload.append({"mime_type": u_audio.type, "data": u_audio.read()})

                final_prompt = u_text if u_text else "請分析以上媒體內容並整理成日誌。"
                content_payload.insert(0, final_prompt)

                try:
                    if FINAL_KEY:
                        response = model.generate_content(content_payload)
                        st.markdown(f"### 📝 AI 綜合分析報告 (來源：{station_origin})")
                        st.write(response.text)
                        
                        # --- 核心邏輯：寫入航行日誌 (關鍵在於寫入檔名，日誌頻道才能自動顯像) ---
                        log_file = os.path.join(LOG_DIR, f"log_{timestamp}.md")
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(f"# 航行紀錄 - {log_time_str}\n\n")
                            f.write(f"### 📍 來源發射站：{station_origin} ({dev_type})\n")
                            f.write(f"- **指令核心**: {u_text if u_text else '自動感測'}\n")
                            
                            # 寫入這幾行，日誌頻道就能自動播放音訊和顯示二姊的圖
                            if u_img: f.write(f"- **關聯影像**: {img_ref_name}\n")
                            if audio_bytes: f.write(f"- **關聯語音**: {mic_ref_name}\n")
                            if u_audio: f.write(f"- **關聯音訊**: {audio_ref_name}\n")
                            
                            f.write(f"\n#### 🧠 AI 解析結果\n{response.text}\n")
                            f.write("\n---\n")
                        st.success(f"✅ 日誌已寫入：log_{timestamp}.md")
                    else:
                        st.info("⚠️ 檔案已物理存檔，但 API Key 未配置。")
                except Exception as e:
                    st.error(f"❌ 解析引擎異常: {str(e)}")

elif channel == "🔧 齒輪重組 (Script)":
    st.title("🔧 邏輯齒輪精密重組")
    st.caption("🔍 模式：精密重構 — 適合增加新功能、提升代碼效能與可讀性")
    st.markdown("---")

    # --- 1. 外部物資打撈區 (檔案拖入) ---
    with st.expander("📥 外部腳本快速打撈 (拖入檔案)", expanded=False):
        uploaded_files = st.file_uploader(
            "拖入要加入專案的腳本 (.gd, .py, .json, .txt)", 
            type=['gd', 'py', 'json', 'txt'],
            accept_multiple_files=True
        )
        
        script_path = config.get("local_script_path", "")
        
        if uploaded_files and script_path:
            for uploaded_file in uploaded_files:
                content = uploaded_file.read().decode("utf-8")
                st.text(f"📄 偵測到檔案：{uploaded_file.name}")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"💾 存入專案", key=f"save_upload_{uploaded_file.name}"):
                        target_full_path = os.path.join(script_path, uploaded_file.name)
                        with open(target_full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        st.success(f"已存入：{uploaded_file.name}")
                        st.rerun() 
                with col2:
                    st.caption(f"目標路徑：{script_path}")

    st.markdown("---")

    # --- 2. 本地檔案編輯與 AI 分析區 ---
    if script_path and os.path.exists(script_path):
        files = [f for f in os.listdir(script_path) if f.endswith('.gd') or f.endswith('.py')]
        
        if not files:
            st.info("📂 資料夾中尚無腳本檔案，請拖入檔案或檢查路徑。")
        else:
            selected_file = st.selectbox("📂 選擇優化目標", files, key="script_select")
            file_full_path = os.path.join(script_path, selected_file)
            
            with open(file_full_path, "r", encoding="utf-8") as f:
                current_code = f.read()

            col_e, col_a = st.columns([1, 1])
            with col_e:
                st.subheader("📝 代碼編輯器")
                new_code = st.text_area("直接編輯並儲存", value=current_code, height=500)
                if st.button("💾 儲存物理修改", key="save_script"):
                    with open(file_full_path, "w", encoding="utf-8") as f:
                        f.write(new_code)
                    st.success(f"✅ {selected_file} 物理覆寫成功！")

            with col_a:
                st.subheader("💡 AI 優化建議")
                if st.button("🚀 啟動邏輯進化分析"):
                    model = genai.GenerativeModel(AI_MODEL)
                    prompt = f"你是一位資深 Godot 專家。請分析此腳本並提供重構建議，使其更符合最佳實踐，並提升效能。\n\n代碼：\n{current_code}"
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.last_script_advice = response.text

                # --- 3. 報告產出：系統檔案總管模式 (核心修改區) ---
                if "last_script_advice" in st.session_state:
                    st.write("---")
                    st.subheader("📥 報告產出 (檔案總管模式)")
                    
                    if st.button("🚩 呼喚檔案總管並儲存進化報告", use_container_width=True):
                        try:
                            # 呼叫 Windows 系統視窗
                            import tkinter as tk
                            from tkinter import filedialog
                            
                            root = tk.Tk()
                            root.withdraw()
                            root.attributes('-topmost', True) # 確保視窗跳到最前面
                            
                            # 預設檔名包含時間戳
                            timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
                            default_name = f"Refactor_{selected_file.split('.')[0]}_{timestamp}.pdf"
                            
                            # 彈出另存新檔視窗
                            save_path = filedialog.asksaveasfilename(
                                defaultextension=".pdf",
                                filetypes=[("PDF files", "*.pdf")],
                                initialfile=default_name,
                                title="小白龍架構師：請核定報告封存位置"
                            )
                            root.destroy()

                            if save_path:
                                from weasyprint import HTML
                                with st.spinner("正在將邏輯齒輪鍛造為實體文件..."):
                                    html_content = f"""
                                    <html>
                                        <head><style>
                                            body {{ font-family: sans-serif; line-height: 1.6; padding: 30px; }} 
                                            h1 {{ color: #D4AF37; border-bottom: 2px solid #D4AF37; }} 
                                            .info {{ color: #666; font-size: 12px; }}
                                        </style></head>
                                        <body>
                                            <h1>{selected_file} 邏輯進化報告</h1>
                                            <p class="info">生成時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                            <hr>
                                            <div>{st.session_state.last_script_advice.replace('\n', '<br>')}</div>
                                            <p style="margin-top:50px; font-size:10px; color:#999;">由 小白龍 19GB 母站生成 | 座標：屏東九如發射站</p>
                                        </body>
                                    </html>
                                    """
                                    HTML(string=html_content).write_pdf(save_path)
                                    st.success(f"✅ 報告已成功封存至：{save_path}")
                            else:
                                st.warning("⚠️ 已取消物理儲存動作。")
                        except Exception as e:
                            st.error(f"檔案總管調用失敗：{e}")
    else:
        st.error("❌ 腳本路徑未配置。請至核心設定配置 local_script_path。")

elif channel == "🧪 結構修復 (Patch)":
    st.title("🧪 檔案結構物理修復 (PDF 知識導入版)")
    st.caption("🚨 模式：結構補丁 — 支援參考 PDF 並自動導出修復報告")
    st.markdown("---")

    script_path = config.get("local_script_path", "")
    if script_path and os.path.exists(script_path):
        # 獲取腳本清單
        files = [f for f in os.listdir(script_path) if f.endswith('.gd') or f.endswith('.py')]
        if not files:
            st.info("📂 腳本夾內空無一物，請先從「齒輪重組」打撈物資。")
        else:
            selected_file = st.selectbox("🎯 選擇待修補目標", files, key="patch_select")
            file_full_path = os.path.join(script_path, selected_file)
            
            with open(file_full_path, "r", encoding="utf-8") as f:
                current_code = f.read()

            # --- 1. 知識注入 (PDF) ---
            st.subheader("📋 導入維修手冊 (PDF)")
            uploaded_pdf = st.file_uploader("上傳之前的 AI 診斷報告或參考文件", type=['pdf'])
            pdf_knowledge = ""
            if uploaded_pdf:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in pdf_reader.pages:
                    pdf_knowledge += page.extract_text()
                st.success(f"✅ PDF 知識已注入緩衝區 ({len(pdf_knowledge)} 字)")

            st.divider()

            # --- 2. 修復需求描述 ---
            st.subheader("🔥 物理修復執行")
            fix_instr = st.text_area("描述修復需求", placeholder="例如：根據 PDF 第 3 頁建議，修復 harpoon.gd 的 null 引用...")

            # --- 3. 執行物理重構與彈窗儲存報告 ---
            if st.button("🛠️ 執行物理重構與生成報告", type="primary", use_container_width=True):
                if not fix_instr:
                    st.error("❌ 請輸入修復指令，否則維修工無法動工。")
                else:
                    try:
                        # 先呼叫檔案總管，讓妳選位置，選好才動工
                        import tkinter as tk
                        from tkinter import filedialog
                        
                        root = tk.Tk()
                        root.withdraw()
                        root.attributes('-topmost', True)
                        
                        timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
                        default_report_name = f"Patch_Report_{selected_file.split('.')[0]}_{timestamp}.pdf"
                        
                        save_path = filedialog.asksaveasfilename(
                            defaultextension=".pdf",
                            filetypes=[("PDF files", "*.pdf")],
                            initialfile=default_report_name,
                            title="小白龍架構師：請核定修復報告儲存位置"
                        )
                        root.destroy()

                        # 只有在妳確認儲存路徑後，才開始消耗 19GB 記憶體進行 AI 運算
                        if save_path:
                            with st.spinner("戰地維修工正在閱讀 PDF 並重新鍛造代碼..."):
                                model = genai.GenerativeModel(AI_MODEL)
                                full_prompt = f"你現在是戰地維修工。參考手冊內容：\n{pdf_knowledge}\n\n指令：{fix_instr}\n\n請根據手冊與指令修復此代碼，僅輸出純代碼，不要有說明。\n代碼：\n{current_code}"
                                
                                response = model.generate_content(full_prompt)
                                clean_code = response.text.replace("```gdscript", "").replace("```", "").strip()
                                
                                # 1. 執行物理覆寫 (更新腳本)
                                with open(file_full_path, "w", encoding="utf-8") as f:
                                    f.write(clean_code)
                                st.success(f"✅ {selected_file} 結構修補完成！代碼已物理更新。")
                                
                                # 2. 生成 PDF 修復報告
                                from weasyprint import HTML
                                html_content = f"""
                                <html>
                                    <head><style>
                                        body {{ font-family: sans-serif; padding: 25px; line-height: 1.6; }}
                                        h1 {{ color: #D4AF37; border-bottom: 2px solid #D4AF37; }}
                                        .box {{ background: #f9f9f9; padding: 15px; border-left: 5px solid #D4AF37; margin: 10px 0; }}
                                        pre {{ background: #222; color: #eee; padding: 15px; font-size: 12px; }}
                                    </style></head>
                                    <body>
                                        <h1>結構修復報告：{selected_file}</h1>
                                        <p><b>生成時間:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                        <div class="box"><b>修復指令：</b><br>{fix_instr}</div>
                                        <hr>
                                        <h2>修復後代碼截圖 (前 1500 字)：</h2>
                                        <pre>{clean_code[:1500]}</pre>
                                        <p style="text-align: right; font-size: 10px; color: #666; margin-top: 30px;">
                                            由 小白龍 19GB 核心母站認證 | 屏東九如發射站
                                        </p>
                                    </body>
                                </html>
                                """
                                HTML(string=html_content).write_pdf(save_path)
                                st.success(f"📄 修復報告已成功封存至：{save_path}")
                        else:
                            st.warning("⚠️ 已取消修復動作，未改動任何實體檔案。")

                    except Exception as e:
                        st.error(f"維修過程發生故障: {e}")
    else:
        st.error("❌ 找不到腳本路徑，請先確認 local_script_path 是否正確。")
elif channel == "🔮 虛空啟示 (Oracle)":
    st.title("🔮 虛空啟示：全域架構諮詢")
    st.caption("🤖 AI 將分析當前專案的所有腳本 (.gd) 與日誌 (.md) 來回答妳的問題")
    st.markdown("---")

    # 1. 自動打撈全域數據
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    script_path = config.get("local_script_path", "")
    
    with st.expander("📂 檢視 AI 當前載入的知識庫範圍"):
        all_files = []
        # 收集 MD
        if os.path.exists(CURRENT_LOG_DIR):
            md_files = [f for f in os.listdir(CURRENT_LOG_DIR) if f.endswith(".md")]
            all_files.extend([f"日誌: {f}" for f in md_files])
        # 收集 GD
        if script_path and os.path.exists(script_path):
            gd_files = [f for f in os.listdir(script_path) if f.endswith(".gd")]
            all_files.extend([f"腳本: {f}" for f in gd_files])
        st.write(all_files if all_files else "目前無載入任何檔案")

    # 2. 諮詢介面
    st.subheader("❓ 向架構導師提問")
    user_query = st.text_area("例如：『根據目前的魚叉腳本和日誌紀錄，我該如何優化海上戰鬥的節奏？』", height=150)
    
    # 3. 額外導入 PDF 手冊 (可選)
    uploaded_pdf = st.file_uploader("若有特定的診斷報告 PDF，也可一併導入參考", type=['pdf'])

    if st.button("🌌 啟動虛空連結"):
        if not user_query:
            st.warning("請先輸入妳的疑問。")
        elif not FINAL_KEY:
            st.error("❌ 金鑰未配置。")
        else:
            with st.spinner("AI 正在翻閱所有日誌與腳本中..."):
                # 提取 PDF 內容
                pdf_text = ""
                if uploaded_pdf:
                    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()

                # 提取所有的 MD 和 GD 內容 (建立 Context)
                context_data = []
                # 讀取 MD
                if os.path.exists(CURRENT_LOG_DIR):
                    for f in os.listdir(CURRENT_LOG_DIR):
                        if f.endswith(".md"):
                            with open(os.path.join(CURRENT_LOG_DIR, f), "r", encoding="utf-8") as file:
                                context_data.append(f"--- 日誌 {f} ---\n{file.read()}")
                # 讀取 GD
                if script_path and os.path.exists(script_path):
                    for f in os.listdir(script_path):
                        if f.endswith(".gd"):
                            with open(os.path.join(script_path, f), "r", encoding="utf-8") as file:
                                context_data.append(f"--- 腳本 {f} ---\n{file.read()}")

                full_context = "\n\n".join(context_data)
                
                # 呼叫 AI
                model = genai.GenerativeModel(AI_MODEL)
                oracle_prompt = f"""
                你是一位資深的遊戲開發架構師，專精於 Godot 引擎與跨媒體敘事。
                以下是專案《{current_p_name}》的完整開發數據（包含日誌與腳本內容）以及參考 PDF。
                
                [參考數據]
                {full_context}
                
                [PDF 補充資訊]
                {pdf_text}
                
                [使用者問題]
                {user_query}
                
                請根據以上資訊，給出具備專業架構眼光、邏輯嚴密且符合開發現況的建議。
                """
                
                try:
                    response = model.generate_content(oracle_prompt)
                    st.markdown("### 🔮 啟示內容：")
                    st.write(response.text)
                    
                    # ✨ 新增：諮詢結果導出 PDF
                    if st.button("📥 導出此份諮詢建議 (PDF)"):
                        from weasyprint import HTML
                        pdf_name = f"Oracle_{datetime.datetime.now().strftime('%m%d_%H%M')}.pdf"
                        html_c = f"<h1>開發諮詢建議</h1><p>問題：{user_query}</p><hr><div>{response.text.replace('\n', '<br>')}</div>"
                        HTML(string=html_c).write_pdf(pdf_name)
                        st.download_button("💾 下載 PDF 啟示錄", open(pdf_name, "rb"), file_name=pdf_name)
                        
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 核心過熱，請等待 30 秒後再點擊。")
                    else:
                        st.error(f"連線中斷: {e}")

    st.divider()
    st.caption("※ 答案之書會隨機連結你的開發記憶，幫助你找回《餘燼航路》的初心。")
elif channel == "📜 航行日誌 (Log)":
    st.title("📜 舊日航行完整紀錄")
    st.markdown("---")
    
    # 定位實體路徑
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    CURRENT_MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")

    # =========================================================
    # 🎨 視覺觀測窗：展示二姊的畫作與素材 (保持原樣)
    # =========================================================
    if os.path.exists(CURRENT_MEDIA_DIR):
        all_imgs = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if all_imgs:
            with st.expander("🎨 航道視覺觀測窗 (二姊的畫作庫)", expanded=True):
                st.caption(f"目前存放於：{CURRENT_MEDIA_DIR}")
                img_cols = st.columns(3)
                sorted_imgs = sorted(all_imgs, key=lambda x: os.path.getmtime(os.path.join(CURRENT_MEDIA_DIR, x)), reverse=True)
                for idx, img_name in enumerate(sorted_imgs[:6]):
                    with img_cols[idx % 3]:
                        st.image(os.path.join(CURRENT_MEDIA_DIR, img_name), use_column_width=True, caption=img_name)
    
    # =========================================================
    # 🚀 核心功能：全專案大數據彙整區 (彈窗儲存進化)
    # =========================================================
    st.info(f"📂 正在監控專案：{current_p_name} | 準備進行跨城市數據彙整")
    
    # 移除原本的 text_input，直接改為按鈕啟動
    if st.button("📊 生成全專案 AI 總結報告 (整合所有 MD & 素材)", type="primary", use_container_width=True):
        if not FINAL_KEY:
            st.error("❌ 核心金鑰失效，請更新 API Key。")
        else:
            try:
                # 1. 先呼喚檔案總管，讓妳選位置，選好才開始運算
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
                default_report_name = f"{current_p_name}_全案報告_{timestamp}.pdf"
                
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=default_report_name,
                    title="小白龍架構師：請核定全域開發報告儲存位置"
                )
                root.destroy()

                # 只有確認路徑後，才動用 19GB 核心進行數據打撈
                if save_path:
                    with st.spinner("正在打撈台北、新竹、台南發射站數據並精煉中..."):
                        all_contents = []
                        # 抓取日誌
                        if os.path.exists(CURRENT_LOG_DIR):
                            for log_f in sorted(os.listdir(CURRENT_LOG_DIR)):
                                if log_f.endswith(".md"):
                                    with open(os.path.join(CURRENT_LOG_DIR, log_f), "r", encoding="utf-8") as f:
                                        all_contents.append(f"### 文件: {log_f}\n{f.read()}")
                        
                        # 媒體統計
                        if os.path.exists(CURRENT_MEDIA_DIR):
                            media_files = os.listdir(CURRENT_MEDIA_DIR)
                            waves = [f for f in media_files if f.endswith(".wav")]
                            imgs_count = [f for f in media_files if f.lower().endswith(('.png', '.jpg', '.webp'))]
                            all_contents.append(f"\n### 媒體庫統計\n已入庫語音: {len(waves)} 筆\n已入庫二姊畫作/素材: {len(imgs_count)} 筆")

                        full_context = "\n\n".join(all_contents)
                        
                        # AI 彙整
                        model = genai.GenerativeModel(AI_MODEL)
                        summary_prompt = f"你是一位資深開發助手。請根據以下數據為《{current_p_name}》整理專業報告。數據源：\n{full_context}"
                        
                        response = model.generate_content(summary_prompt)
                        ai_report = response.text
                        
                        # 轉 PDF
                        from weasyprint import HTML
                        html_style = f"""
                        <html><body style="font-family: sans-serif; padding: 30px;">
                            <h1 style="color: #d4af37; border-bottom: 2px solid #d4af37;">餘燼航路：全域開發報告</h1>
                            <div style="background: #fdfaf3; padding: 20px; border: 1px solid #ddd; line-height: 1.6;">
                                {ai_report.replace('\n', '<br>')}
                            </div>
                            <p style="font-size: 10px; color: #999; margin-top: 20px;">由 小白龍 19GB 核心主機生成 | 座標：屏東九如發射站</p>
                        </body></html>
                        """
                        HTML(string=html_style).write_pdf(save_path)
                        st.success(f"✅ 全案報告已物理歸檔：{save_path}")
                else:
                    st.warning("⚠️ 已取消報告生成動作。")

            except Exception as e:
                st.error(f"❌ 彙整失敗: {str(e)}")

    st.markdown("---")
    
    # [後續建立時間線的代碼維持不變...]
elif channel == "⚙️ 核心維護 (System)":
    st.title("⚙️ 核心動力室維護")
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
        
# 刪除專案 (危險區 - 增加雙重鎖定)
        st.divider()
        
        # 使用 expander 把危險功能收納起來，避免誤觸
        with st.expander("🚨 危險區域：專案物理拆解"):
            st.warning(f"注意：此操作將物理刪除「{current_p_name}」所有資料夾與配置，且無法復原。")
            
            # 認證碼輸入框
            confirm_input = st.text_input(
                "請輸入專案名稱以解鎖刪除按鈕：", 
                placeholder=current_p_name,
                help="這是在執行物理刪除前的最後安全驗證"
            )

            # 只有認證碼正確，刪除按鈕才可被點擊 (disabled 邏輯)
            is_verified = (confirm_input == current_p_name)
            
            if st.button(
                f"🔥 確認物理刪除：{current_p_name}", 
                type="primary", 
                disabled=not is_verified,
                use_container_width=True
            ):
                if len(PROJECTS) > 1:
                    # 1. 從配置中移除
                    del PROJECTS[current_p_name]
                    save_config(PROJECTS)
                    
                    # 2. 物理刪除實體資料夾
                    project_dir = os.path.join(DATA_ROOT, current_p_name)
                    if os.path.exists(project_dir):
                        shutil.rmtree(project_dir, ignore_errors=True)
                    
                    st.toast(f"🚩 專案【{current_p_name}】已從磁區中徹底抹除", icon="🗑️")
                    st.rerun()
                else:
                    st.error("🚨 核心協議：必須保留至少一個運作中的專案。")
            
            if confirm_input and not is_verified:
                st.caption("⚠️ 認證名稱不匹配，刪除系統已鎖定。")

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
                    # 4. 🛰️ 虛空定標：模型可用性診斷 (解決 404 問題)
    st.divider()
    st.subheader("🛰️ 虛空定標診斷")
    st.caption("當出現 404 錯誤時，請啟動此雷達掃描當前 API Key 支援的精確模型名稱。")
    
    if st.button("🔍 啟動全域模型掃描"):
        # 確保使用當前鎖定的金鑰
        ACTIVE_KEY = st.session_state.get("active_key", os.getenv("ai_key"))
        
        if not ACTIVE_KEY:
            st.error("❌ 未偵測到有效金鑰，請先在側邊欄鎖定或在 .env 寫入。")
        else:
            try:
                with st.spinner("正在掃描虛空可用模型..."):
                    genai.configure(api_key=ACTIVE_KEY)
                    models = genai.list_models()
                    
                    # 篩選出支援生成內容的模型
                    available_models = [
                        m.name for m in models 
                        if 'generateContent' in m.supported_generation_methods
                    ]
                    
                    if available_models:
                        st.success(f"✅ 掃描完成！發現 {len(available_models)} 個可用航道：")
                        for m in available_models:
                            # 用 code 格式方便妳直接複製
                            st.code(m)
                        
                        st.info("💡 提示：請複製清單中的名稱（包含 models/ 前綴），更新至 model_map 中。")
                    else:
                        st.warning("⚠️ 掃描完成，但此金鑰似乎不具備任何內容生成權限。")
            except Exception as e:
                st.error(f"❌ 掃描程序崩潰：{str(e)}")
                st.info("💡 這通常代表金鑰無效或網路環境（九如節點）連結不穩。")
elif channel == "📜 航道啟示錄 (Oracle's Compass)":
    st.title("📜 航道啟示錄 (Oracle's Compass)")
    st.caption("⚓ 當妳在迷霧中失去方向，請轉動此羅盤，聽取虛空的殘響。")
    st.markdown("---")

    # 1. 虛空打撈：獲取全域腳本與日誌碎片
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    CURRENT_MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
    ARCHIVE_DIR = os.path.join(DATA_ROOT, current_p_name, "archives") 
    
    # 物理空間自癒
    if not os.path.exists(ARCHIVE_DIR): os.makedirs(ARCHIVE_DIR)

    script_path = config.get("local_script_path", "")
    knowledge_pool = []
    
    # 打撈日誌與代碼邏輯 (保持原本優良設計)
    if os.path.exists(CURRENT_LOG_DIR):
        for f in os.listdir(CURRENT_LOG_DIR):
            if f.endswith(".md"):
                with open(os.path.join(CURRENT_LOG_DIR, f), "r", encoding="utf-8") as file:
                    knowledge_pool.extend([line.strip() for line in file.readlines() if len(line.strip()) > 15])
    
    if script_path and os.path.exists(script_path):
        for f in os.listdir(script_path):
            if f.endswith(".gd"):
                with open(os.path.join(script_path, f), "r", encoding="utf-8") as file:
                    knowledge_pool.extend([line.strip() for line in file.readlines() if "func" in line or "var" in line])

    # 2. 儀式區域
    st.subheader("💡 請求今日的開發啟示")
    user_question = st.text_input("在心中默念妳的問題...", placeholder="例如：這段複雜的羅格賴加邏輯該如何收尾？")

    if st.button("🎡 撥動命運羅盤"):
        if not knowledge_pool:
            st.warning("📜 目前知識池是空的。")
        else:
            fragment = random.choice(knowledge_pool)
            with st.spinner("🚢 正在迷霧中打撈啟示..."):
                try:
                    # ✨ 核心自癒：強制校準型號字串
                    # 某些版本的 SDK 喜歡 'gemini-1.5-flash'，某些喜歡 'models/gemini-1.5-flash'
                    # 我們先嘗試妳選擇的，若失敗自動微調名稱
                    
                    target_model = AI_MODEL
                    
                    # 如果妳選的是 1.5 且之前報過 404，我們在這裡做最後的格式修正
                    if "1.5-flash" in target_model:
                        # 嘗試最原始的名稱格式
                        target_model = "gemini-1.5-flash" 

                    model = genai.GenerativeModel(target_model)
                    
                    # 增加超時設定，確保 19GB 記憶體主機不會空等
                    response = model.generate_content(
                        f"你是一位末世架構師。根據碎片『{fragment}』指引問題：{user_question}"
                    )
                    
                    # [後續顯示與 PDF 邏輯保持不變...]
                    st.info(f"『 {response.text} 』")

                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        st.error(f"❌ 404 航道遺失：系統找不到型號 '{target_model}'。")
                        st.info("💡 小白龍架構師，請嘗試在側邊欄切換另一個 1.5 版本，或檢查 SDK 是否需要更新。")
                    elif "429" in error_msg:
                        st.error("❌ 2.5 能量耗盡，請切換至 1.5 備援航道。")
                    else:
                        st.error(f"❌ 虛空連結異常：{error_msg}")
                    oracle_prompt = f"""
                    你是《餘燼航路》的古老導靈。使用者(架構師)正處於困惑中。
                    請根據這段打撈出的內容，給予一段充滿哲理、黃銅蒸氣與末世感的「答案之書」式指引。
                    [打撈碎片]: {fragment}
                    [使用者疑問]: {user_question}
                    要求：語氣冷峻但具備指引性，結尾附上一句與碎片相關的虛空叮嚀。
                    """
                    
                    response = model.generate_content(oracle_prompt)
                    
                    # 多媒體展現 (隨機顯像)
                    all_imgs = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.endswith(('.png', '.jpg', '.webp'))]
                    if all_imgs:
                        st.image(os.path.join(CURRENT_MEDIA_DIR, random.choice(all_imgs)), width=300, caption="🖼️ 啟示顯像")

                    all_audios = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.endswith(('.wav', '.mp3', '.ogg'))]
                    if all_audios:
                        st.audio(os.path.join(CURRENT_MEDIA_DIR, random.choice(all_audios)))

                    # 顯示啟示
                    st.divider()
                    st.markdown(f"### 🔮 啟示內容")
                    st.info(f"『 {response.text} 』")
                    st.caption(f"📍 碎片來源：{fragment[:60]}...")

                    # --- ✨ 核心修正：PDF 生成與物理存檔 ---
                    from weasyprint import HTML
                    import html
                    
                    pdf_filename = f"Oracle_{datetime.datetime.now().strftime('%m%d_%H%M')}.pdf"
                    pdf_path = os.path.join(ARCHIVE_DIR, pdf_filename)
                    
                    # 使用 html.escape 防止文本中的特殊字符破壞 HTML 結構
                    safe_text = html.escape(response.text).replace('\n', '<br>')
                    safe_fragment = html.escape(fragment)
                    
                    html_template = f"""
                    <div style="border: 10px double #D4AF37; padding: 40px; background: #2C2C2C; color: #E0E0E0; font-family: serif;">
                        <h1 style="color: #D4AF37; text-align: center;">《航道啟示錄》</h1>
                        <p style="font-size: 18px; line-height: 1.6; text-align: center; font-style: italic;">{safe_text}</p>
                        <hr style="border: 1px solid #D4AF37; margin: 30px 0;">
                        <p style="font-size: 10px; color: #888; text-align: right;">碎片殘響：{safe_fragment}</p>
                        <p style="font-size: 9px; color: #555; text-align: center; margin-top: 20px;">—— 錄於 總部核心 (acer) ——</p>
                    </div>
                    """
                    
                    # 物理寫入硬碟
                    HTML(string=html_template).write_pdf(pdf_path)
                    st.success(f"✅ 啟示已永恆封存至圖書館")
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button("💾 下載 PDF 啟示箋備份", f, file_name=pdf_filename)

                except Exception as e:
                    st.error(f"❌ 虛空連結中斷：{str(e)}")

elif channel == "📚 封存圖書館 (Library)":
    st.title("📚 舊日知識封存圖書館")
    st.caption("🔒 模式：物理歸檔 — 存放 PDF 報告、技術手冊與世界觀設定")
    st.markdown("---")

    # 1. 定位實體路徑 (ARCHIVE_DIR 應在核心配置中已定義)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    # =========================================================
    # 📥 知識物資歸檔區 (路徑核定模式)
    # =========================================================
    with st.expander("📥 知識物資快速歸檔 (核定後存入本地)", expanded=True):
        uploaded_lib_files = st.file_uploader(
            "拖入要封存的 PDF、文檔或圖片", 
            type=['pdf', 'txt', 'md', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="lib_uploader"
        )
        
        if uploaded_lib_files:
            for lib_file in uploaded_lib_files:
                st.markdown(f"**📄 偵測到物資：{lib_file.name}**")
                
                # 自動計算預設目標路徑
                target_full_path = os.path.join(ARCHIVE_DIR, lib_file.name)
                
                # 讓架構師核定路徑 (比照齒輪重組模式)
                col_path, col_btn = st.columns([3, 1])
                with col_path:
                    final_path = st.text_input(
                        "核定物理封存路徑：", 
                        value=target_full_path, 
                        key=f"path_in_{lib_file.name}"
                    )
                with col_btn:
                    st.write(" ") # 對齊調整
                    if st.button("🚩 執行物理封存", key=f"btn_save_{lib_file.name}"):
                        try:
                            with open(final_path, "wb") as f:
                                f.write(lib_file.getbuffer())
                            st.success(f"已歸檔至：{lib_file.name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"物理寫入失敗：{e}")
                st.markdown("---")

    # =========================================================
    # 🏛️ 封存閱覽室介面 (展示區)
    # =========================================================
    st.subheader("🏛️ 封存閱覽室 (The Archives)")
    
    if os.path.exists(ARCHIVE_DIR):
        # 抓取所有檔案並按時間排序
        archived_files = sorted(
            os.listdir(ARCHIVE_DIR), 
            key=lambda x: os.path.getmtime(os.path.join(ARCHIVE_DIR, x)), 
            reverse=True
        )
        
        if archived_files:
            for arch in archived_files:
                file_full_path = os.path.join(ARCHIVE_DIR, arch)
                if os.path.exists(file_full_path):
                    f_size = round(os.path.getsize(file_full_path)/1024, 1)
                    col_name, col_info, col_read = st.columns([3, 1, 1])
                    
                    col_name.write(f"📜 **{arch}**")
                    col_info.caption(f"💾 {f_size} KB")
                    
                    with open(file_full_path, "rb") as f:
                        col_read.download_button("📖 讀取", f, file_name=arch, key=f"read_{arch}")
        else:
            st.info("⚓ 目前圖書館尚無封存紀錄。")
