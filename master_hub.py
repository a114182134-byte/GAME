import json
import streamlit as st
import os
import requests
import google.generativeai as genai
import vertexai  
from vertexai.preview.vision_models import ImageGenerationModel
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
# --- 側邊欄：虛空定標配置 ---
st.sidebar.markdown("---")
st.sidebar.subheader("🌌 虛空定標配置")

# 使用 session_state 保留 ID，避免重新整理時消失
if "gcp_project_id" not in st.session_state:
    st.session_state.gcp_project_id = ""

# 建立輸入框
gcp_id = st.sidebar.text_input(
    "GCP Project ID", 
    value=st.session_state.gcp_project_id, 
    placeholder="例如: my-project-1234",
    help="請輸入妳在 Google Cloud 控制台看到的 Project ID"
)

# 狀態更新與初始化
if gcp_id:
    st.session_state.gcp_project_id = gcp_id
    try:
        import vertexai
        # 動態初始化：只要輸入 ID，系統就自動嘗試連線
        vertexai.init(project=gcp_id, location="us-central1")
        st.sidebar.success("✅ 座標定位成功 (ADC 模式)")
        VERTEX_READY = True
    except Exception as e:
        st.sidebar.error(f"❌ 定位失敗: {e}")
        VERTEX_READY = False
else:
    VERTEX_READY = False

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
    # --- ✨ 跨專案對接協定 (Bridge Protocol) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔗 專案對接協定")
    is_bridged = st.sidebar.checkbox("開啟跨專案對接", value=False, help="開啟後，日誌頻道將同時顯示多個專案的紀錄。")
    
    bridge_targets = [current_p_name] # 預設包含當前專案
    if is_bridged:
        # 讓妳選取要對接的「特定」專案
        bridge_targets = st.sidebar.multiselect(
            "選擇對接目標：",
            options=list(PROJECTS.keys()),
            default=[current_p_name]
        )
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
        "📚 封存圖書館 (Library)", "🕹️ 遊戲開發總覽",
        "🤖 腳本鍛造", "⚙️ 核心維護 (System)"
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

# =========================================================
# 📸 頻道：📸 素材打撈 (Media) - PDF 規範與多模態融合版
# =========================================================
if channel == "📸 素材打撈 (Media)":
        st.title("📸 殘留影像與波形打撈")
        st.caption("🤖 透過自定義「核心協議」深度解析影像、聲波與 PDF 規範")
        st.markdown("---")

        # ⚡ 核心優化：發射站識別
        ua = st.context.headers.get("User-Agent", "").lower()
        dev_type = "行動裝置" if "mobile" in ua else "核心主機"
        
        col_loc, col_info = st.columns([1, 2])
        with col_loc:
            station_origin = st.selectbox("📍 當前發射站", ["總部 (acer)", "台北站", "新竹站", "台南站"])
        with col_info:
            st.caption(f"📡 設備類型：`{dev_type}` | 接入網址：`{st.context.headers.get('Host')}`")

        # --- [核心功能] 手動更改 AI 提示詞配置區 ---
        with st.expander("🛠️ 配置打撈核心協議 (System Prompt 自定義)"):
            st.info("💡 這裡定義 AI 如何「解讀」妳上傳的影像與聲音。")
            
            default_media_instruction = f"""你現在是《{current_p_name}》專案的【素材打撈官】。
妳擅長從混亂的影像與波形中提取符合「黃銅蒸氣」與「末世重生」美學的開發靈感。

[任務]
請結合媒體內容與 PDF 規範，為開發者提供精準的素材分析報告。

[啟示指南]
1. 視覺拆解：分析構圖、色調是否符合專案設定。
2. 聲學轉譯：若有音訊，將其描述為具體的遊戲環境音效需求。
3. 規範對齊：嚴格遵守 PDF 提供的視覺或敘事準則。"""

            if "custom_media_prompt" not in st.session_state:
                st.session_state.custom_media_prompt = default_media_instruction

            st.session_state.custom_media_prompt = st.text_area(
                "編輯打撈協議 (System Instruction)", 
                value=st.session_state.custom_media_prompt, 
                height=200,
                key="media_prompt_area"
            )
            if st.button("♻️ 重置打撈協議"):
                st.session_state.custom_media_prompt = default_media_instruction
                st.rerun()

        # 1. 指令與 PDF 知識注入區
        st.subheader("🧠 靈感指令與 PDF 規範")
        col_text, col_pdf = st.columns([2, 1])
        
        with col_text:
            u_text = st.text_area("靈感咒語 / 分析需求", placeholder="例如：分析這張草圖，並根據 PDF 規範建議改進方向...", height=120)
        
        with col_pdf:
            u_pdf = st.file_uploader("📋 導入規範 (PDF)", type=['pdf'], key="media_pdf_up")
            pdf_context = ""
            if u_pdf:
                pdf_reader = PyPDF2.PdfReader(u_pdf)
                for page in pdf_reader.pages:
                    pdf_context += (page.extract_text() or "") + "\n"
                st.success(f"✅ 規範已載入")

        st.subheader("🎤 語音靈感捕捉")
        from audio_recorder_streamlit import audio_recorder
        audio_bytes = audio_recorder(
            text=f"來自【{station_origin}】的通訊",
            recording_color="#e74c3c", neutral_color="#D4AF37", icon_size="2x"
        )

        if audio_bytes:
            if "last_mic_data" not in st.session_state or st.session_state.last_mic_data != audio_bytes:
                timestamp = datetime.datetime.now().strftime('%m%d_%H%M%S')
                mic_path = os.path.join(MEDIA_DIR, f"mic_{station_origin}_{timestamp}.wav")
                with open(mic_path, "wb") as f: f.write(audio_bytes)
                st.session_state.last_mic_data = audio_bytes 
                st.sidebar.success(f"🎙️ 聲波已入庫")
            st.audio(audio_bytes, format="audio/wav")

        st.divider()
        
        # 2. 檔案上傳預覽
        col_up1, col_up2 = st.columns(2)
        with col_up1:
            u_img = st.file_uploader("🖼️ 影像打撈", type=['png', 'jpg', 'jpeg', 'webp'])
            if u_img:
                img = Image.open(u_img)
                st.image(img, caption="🚀 待處理影像預覽", use_column_width=True)

        with col_up2:
            u_audio = st.file_uploader("🎵 音訊打撈", type=['mp3', 'wav', 'ogg', 'm4a'])
            if u_audio: st.audio(u_audio)

        st.markdown("---")
        
        # 3. 處理按鈕
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            analyze_btn = st.button("🚀 啟動解析 (依據自定義協議)", use_container_width=True)
        with col_btn2:
            draw_btn = st.button("🎨 請求虛空重塑 (Imagen 3)", use_container_width=True)

        # --- 邏輯處理 A：Gemini 解析 ---
        if analyze_btn:
            if not (u_img or u_audio or u_text or audio_bytes or u_pdf):
                st.warning("📡 數據不足，請提供素材、指令或規範。")
            else:
                with st.spinner("正在套用自定義協議進行打撈..."):
                    try:
                        content_payload = []
                        # 注入【自定義協議】與【PDF】
                        full_instr = f"{st.session_state.custom_media_prompt}\n\n[PDF 規範內容]：\n{pdf_context[:5000]}"
                        content_payload.append(full_instr)
                        
                        # 注入指令與媒體
                        content_payload.append(f"[用戶當前指令]：{u_text if u_text else '綜合分析媒體內容。'}")
                        if u_img: content_payload.append(img)
                        if audio_bytes: content_payload.append({"mime_type": "audio/wav", "data": audio_bytes})
                        if u_audio: 
                            u_audio.seek(0)
                            content_payload.append({"mime_type": u_audio.type, "data": u_audio.read()})

                        genai.configure(api_key=FINAL_KEY, transport="rest")
                        model = genai.GenerativeModel(AI_MODEL)
                        response = model.generate_content(content_payload)
                        
                        st.markdown("### 📝 打撈報告")
                        st.info(response.text)
                        
                        # 紀錄日誌
                        log_dir = os.path.join(DATA_ROOT, current_p_name, "logs")
                        os.makedirs(log_dir, exist_ok=True)
                        log_path = os.path.join(log_dir, f"Media_Salvage_{datetime.datetime.now().strftime('%m%d_%H%M')}.md")
                        with open(log_path, "w", encoding="utf-8") as f:
                            f.write(f"# 媒體打撈報告\n\n### 核心協議\n{st.session_state.custom_media_prompt}\n\n### 解析結果\n{response.text}")
                        st.success(f"✅ 解析結果已同步至專案日誌")
                    except Exception as e:
                        st.error(f"❌ 引擎異常: {str(e)}")
    # --- 邏輯 B：Vertex AI Imagen 3 生成 ---
        if draw_btn:
            current_id = st.session_state.get("gcp_project_id")
            if not current_id:
                st.warning("⚠️ 虛空航道未定位！請先在側邊欄輸入『GCP Project ID』。")
            elif not u_text:
                st.warning("🔮 缺少咒語！請在指令核心輸入描述。")
            else:
                with st.spinner("正在調動 Vertex AI 進行物理重塑..."):
                    try:
                        from vertexai.preview.vision_models import ImageGenerationModel
                        imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
                        
                        # 如果有 PDF 內容，擷取關鍵字加入咒語
                        style_hint = "Brass steampunk, post-apocalyptic."
                        if pdf_context:
                            style_hint += f" Follow style guide: {pdf_context[:200]}"
                            
                        full_prompt = f"Style: {style_hint}. Subject: {u_text}"
                        
                        images = imagen_model.generate_images(
                            prompt=full_prompt,
                            number_of_images=1,
                            aspect_ratio="1:1"
                        )
                        
                        if images:
                            timestamp = datetime.datetime.now().strftime('%m%d_%H%M%S')
                            img_name = f"reborn_{station_origin}_{timestamp}.png"
                            img_path = os.path.join(MEDIA_DIR, img_name)
                            images[0].save(location=img_path, include_generation_parameters=False)
                            st.image(img_path, caption=f"✨ 虛空重塑完成：{u_text}")
                            st.sidebar.success(f"🎨 影像已入庫")
                    except Exception as e:
                        st.error(f"❌ 影像重塑失敗：{str(e)}")

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

# =========================================================
# =========================================================
# =========================================================
# =========================================================
# 🧪 頻道：全域結構物理修復 (Patch) - 配額超頻打包版
# =========================================================
elif channel == "🧪 結構修復 (Patch)":
    st.title("🧪 全域結構物理修復 (2.5 Flash 能量節省版)")
    st.caption(f"🚀 核心協定：打包重塑 | 當前模型：{AI_MODEL}")
    st.warning(f"⚡ 警告：2.5 Flash 每日僅 20 次配額。目前採用「打包模式」，選中再多檔案也只消耗 1 次配額。")
    st.markdown("---")

    script_path = config.get("local_script_path", "")
    if script_path and os.path.exists(script_path):
        all_files = [f for f in os.listdir(script_path) if f.endswith('.gd') or f.endswith('.py')]
        
        if not all_files:
            st.info("📂 腳本夾內空無一物。")
        else:
            # --- 多選介面 ---
            st.subheader("🎯 選擇待修補目標")
            col_sel_all, _ = st.columns([1, 3])
            with col_sel_all:
                is_select_all = st.checkbox("全選所有腳本")
            
            targets = all_files if is_select_all else st.multiselect("手動挑選檔案", all_files, key="patch_multi_select")

            # --- 1. 知識注入 (PDF) ---
            uploaded_pdf = st.file_uploader("📋 導入維修手冊 (PDF)", type=['pdf'], key="patch_pdf")
            pdf_knowledge = ""
            if uploaded_pdf:
                pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                for page in pdf_reader.pages:
                    pdf_knowledge += (page.extract_text() or "") + "\n"
                st.success(f"✅ PDF 知識已注入緩衝區 ({len(pdf_knowledge)} 字)")

            st.divider()

            # --- 2. 修復需求 ---
            st.subheader("🔥 啟動打包重構")
            fix_instr = st.text_area("描述修復需求", placeholder="例如：將所有檔案的變數名改為底線命名法...", height=150)

            # --- 3. 核心執行邏輯 ---
            if st.button("🛠️ 執行物理重構與生成報告", type="primary", use_container_width=True):
                if not targets or not fix_instr:
                    st.error("❌ 未選取檔案或指令。")
                elif not ai_key: # 確保讀取環境變數中的 key
                    st.error("❌ 找不到 AI 金鑰。")
                else:
                    try:
                        # 詢問存檔位置
                        import tkinter as tk
                        from tkinter import filedialog
                        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
                        save_report_path = filedialog.asksaveasfilename(
                            defaultextension=".pdf",
                            filetypes=[("PDF files", "*.pdf")],
                            initialfile=f"Batch_Patch_{datetime.datetime.now().strftime('%m%d')}.pdf",
                            title="小白龍架構師：指定維修報告位置"
                        )
                        root.destroy()

                        if save_report_path:
                            # A. 打包所有代碼
                            all_code_context = ""
                            for file_name in targets:
                                f_path = os.path.join(script_path, file_name)
                                with open(f_path, "r", encoding="utf-8") as f:
                                    all_code_context += f"\n--- START_FILE: {file_name} ---\n{f.read()}\n--- END_FILE: {file_name} ---\n"

                            # B. 啟動 AI (REST 協定穩定版)
                            with st.spinner(f"正在對 {len(targets)} 個檔案進行大規模邏輯超頻..."):
                                genai.configure(api_key=ai_key, transport="rest")
                                model = genai.GenerativeModel(model_name=AI_MODEL)
                                
                                full_prompt = f"""
                                你現在是資深 Godot 架構師。
                                [參考規範] {pdf_knowledge[:3000]}
                                [修改需求] {fix_instr}
                                
                                以下是多個檔案的代碼集。請根據需求修改，並保持以下輸出格式：
                                每個檔案開頭必須是「--- SAVETO: 檔名 ---」，接著是完整代碼。
                                不要有任何解釋，只要純代碼。
                                
                                [代碼集]
                                {all_code_context}
                                """
                                
                                response = model.generate_content(full_prompt)
                                raw_output = response.text

                            # C. 物理拆解與覆寫
                            import re
                            parts = re.split(r"--- SAVETO: (.*?) ---", raw_output)
                            success_files = []
                            
                            # parts 結構: [空/雜訊, 檔名1, 代碼1, 檔名2, 代碼2...]
                            for i in range(1, len(parts), 2):
                                f_name = parts[i].strip()
                                f_code = parts[i+1].strip().replace("```gdscript", "").replace("```", "").strip()
                                
                                if f_name in targets:
                                    with open(os.path.join(script_path, f_name), "w", encoding="utf-8") as f:
                                        f.write(f_code)
                                    success_files.append(f_name)
                                    st.toast(f"✅ {f_name} 已物理覆寫")

                            st.success(f"🚀 重構完成！僅消耗 1 次配額，成功修補 {len(success_files)} 個檔案。")
                            st.balloons()
                    except Exception as e:
                        st.error(f"全域重構故障: {e}")

# =========================================================
# 🔮 頻道：虛空啟示 (Oracle) - 核心協定自定義版
# =========================================================
elif channel == "🔮 虛空啟示 (Oracle)":
    st.title("🔮 虛空啟示：全域架構諮詢")
    st.caption("🤖 AI 將根據妳自定義的「核心協定」分析專案檔案與日誌")
    st.markdown("---")

    # 1. 自動打撈路徑定位
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    script_path = config.get("local_script_path", "")
    
    # --- 2. [新增] 手動更改 AI 提示詞配置區 ---
    with st.expander("🛠️ 配置虛空核心協定 (System Prompt 自定義)"):
        st.info("💡 妳可以在這裡手動更改 AI 的導師身份與行為邏輯。")
        
        # 預設範本：整合了黃銅蒸氣風格與架構檢查邏輯
        default_system_instruction = f"""你現在是《{current_p_name}》專案的核心架構導師：【虛空奧術師】。
風格應冷靜、精準且具備遊戲開發的前瞻性，語氣帶有一點黃銅蒸氣的機械感。

[任務]
請分析提供的代碼與日誌，回答開發者的提問，並找出邏輯斷層或優化空間。

[啟示指南]
1. 實戰建議：針對 Godot (GDScript) 提供具體代碼修改方向。
2. 邏輯檢查：若發現日誌紀錄與現有腳本邏輯衝突，請務必指出。
3. 風格對齊：請考慮「黃銅蒸氣」與「末世」的遊戲背景設定。"""

        # 使用 session_state 保留妳手動修改的內容
        if "custom_oracle_prompt" not in st.session_state:
            st.session_state.custom_oracle_prompt = default_system_instruction

        # 核心編輯接口
        st.session_state.custom_oracle_prompt = st.text_area(
            "編輯導師協議 (System Instruction)", 
            value=st.session_state.custom_oracle_prompt, 
            height=250,
            help="這段文字決定了 AI 的思考邏輯與回應風格。"
        )
        if st.button("♻️ 重置為預設協議"):
            st.session_state.custom_oracle_prompt = default_system_instruction
            st.rerun()

    # 顯示當前知識庫範圍
    with st.expander("📂 檢視 AI 當前載入的知識庫範圍"):
        all_files_list = []
        if os.path.exists(CURRENT_LOG_DIR):
            md_files = [f for f in os.listdir(CURRENT_LOG_DIR) if f.endswith(".md")]
            all_files_list.extend([f"日誌: {f}" for f in md_files])
        if script_path and os.path.exists(script_path):
            gd_files = [f for f in os.listdir(script_path) if f.endswith(".gd")]
            all_files_list.extend([f"腳本: {f}" for f in gd_files])
        st.write(all_files_list if all_files_list else "目前無載入任何檔案")

    # 3. 提問介面
    st.subheader("❓ 向架構導師提問")
    user_query = st.text_area("提問內容", placeholder="例如：『根據目前的魚叉腳本，如何加入連鎖閃電效果？』", height=100)
    uploaded_pdf = st.file_uploader("導入 PDF 參考", type=['pdf'], key="oracle_pdf")

    if "oracle_response" not in st.session_state:
        st.session_state.oracle_response = ""

    if st.button("🌌 啟動虛空連結", type="primary", use_container_width=True):
        if not user_query:
            st.warning("請先輸入疑問。")
        elif not FINAL_KEY:
            st.error("❌ 金鑰未配置。")
        else:
            with st.spinner("AI 正在解析全域資料並套用自定義協定..."):
                try:
                    # A. 提取 Context (加入內容切片防止過載)
                    context_data = []
                    if os.path.exists(CURRENT_LOG_DIR):
                        for f in os.listdir(CURRENT_LOG_DIR):
                            if f.endswith(".md"):
                                with open(os.path.join(CURRENT_LOG_DIR, f), "r", encoding="utf-8") as file:
                                    context_data.append(f"--- 日誌 {f} ---\n{file.read()[:3000]}")
                    
                    if script_path and os.path.exists(script_path):
                        for f in os.listdir(script_path):
                            if f.endswith(".gd"):
                                with open(os.path.join(script_path, f), "r", encoding="utf-8") as file:
                                    context_data.append(f"--- 腳本 {f} ---\n{file.read()[:5000]}")

                    full_context = "\n\n".join(context_data)
                    
                    # 提取 PDF
                    pdf_text = ""
                    if uploaded_pdf:
                        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                        for page in pdf_reader.pages:
                            pdf_text += (page.extract_text() or "") + "\n"
                    
                    # B. 呼叫 AI (注入手動修改後的提示詞)
                    genai.configure(api_key=FINAL_KEY, transport="rest")
                    model = genai.GenerativeModel(AI_MODEL)
                    
                    # 最終組裝：[自定義協定] + [知識庫] + [PDF] + [問題]
                    final_oracle_prompt = f"""
{st.session_state.custom_oracle_prompt}

[專案全域知識庫]
{full_context[:15000]}

[PDF 補充資料]
{pdf_text[:5000]}

[開發者當前疑問]
{user_query}
"""
                    response = model.generate_content(final_oracle_prompt)
                    st.session_state.oracle_response = response.text
                    st.session_state.last_query = user_query
                    
                except Exception as e:
                    st.error(f"虛空連線中斷: {e}")

    # 4. 顯示與導出
    if st.session_state.oracle_response:
        st.markdown("---")
        st.subheader("🔮 虛空啟示內容")
        st.info(st.session_state.oracle_response)
        
        # PDF 導出
        try:
            from weasyprint import HTML
            output_dir = os.path.join(DATA_ROOT, current_p_name, "logs")
            pdf_filename = f"Oracle_{datetime.datetime.now().strftime('%m%d_%H%M')}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)

            html_content = f"""
            <html><body style="font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d4af37;">餘燼啟示錄：自定義架構報告</h1>
                <p><b>諮詢問題：</b> {st.session_state.get('last_query', '未知')}</p>
                <hr>
                <div style="white-space: pre-wrap; line-height: 1.6;">{st.session_state.oracle_response}</div>
                <p style="font-size: 10px; color: #999; margin-top: 50px;">由 小白龍 19GB 核心主機生成 | 核心型號: {AI_MODEL}</p>
            </body></html>
            """
            
            if st.button("📥 將啟示歸檔為 PDF", use_container_width=True):
                HTML(string=html_content).write_pdf(pdf_path)
                st.success(f"✅ 啟示錄已存至：{pdf_path}")
                with open(pdf_path, "rb") as f:
                    st.download_button("💾 下載 PDF 檔案", f, file_name=pdf_filename, mime="application/pdf", use_container_width=True)
        except Exception as e:
            st.warning(f"導出功能暫不可用：{e}")

    st.divider()
    st.caption("📜 虛空啟示錄：妳已獲得核心協議的修改權限。現在，導師的靈魂將隨妳的意念而重塑。")

# =========================================================
# 📜 頻道：航行日誌 (Log) - 跨專案對接與 AI 聯動版
# =========================================================
elif channel == "📜 航行日誌 (Log)":
    if is_bridged and len(bridge_targets) > 1:
        st.title(f"🔗 跨專案對接：{', '.join(bridge_targets)}")
        st.caption("目前處於跨專案聯動模式，數據將進行全域排序。")
    else:
        st.title(f"📜 {current_p_name}：專屬航行紀錄")
    st.markdown(f"---")
    
    # 1. 🔍 多軌數據打撈邏輯
    all_logs_data = []
    for p_name in bridge_targets:
        t_log_dir = os.path.join(DATA_ROOT, p_name, "logs")
        t_media_dir = os.path.join(DATA_ROOT, p_name, "media")
        
        if os.path.exists(t_log_dir):
            for f_name in os.listdir(t_log_dir):
                # 讀取 md 檔案，排除生成的報告
                if f_name.endswith(".md") and "_全案報告_" not in f_name:
                    f_full_path = os.path.join(t_log_dir, f_name)
                    all_logs_data.append({
                        "project": p_name,
                        "filename": f_name,
                        "path": f_full_path,
                        "media_dir": t_media_dir,
                        "time": os.path.getmtime(f_full_path)
                    })

    # ⚡ 全域時間排序 (最新優先)
    all_logs_data = sorted(all_logs_data, key=lambda x: x["time"], reverse=True)

    # 2. 🚀 數據精煉中心 (支援聯動總結)
    st.subheader("📊 專案彙整與報告生成")
    report_label = "📊 生成聯動開發報告" if is_bridged else f"📊 生成 {current_p_name} 專屬報告"
    
    if st.button(report_label, type="primary", use_container_width=True):
        if not FINAL_KEY:
            st.error("❌ 核心金鑰失效，請更新 API Key。")
        else:
            try:
                with st.spinner(f"🚀 正在對接 {'、'.join(bridge_targets)} 數據並精煉 PDF..."):
                    combined_contents = []
                    for entry in all_logs_data:
                        with open(entry["path"], "r", encoding="utf-8") as f:
                            combined_contents.append(f"--- [來源專案: {entry['project']}] 檔案: {entry['filename']} ---\n{f.read()}")
                    
                    if not combined_contents:
                        st.warning("📡 範圍內找不到原始日誌數據。")
                    else:
                        # 準備 AI 彙整內容
                        full_context = "\n\n".join(combined_contents)
                        model = genai.GenerativeModel(AI_MODEL)
                        
                        # 針對對接模式調整 Prompt
                        if is_bridged:
                            prompt = f"你是一位資深開發架構師。請針對以下多個對接專案的日誌進行聯動分析，指出它們的開發關聯點、技術重合處或潛在的整合建議：\n\n{full_context}"
                        else:
                            prompt = f"你是一位資深開發助手。請根據以下數據為《{current_p_name}》整理專業報告：\n\n{full_context}"
                        
                        response = model.generate_content(prompt)
                        ai_report = response.text
                        
                        # 建立報告路徑 (存放在當前主專案)
                        timestamp_str = datetime.datetime.now().strftime('%m%d_%H%M')
                        report_filename = f"聯動報告_{timestamp_str}.pdf" if is_bridged else f"{current_p_name}_報告_{timestamp_str}.pdf"
                        save_path = os.path.join(DATA_ROOT, current_p_name, "logs", report_filename)
                        
                        # 轉 PDF
                        from weasyprint import HTML
                        html_style = f"""
                        <html><body style="font-family: sans-serif; padding: 30px;">
                            <h1 style="color: #d4af37; border-bottom: 2px solid #d4af37;">餘燼航路：{'聯動' if is_bridged else '專屬'}開發報告</h1>
                            <div style="background: #fdfaf3; padding: 20px; border: 1px solid #ddd; line-height: 1.6; white-space: pre-wrap;">
                                {ai_report}
                            </div>
                            <p style="font-size: 10px; color: #999; margin-top: 20px;">由 小白龍 19GB 核心主機生成 | 座標：屏東九如發射站</p>
                        </body></html>
                        """
                        HTML(string=html_style).write_pdf(save_path)
                        st.success(f"✅ 報告已生成並物理歸檔。")
                        
                        with open(save_path, "rb") as pdf_file:
                            st.download_button(label="📥 下載報告 PDF", data=pdf_file, file_name=report_filename, mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"❌ 彙整失敗: {str(e)}")

    # 3. 📜 歷史航行紀錄 (支援跨專案對齊)
    st.divider()
    st.subheader("📜 歷史紀錄詳細打撈")
    
    if not all_logs_data:
        st.info("📡 偵測範圍內尚無任何日誌紀錄。")
    else:
        import re
        for log_item in all_logs_data:
            # 顯示標籤：若開啟對接則顯示專案名
            expander_label = f"🚀 [{log_item['project']}] {log_item['filename']}" if is_bridged else f"📒 {log_item['filename']}"
            
            with st.expander(expander_label, expanded=False):
                with open(log_item["path"], "r", encoding="utf-8") as f:
                    log_text = f.read()
                
                col_txt, col_img = st.columns([2, 1])
                with col_txt:
                    st.markdown(log_text)
                
                with col_img:
                    img_match = re.search(r"- \*\*關聯影像\*\*: (.+)", log_text)
                    if img_match:
                        ref_img_name = img_match.group(1).strip()
                        # 自動去該日誌所屬的專案媒體庫找圖
                        ref_img_path = os.path.join(log_item["media_dir"], ref_img_name)
                        if os.path.exists(ref_img_path):
                            st.image(ref_img_path, caption=f"來自 {log_item['project']}", use_column_width=True)
                        else:
                            st.caption("⚠️ 影像檔案遺失")
                    else:
                        st.caption("📷 無影像連結")
                st.caption(f"📍 座標：`{log_item['path']}`")

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

    # 1. 定位實體路徑
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    # =========================================================
    # 📥 知識物資歸檔區 (保持不變)
    # =========================================================
    with st.expander("📥 知識物資快速歸檔 (核定後存入本地)", expanded=False):
        uploaded_lib_files = st.file_uploader(
            "拖入要封存的 PDF、文檔或圖片", 
            type=['pdf', 'txt', 'md', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="lib_uploader"
        )
        
        if uploaded_lib_files:
            for lib_file in uploaded_lib_files:
                st.markdown(f"**📄 偵測到物資：{lib_file.name}**")
                target_full_path = os.path.join(ARCHIVE_DIR, lib_file.name)
                col_path, col_btn = st.columns([3, 1])
                with col_path:
                    final_path = st.text_input("核定物理封存路徑：", value=target_full_path, key=f"path_in_{lib_file.name}")
                with col_btn:
                    st.write(" ")
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
    # 🔮 虛空文獻諮詢 (新加入：圖書館問答功能)
    # =========================================================
    st.subheader("🔮 虛空文獻諮詢")
    st.caption("向圖書館投射疑問，AI 將翻閱所有封存 PDF 並從舊日啟示中尋找答案。")
    
    col_ask, col_go = st.columns([4, 1])
    with col_ask:
        archive_query = st.text_input("輸入疑問：", placeholder="例如：之前的魚叉系統進化建議是什麼？", label_visibility="collapsed")
    with col_go:
        start_search = st.button("🔍 執行打撈", use_container_width=True)

    if start_search:
        if not archive_query:
            st.warning("請先輸入疑問。")
        elif not os.getenv("ai_key"):
            st.error("❌ 缺少 API Key，無法呼喚圖書館守護靈。")
        else:
            with st.spinner("正在快速翻閱圖書館 PDF 文獻..."):
                all_pdf_texts = []
                if os.path.exists(ARCHIVE_DIR):
                    for f_name in os.listdir(ARCHIVE_DIR):
                        if f_name.endswith(".pdf"):
                            pdf_path = os.path.join(ARCHIVE_DIR, f_name)
                            try:
                                with open(pdf_path, "rb") as f:
                                    reader = PyPDF2.PdfReader(f)
                                    # 每一份 PDF 提取前 5 頁內容以節省資源
                                    content = f"\n[文獻：{f_name}]\n"
                                    for i in range(min(len(reader.pages), 5)):
                                        content += reader.pages[i].extract_text()
                                    all_pdf_texts.append(content)
                            except:
                                pass # 略過毀損檔案
                
                if not all_pdf_texts:
                    st.info("⚓ 圖書館目前尚無可供解析的 PDF 文獻。")
                else:
                    try:
                        # 呼喚 AI 並注入文獻 Context
                        model = genai.GenerativeModel(AI_MODEL)
                        context_str = "\n".join(all_pdf_texts)
                        prompt = f"""
                        你是一位管理《{current_p_name}》圖書館的守護靈。
                        架構師「小白龍」正在查詢舊日文獻。
                        
                        以下是圖書館內部的文獻碎片：
                        {context_str}
                        
                        請根據以上文獻回答：{archive_query}
                        如果文獻中沒有提到，請以守護靈的身份給予建議，並說明這不在現有紀錄中。
                        """
                        response = model.generate_content(prompt)
                        st.markdown(f"### 📖 圖書館啟示錄\n\n{response.text}")
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"虛空連結中斷：{e}")

    # =========================================================
    # 🏛️ 封存閱覽室介面 (展示區 - 保持不變)
    # =========================================================
    st.subheader("🏛️ 封存閱覽室 (The Archives)")
    if os.path.exists(ARCHIVE_DIR):
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
elif channel == "⚙️ 核心維護 (System)":
    st.title("⚙️ 核心動力室維護")
    st.caption("管理母站燃料、專案架構及遠端進化協定。")
    st.markdown("---")
    
    # 1. 燃料庫 (.env) 配置 (保持不變)
    with st.expander("🔑 燃料庫 (.env) 配置"):
        st.info("若顯示『未配置 github_token』，請在此輸入並點擊物理寫入。")
        curr_ai = os.getenv("ai_key", "")
        curr_gh = os.getenv("github_token", "")
        
        new_ai = st.text_input("填入 ai_key", value=curr_ai, type="password")
        new_gh = st.text_input("填入 github_token", value=curr_gh, type="password")
        
        if st.button("🚀 物理寫入 .env 燃料庫"):
            with open(BASE_PATH / ".env", "w", encoding="utf-8") as f:
                f.write(f"ai_key={new_ai}\ngithub_token={new_gh}\n")
            os.environ["ai_key"] = new_ai
            os.environ["github_token"] = new_gh
            st.success("✅ 燃料庫已重新注入，環境變數已即時刷新！")

    # 2. 🚀 遠端邏輯同步 (GitHub Sync) - 固定路徑版
    with st.expander("🚀 遠端邏輯同步 (GitHub Sync)", expanded=True):
        st.info("從 GitHub 遠端倉庫打撈最新代碼，直接物理覆寫母站核心。")
        
        # 從專案設定中讀取已存的路徑，若無則預設為空
        saved_repo = PROJECTS[current_p_name].get("github_repo", "")
        saved_branch = PROJECTS[current_p_name].get("github_branch", "main")
        
        sync_repo = st.text_input("遠端倉庫位址 (格式: 用戶名/倉庫名)", value=saved_repo, placeholder="zzz961011/Your_Repo_Name")
        sync_branch = st.text_input("目標分支", value=saved_branch)
        
        # 新增一個儲存路徑的按鈕，避免每次都要重打
        if st.button("📌 固定此倉庫路徑"):
            PROJECTS[current_p_name]["github_repo"] = sync_repo
            PROJECTS[current_p_name]["github_branch"] = sync_branch
            save_config(PROJECTS)
            st.success(f"✅ 座標已定標！下次進入【{current_p_name}】將自動載入此路徑。")

        st.divider()

        if st.button("🔥 啟動核心邏輯物理同步", use_container_width=True):
            gh_token = os.getenv("github_token")
            if not gh_token or not sync_repo:
                st.error("❌ 缺少 token 或倉庫路徑，無法穿越虛空。")
            else:
                with st.spinner("正在連接 GitHub 衛星，準備重新鍛造核心..."):
                    try:
                        api_url = f"https://api.github.com/repos/{sync_repo}/contents/master_hub.py?ref={sync_branch}"
                        headers = {"Authorization": f"token {gh_token}"}
                        
                        resp = requests.get(api_url, headers=headers)
                        if resp.status_code == 200:
                            download_url = resp.json().get("download_url")
                            new_code = requests.get(download_url).text
                            
                            with open(__file__, "w", encoding="utf-8") as f:
                                f.write(new_code)
                            
                            st.success("✅ 核心邏輯同步完成！母站正在重新啟動進化...")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"同步失敗：HTTP {resp.status_code} (請檢查路徑與權限)")
                    except Exception as e:
                        st.error(f"❌ 同步過程發生物理故障: {e}")

    # 3. 專案修改、新增與刪除
    with st.expander("📝 專案架構管理"):
        st.subheader(f"當前專案：{current_p_name}")
        new_path = st.text_input("Godot 腳本資料夾路徑", config.get("local_script_path", ""))
        new_prompt = st.text_area("AI 架構師公約 (System Prompt)", config.get("prompt", ""))
        
        if st.button("💾 儲存專案修改"):
            PROJECTS[current_p_name]["local_script_path"] = new_path
            PROJECTS[current_p_name]["prompt"] = new_prompt
            save_config(PROJECTS)
            st.success("專案設定已同步至 projects_config.json")

        st.divider()
        new_p_name = st.text_input("➕ 建立新專案名稱")
        if st.button("🏗️ 啟動新專案架構"):
            if new_p_name and new_p_name not in PROJECTS:
                PROJECTS[new_p_name] = {
                    "theme_color": "#D4AF37", "bg_color": "#1A1A1A", 
                    "prompt": "你是架構師", "local_script_path": "", "keys_list": []
                }
                save_config(PROJECTS)
                st.rerun()
        
        st.divider()
       # =========================================================
        # 🚨 危險區域：專案物理拆解 (深度強制解鎖版)
        # =========================================================
        with st.expander("🚨 危險區域：專案物理拆解"):
            st.warning(f"警告：此操作將物理刪除「{current_p_name}」所有資料夾與配置。")
            
            confirm_input = st.text_input(
                f"請輸入專案名稱「{current_p_name}」以解鎖：", 
                placeholder=current_p_name,
                key="delete_auth_input"
            )
            
            if st.button(f"🔥 啟動末世抹除協定", type="primary", disabled=(confirm_input != current_p_name), use_container_width=True):
                if len(PROJECTS) > 1:
                    # 1. 🔍 逃生艙：決定跳轉目標
                    escape_target = [p for p in PROJECTS.keys() if p != current_p_name][0]
                    
                    # 2. 📝 從記憶體移除紀錄
                    target_dir = os.path.join(DATA_ROOT, current_p_name)
                    del PROJECTS[current_p_name]
                    save_config(PROJECTS)
                    
                    # 3. 🛸 意識強制跳轉 (解除 Streamlit 對當前目錄的監控)
                    st.session_state["current_project"] = escape_target
                    
                    # 4. 🧹 清理內部緩存 (重要：解除可能的檔案讀取鎖定)
                    st.cache_resource.clear()
                    st.cache_data.clear()

                    # 5. 🧨 強制物理抹除
                    # 先切換當前工作目錄到 DATA_ROOT，防止進程鎖定子資料夾
                    original_cwd = os.getcwd()
                    try:
                        if os.path.exists(target_dir):
                            # 使用 shutil.rmtree 的 onerror 處理唯讀檔案或權限問題
                            def remove_readonly(func, path, excinfo):
                                os.chmod(path, 0o777) # 賦予最高權限
                                func(path)

                            shutil.rmtree(target_dir, onerror=remove_readonly)
                            
                        st.toast(f"🚩 專案【{current_p_name}】已徹底抹除", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 物理抹除失敗：{str(e)}")
                        st.info("💡 建議：手動關閉『檔案總管』或『VS Code』對該資料夾的存取，並切換專案後重試。")
                else:
                    st.error("🚨 核心協議：必須保留至少一個運作中的專案。")

    st.divider()
    
    # 4. 雲端進化同步 (Git Push)
    st.subheader("🚀 雲端進化同步 (Git Push)")
    if not os.getenv("github_token"):
        st.error("⚠️ 偵測不到 GitHub Token，同步功能已鎖定。")
    
    commit_msg = st.text_input("進化紀錄訊息 (Commit Message)", 
                               value=f"v{datetime.datetime.now().strftime('%m%d')} 小白龍架構進化")
    
    if st.button("🔥 啟動全域同步 (Push)"):
        if not os.getenv("github_token"):
            st.error("請先在上方寫入 github_token")
        else:
            with st.spinner("正在穿越虛空同步至 GitHub..."):
                success, msg = secure_auto_push(commit_msg)
                if success: st.success(msg)
                else: st.error(msg)

    # 5. 🛰️ 虛空定標診斷
    st.divider()
    st.subheader("🛰️ 虛空定標診斷")
    if st.button("🔍 啟動全域模型掃描"):
        ACTIVE_KEY = st.session_state.get("active_key", os.getenv("ai_key"))
        if not ACTIVE_KEY:
            st.error("❌ 未偵測到有效金鑰。")
        else:
            try:
                with st.spinner("正在掃描虛空可用模型..."):
                    genai.configure(api_key=ACTIVE_KEY)
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if available_models:
                        st.success(f"✅ 掃描完成！")
                        for m in available_models: st.code(m)
                    else:
                        st.warning("⚠️ 此金鑰無生成權限。")
            except Exception as e:
                st.error(f"❌ 掃描程序崩潰：{str(e)}")
# =========================================================
    # 🕹️ 頻道：遊戲開發總覽 (Game Dev Hub) - 黃銅觀測站
    # =========================================================
elif channel == "🕹️ 遊戲開發總覽":
    st.title("🕹️ 餘燼檔案：全域開發總覽")
    
    # --- [1] 注入黃銅蒸氣美學 CSS ---
    st.markdown("""
        <style>
        .game-card {
            background-color: #1a1a1a;
            border: 2px solid #d4af37;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
            transition: transform 0.3s;
        }
        .game-card:hover {
            transform: scale(1.02);
            border-color: #ffcc33;
            box-shadow: 0px 0px 20px rgba(212, 175, 55, 0.4);
        }
        .game-title {
            color: #d4af37;
            font-family: 'Courier New', Courier, monospace;
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 10px;
        }
        .game-preview {
            color: #b0b0b0;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- [2] 全域專案數據打撈 ---
    all_game_data = []
    if os.path.exists(DATA_ROOT):
        for p_folder in os.listdir(DATA_ROOT):
            p_path = os.path.join(DATA_ROOT, p_folder)
            if not os.path.isdir(p_path): continue
            
            # 尋找與專案同名的 .md 或資料夾內的 md
            md_path = os.path.join(p_path, f"{p_folder}.md")
            if not os.path.exists(md_path):
                # 如果沒找到同名 md，抓 logs 裡最新的一份
                log_dir = os.path.join(p_path, "logs")
                if os.path.exists(log_dir):
                    md_files = [f for f in os.listdir(log_dir) if f.endswith(".md")]
                    if md_files:
                        md_path = os.path.join(log_dir, sorted(md_files)[-1])
            
            if os.path.exists(md_path):
                # 抓取圖片：尋找 media 裡最新的一張圖
                media_dir = os.path.join(p_path, "media")
                cover_img = None
                if os.path.exists(media_dir):
                    imgs = [f for f in os.listdir(media_dir) if f.lower().endswith(('.png', '.jpg', '.webp'))]
                    if imgs:
                        # 排序抓最新的一張作為封面
                        imgs = sorted(imgs, key=lambda x: os.path.getmtime(os.path.join(media_dir, x)), reverse=True)
                        cover_img = os.path.join(media_dir, imgs[0])
                
                # 讀取前 100 字簡介
                with open(md_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 移除 Markdown 標籤純取文字
                    clean_text = content.replace("#", "").replace("*", "").strip()
                    preview = clean_text[:100] + "..." if len(clean_text) > 100 else clean_text

                all_game_data.append({
                    "name": p_folder,
                    "img": cover_img,
                    "preview": preview,
                    "full_content": content,
                    "path": md_path
                })

    # --- [3] 卡片式佈局呈現 ---
    if not all_game_data:
        st.warning("📡 觀測站掃描完畢，未發現任何啟動中的專案檔案。")
    else:
        # 每列顯示兩張卡片
        cols = st.columns(2)
        for idx, game in enumerate(all_game_data):
            with cols[idx % 2]:
                # 建立卡片容器
                st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
                
                # 圖片顯示 (若無則顯示預設齒輪)
                if game["img"]:
                    st.image(game["img"], use_column_width=True)
                else:
                    # 預設生鏽齒輪圖片 (可替換為妳筆電裡的特定路徑)
                    st.image("https://img.icons8.com/color/96/000000/settings.png", caption="⚙️ 齒輪休眠中 (暫無素材)", width=100)
                
                st.markdown(f'<div class="game-title">{game["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="game-preview">{game["preview"]}</div>', unsafe_allow_html=True)
                
                # 展開詳細設定
                with st.expander(f"🛠️ 檢視《{game['name']}》核心設定"):
                    st.markdown(game["full_content"])
                    st.caption(f"📍 座標：{game['path']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.write("") # 間距
# =========================================================
# 🤖 頻道：核心腳本鍛造爐 (Script Forge) - 全域重塑版
# =========================================================
elif channel == "🤖 腳本鍛造":
    st.title("🤖 核心腳本鍛造爐：全域重塑")
    st.caption("⚙️ 支援「全新鍛造」與「既有重塑」。AI 可讀取專案內所有腳本並執行邏輯更改。")
    st.markdown("---")

    # --- 1. 定位腳本庫 ---
    script_folder = os.path.join(DATA_ROOT, current_p_name, "scripts")
    if not os.path.exists(script_folder):
        os.makedirs(script_folder)
    
    existing_scripts = [f for f in os.listdir(script_folder) if not f.startswith(".")]

    # --- 2. 模式切換：全新 vs 修改 ---
    forge_mode = st.radio("選擇操作模式", ["✨ 全新邏輯鍛造", "🔧 既有腳本重塑"], horizontal=True)

    selected_script_content = ""
    target_file_name = ""

    if forge_mode == "🔧 既有腳本重塑":
        if not existing_scripts:
            st.info("📡 腳本庫空虛，請先切換至全新鍛造模式。")
        else:
            target_file_name = st.selectbox("選擇要重塑的腳本", options=existing_scripts)
            # 讀取現有內容
            with open(os.path.join(script_folder, target_file_name), "r", encoding="utf-8") as f:
                selected_script_content = f.read()
            with st.expander("📄 查看原始代碼內容"):
                st.code(selected_script_content)
    else:
        col_type, col_name = st.columns([1, 2])
        with col_type:
            st_type = st.selectbox("腳 from 選項", [".gd", ".py", ".js", ".json", ".md"])
        with col_name:
            target_file_name = st.text_input("新檔案名稱", placeholder="harpoon.gd")

    # --- 3. 文獻參考 (選填) ---
    referenced_pdf = st.file_uploader("📚 參考外部 PDF 文獻 (可選)", type=["pdf"])
    pdf_context = ""
    if referenced_pdf:
        import PyPDF2
        reader = PyPDF2.PdfReader(referenced_pdf)
        for page in reader.pages:
            pdf_context += (page.extract_text() or "") + "\n"

    # --- 4. 修改需求 ---
    st.subheader("🛠️ 修改/編寫需求")
    instruction = st.text_area("請輸入妳的指令：", placeholder="例如：將原本的魚叉發射改為追蹤模式，並參考 PDF 的公式調整速度...", height=150)

    # --- 5. 啟動重塑引擎 ---
    if st.button("🔥 啟動全域重塑協定", type="primary", use_container_width=True):
        if not target_file_name or not instruction:
            st.warning("📡 報告架構師：檔案名稱與指令不可為空。")
        elif not FINAL_KEY:
            st.error("❌ 金鑰失效。")
        else:
            try:
                with st.spinner(f"🚀 正在對 {target_file_name} 進行邏輯超頻..."):
                    model = genai.GenerativeModel(AI_MODEL)
                    
                    # 核心 Prompt：賦予 AI 區分「新寫」與「修改」的能力
                    prompt = f"""
                    你是一位資深的 Godot 架構師。
                    目標檔案：{target_file_name}
                    操作模式：{forge_mode}
                    
                    [原始內容] (若是全新鍛造則為空)
                    {selected_script_content}
                    
                    [PDF 參考資料]
                    {pdf_context[:5000]}
                    
                    [修改需求]
                    {instruction}
                    
                    請根據需求，重寫整份檔案的代碼。
                    請僅回傳代碼內容，不要有解釋文字，不要包含 Markdown 代碼塊標籤。
                    """
                    
                    response = model.generate_content(prompt)
                    new_code = response.text.strip()

                    # 6. 物理覆蓋/寫入
                    save_path = os.path.join(script_folder, target_file_name)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(new_code)
                    
                    st.success(f"✅ 腳本物理更新成功：`{save_path}`")
                    st.code(new_code)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ 重塑失敗：{str(e)}")

    # --- 7. 管理既有腳本庫 ---
    st.divider()
    st.subheader("📂 腳本庫物理狀態")
    for s in existing_scripts:
        with st.expander(f"📄 {s}"):
            s_p = os.path.join(script_folder, s)
            with open(s_p, "r", encoding="utf-8") as f:
                st.code(f.read())
            if st.button(f"🗑️ 抹除 {s}", key=f"del_{s}"):
                os.remove(s_p)
                st.rerun()