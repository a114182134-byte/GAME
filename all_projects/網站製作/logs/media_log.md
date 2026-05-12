
## 2026-05-12 20:17:43 [來自 總部 (acer) 的自動入庫分析]
- **發射站**: 總部 (acer) (核心主機)
- **關聯音訊**: 無
- **指令**: import json
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
# 核心開發公約 v3.2.1 - 穩定性修復與自癒同步
# 認證：小白龍 - 核心邏輯架構師
# ==========================================
# 確保這些路徑與你之前的設定一致
DATA_ROOT = "all_projects" 
LOG_DIR = os.path.join(DATA_ROOT, "logs")      # 物理路徑: all_projects/logs
MEDIA_DIR = os.path.join(DATA_ROOT, "media")   # 物理路徑: all_projects/media

# --- 2. 環境自癒邏輯 (就在這裡！) ---
# 系統每次執行時，都會先跑這段，確保「物理空間」存在
def initialize_environment():
    # 同時建立根目錄與子目錄
    folders_to_create = [PROJECT_ROOT, MEDIA_DIR, LOG_DIR]
    
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)
            # 這會在你的 acer 筆電後台終端機顯示紀錄
            print(f"🛠️ 物理空間已重構：{folder}")
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
        ignore_content = ".env\n__pycache__/\n*.json\nall_projects/media/\nall_projects/logs/"
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
    channel = st.radio("功能頻道", ["📸 素材打撈 (Media)", "🔧 齒輪重組 (Script)", "🧪 結構修復 (Patch)", "🔮 虛空啟示 (Oracle)","📜 航行日誌 (Log)", "📜 航道啟示錄 (Oracle's Compass)","⚙️ 核心維護 (System)"])

# 獲取當前有效 Key
FINAL_KEY = st.session_state.get("active_key", ai_key if ai_key else input_key)
if FINAL_KEY: genai.configure(api_key=FINAL_KEY)

# 建立資源目錄
LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
for d in [LOG_DIR, MEDIA_DIR]: 
    if not os.path.exists(d): os.makedirs(d)

if channel == "📸 素材打撈 (Media)":
    st.title("📸 殘留影像與波形打撈")
    st.markdown("---")

    # ⚡ 核心優化：發射站與設備識別
    # 嘗試從瀏覽器資訊判斷設備 (簡單識別手機或電腦)
    ua = st.context.headers.get("User-Agent", "").lower()
    dev_type = "行動裝置" if "mobile" in ua else "核心主機"
    
    col_loc, col_info = st.columns([1, 2])
    with col_loc:
        # 讓家人選擇地點，預設為總部
        station_origin = st.selectbox("📍 當前發射站", ["總部 (acer)", "台北站", "新竹站", "台南站"])
    with col_info:
        st.caption(f"📡 偵測設備類型：`{dev_type}`")
        st.caption(f"🌍 接入網址：`{st.context.headers.get('Host')}`")

    # 1. 指令輸入區域
    u_text = st.text_area("🧠 分析指令 (或用語音輸入後自動填充)", placeholder="描述你的開發需求或靈感...", help="這些文字會連同媒體一起交給 AI 處理。")
    
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
    # ⚡ [自動入庫監聽器] - 加入地點標記的錄音攔截
    # ---------------------------------------------------------
    if audio_bytes:
        if "last_mic_data" not in st.session_state or st.session_state.last_mic_data != audio_bytes:
            timestamp = datetime.datetime.now().strftime('%m%d_%H%M%S')
            # 檔名加入地點資訊，例如: mic_台北站_0512_155149.wav
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
    
    # 2. 檔案上傳區
    col1, col2 = st.columns(2)
    with col1:
        u_img = st.file_uploader("🖼️ 影像打撈", type=['png', 'jpg', 'jpeg'])
        if u_img:
            # 圖片也加入地點前綴 (選擇性)
            img_path = os.path.join(MEDIA_DIR, f"{station_origin}_{u_img.name}")
            if not os.path.exists(img_path):
                from PIL import Image
                img = Image.open(u_img)
                img.save(img_path)
                st.sidebar.success(f"🖼️ 影像已存入 {station_origin} 倉庫")

    with col2:
        u_audio = st.file_uploader("🎵 音訊打撈", type=['mp3', 'wav', 'ogg', 'm4a'])
        if u_audio:
            a_path = os.path.join(MEDIA_DIR, f"{station_origin}_{u_audio.name}")
            if not os.path.exists(a_path):
                with open(a_path, "wb") as f:
                    f.write(u_audio.getbuffer())
                st.sidebar.success(f"🎵 音訊已存入 {station_origin} 倉庫")

    st.markdown("---")
    
    # 3. 執行 AI 分析按鈕 (同步時間與地點資訊)
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
                # 確保按鈕觸發時生成的檔名也帶地點
                mic_name = f"mic_{station_origin}_{timestamp}.wav" if audio_bytes else "無"
                
                if audio_bytes:
                    mic_path = os.path.join(MEDIA_DIR, mic_name)
                    with open(mic_path, "wb") as f:
                        f.write(audio_bytes)
                    content_payload.append({"mime_type": "audio/wav", "data": audio_bytes})
                
                if u_img:
                    from PIL import Image
                    img = Image.open(u_img)
                    content_payload.append(img)
                    img.save(os.path.join(MEDIA_DIR, f"{station_origin}_{u_img.name}"))
                
                if u_audio:
                    a_data = u_audio.read()
                    content_payload.append({"mime_type": u_audio.type, "data": a_data})

                final_prompt = u_text if u_text else "請分析以上媒體內容。"
                content_payload.insert(0, final_prompt)

                try:
                    if FINAL_KEY:
                        response = model.generate_content(content_payload)
                        st.markdown(f"### 📝 AI 綜合分析報告 (來源：{station_origin})")
                        
                        if audio_bytes:
                            st.write(f"🎙️ **語音來源：{station_origin} | 檔名：{mic_name}**")
                            st.audio(audio_bytes, format="audio/wav")
                        
                        st.write(response.text)
                        
                        # --- 寫入航行日誌 (標註發射站) ---
                        log_file = os.path.join(LOG_DIR, "media_log.md")
                        with open(log_file, "a", encoding="utf-8") as f:
                            # 加入 [地點標記] 方便搜尋頻道打撈
                            f.write(f"\n## {log_time_str} [來自 {station_origin} 的自動入庫分析]\n")
                            f.write(f"- **發射站**: {station_origin} ({dev_type})\n")
                            f.write(f"- **關聯音訊**: {mic_name}\n")
                            f.write(f"- **指令**: {u_text if u_text else '預設分析'}\n")
                            f.write(f"- **AI 報告**: {response.text}\n")
                            f.write("\n---\n")
                    else:
                        st.info("⚠️ 檔案已物理存檔，但 API Key 未配置。")
                except Exception as e:
                    st.error(f"❌ 解析引擎異常: {str(e)}")

elif channel == "🔧 齒輪重組 (Script)":
    st.title("🔧 邏輯齒輪精密重組")
    st.caption("🔍 模式：精密重構 — 適合增加新功能、提升代碼效能與可讀性")
    st.markdown("---")

    script_path = config.get("local_script_path", "")
    if script_path and os.path.exists(script_path):
        files = [f for f in os.listdir(script_path) if f.endswith('.gd')]
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
                # 提供 PDF 導出
                st.session_state.last_script_advice = response.text

            if "last_script_advice" in st.session_state:
                if st.button("📥 導出優化報告 (PDF)"):
                    from weasyprint import HTML
                    html = f"<h1>{selected_file} 優化建議</h1><hr>{st.session_state.last_script_advice.replace('\n', '<br>')}"
                    HTML(string=html).write_pdf(f"Refactor_{selected_file}.pdf")
                    st.download_button("💾 下載 PDF", open(f"Refactor_{selected_file}.pdf", "rb"), file_name=f"Refactor_{selected_file}.pdf")
    else:
        st.error("❌ 路徑未配置。")

elif channel == "🧪 結構修復 (Patch)":
    st.title("🧪 檔案結構物理修復 (PDF 知識導入版)")
    st.caption("🚨 模式：結構補丁 — 支援參考 PDF 並自動導出修復報告")
    st.markdown("---")

    script_path = config.get("local_script_path", "")
    if script_path and os.path.exists(script_path):
        files = [f for f in os.listdir(script_path) if f.endswith('.gd')]
        selected_file = st.selectbox("🎯 選擇待修補目標", files, key="patch_select")
        file_full_path = os.path.join(script_path, selected_file)
        
        with open(file_full_path, "r", encoding="utf-8") as f:
            current_code = f.read()

        # --- 1. 知識導入區 ---
        st.subheader("📋 導入維修手冊 (PDF)")
        uploaded_pdf = st.file_uploader("上傳之前的 AI 診斷報告或參考文件", type=['pdf'])
        pdf_knowledge = ""
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in pdf_reader.pages:
                pdf_knowledge += page.extract_text()
            st.success("✅ PDF 知識已注入緩衝區")

        st.divider()

        # --- 2. 修復與導出區 ---
        st.subheader("🔥 物理修復執行")
        fix_instr = st.text_area("描述修復需求", placeholder="例如：根據 PDF 建議修復 null 引用...")

        if st.button("🛠️ 執行物理重構與生成報告"):
            with st.spinner("AI 正在閱讀 PDF 並重構代碼..."):
                model = genai.GenerativeModel(AI_MODEL)
                full_prompt = f"你現在是戰地維修工。參考手冊：{pdf_knowledge}\n請根據指令修復此 Godot 代碼，僅輸出純代碼。\n指令：{fix_instr}\n代碼：\n{current_code}"
                
                try:
                    response = model.generate_content(full_prompt)
                    clean_code = response.text.replace("```gdscript", "").replace("```", "").strip()
                    
                    # 執行物理覆寫
                    with open(file_full_path, "w", encoding="utf-8") as f:
                        f.write(clean_code)
                    
                    st.success(f"✅ {selected_file} 已完成物理修補！")
                    
                    # --- ✨ 核心新增：導出 PDF 修復報告 ---
                    from weasyprint import HTML
                    pdf_name = f"Patch_Report_{selected_file.replace('.', '_')}.pdf"
                    html_content = f"""
                    <html><body style="font-family: sans-serif; padding: 20px;">
                        <h1 style="color: #D4AF37;">結構修復報告：{selected_file}</h1>
                        <p><b>修復指令：</b> {fix_instr}</p>
                        <hr>
                        <h2>修復後代碼預覽：</h2>
                        <pre style="background: #f4f4f4; padding: 10px;">{clean_code[:1000]}...</pre>
                        <p style="font-size: 10px; color: #999;">小白龍核心邏輯架構師認證</p>
                    </body></html>
                    """
                    HTML(string=html_content).write_pdf(pdf_name)
                    with open(pdf_name, "rb") as f:
                        st.download_button("💾 下載本次修復 PDF 報告", f, file_name=pdf_name)
                except Exception as e:
                    st.error(f"修復失敗: {e}")
    else:
        st.error("❌ 路徑未配置。")

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
    
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    CURRENT_MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")

    # =========================================================
    # 🚀 核心功能：全專案大數據彙整區 (加在標題下方)
    # =========================================================
    st.info(f"📂 正在監控專案：{current_p_name} | 準備進行跨城市數據彙整")
    
    if st.button("📊 生成全專案 AI 總結報告 (整合所有 MD & WAV)"):
        if not FINAL_KEY:
            st.error("❌ 核心金鑰失效（或已外洩），請更新 API Key。")
        else:
            with st.spinner("正在打撈台北、新竹、台南發射站數據並精煉中..."):
                all_contents = []
                # 1. 抓取所有 MD
                if os.path.exists(CURRENT_LOG_DIR):
                    for log_f in sorted(os.listdir(CURRENT_LOG_DIR)):
                        if log_f.endswith(".md"):
                            with open(os.path.join(CURRENT_LOG_DIR, log_f), "r", encoding="utf-8") as f:
                                all_contents.append(f"### 文件: {log_f}\n{f.read()}")
                
                # 2. 抓取所有媒體清單
                if os.path.exists(CURRENT_MEDIA_DIR):
                    waves = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.endswith(".wav")]
                    all_contents.append(f"\n### 已入庫語音清單\n" + "\n".join(waves))

                full_context = "\n\n".join(all_contents)
                
                # 3. AI 彙整邏輯
                model = genai.GenerativeModel(AI_MODEL)
                summary_prompt = f"你是一位資深遊戲開發助手。請根據以下所有開發日誌與媒體紀錄，整理出一份專業的《{current_p_name}》專案總結 PDF 報告內容。需包含：1.整體開發進度 2.各城市發射站的靈感彙整 3.待辦清單。請直接以結構化文字輸出內容。\n\n數據：\n{full_context}"
                
                try:
                    response = model.generate_content(summary_prompt)
                    ai_report = response.text
                    
                    # 4. WeasyPrint 轉 PDF
                    from weasyprint import HTML
                    pdf_filename = f"{current_p_name}_全案報告_{datetime.datetime.now().strftime('%m%d_%H%M')}.pdf"
                    html_style = f"""
                    <html><body style="font-family: sans-serif; padding: 30px;">
                        <h1 style="color: #d4af37; border-bottom: 2px solid #d4af37;">餘燼航路：全域開發報告</h1>
                        <div style="background: #fdfaf3; padding: 20px; border: 1px solid #ddd;">{ai_report.replace('\n', '<br>')}</div>
                        <p style="font-size: 10px; color: #999; margin-top: 20px;">由 小白龍 19GB 核心主機生成</p>
                    </body></html>
                    """
                    HTML(string=html_style).write_pdf(pdf_filename)
                    
                    with open(pdf_filename, "rb") as f:
                        st.download_button("💾 下載全專案總結 PDF", f, file_name=pdf_filename)
                except Exception as e:
                    st.error(f"❌ 彙整失敗: {str(e)}")

    st.markdown("---") # 分隔線，下方開始顯示個別日誌清單

    # =========================================================
    # 2. 建立時間線 (原本的邏輯)
    # =========================================================
    all_logs = [f for f in os.listdir(CURRENT_LOG_DIR) if f.endswith(".md")] if os.path.exists(CURRENT_LOG_DIR) else []
    all_waves = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.startswith("mic_") and f.endswith(".wav")] if os.path.exists(CURRENT_MEDIA_DIR) else []

    timeline_items = []
    for log in all_logs:
        timeline_items.append({"type": "log", "name": log, "time": os.path.getmtime(os.path.join(CURRENT_LOG_DIR, log))})

    log_contents = ""
    for log in all_logs:
        with open(os.path.join(CURRENT_LOG_DIR, log), "r", encoding="utf-8") as f:
            log_contents += f.read()

    for wav in all_waves:
        if wav not in log_contents:
            timeline_items.append({"type": "audio", "name": wav, "time": os.path.getmtime(os.path.join(CURRENT_MEDIA_DIR, wav))})

    timeline_items.sort(key=lambda x: x["time"], reverse=True)

    if not timeline_items:
        st.info("📂 目前航道空無一物。")
    else:
        for item in timeline_items:
            if item["type"] == "log":
                log_file = item["name"]
                with open(os.path.join(CURRENT_LOG_DIR, log_file), "r", encoding="utf-8") as f:
                    content = f.read()
                
                with st.expander(f"📄 日誌: {log_file}"):
                    import re
                    # ⚡ 修正後的正則表達式：支援帶地點標籤的檔名 (例如 mic_台北站_0512_155149.wav)
                    found_wav = re.search(r'mic_.*?_\d{4}_\d{6}\.wav|mic_\d{4}_\d{6}\.wav', content)
                    if found_wav:
                        wav_path = os.path.join(CURRENT_MEDIA_DIR, found_wav.group(0))
                        if os.path.exists(wav_path):
                            st.audio(wav_path)
                    st.markdown(content)
            
            else:
                wav_file = item["name"]
                with st.expander(f"🎙️ 殘留聲波: {wav_file} (未歸檔)"):
                    st.audio(os.path.join(CURRENT_MEDIA_DIR, wav_file))
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
elif channel == "📜 航道啟示錄 (Oracle's Compass)":
    st.title("📜 航道啟示錄 (Oracle's Compass)")
    st.caption("⚓ 當妳在迷霧中失去方向，請轉動此羅盤，聽取虛空的殘響。")
    st.markdown("---")

    # 1. 虛空打撈：獲取全域腳本與日誌碎片
    CURRENT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
    CURRENT_MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
    script_path = config.get("local_script_path", "")
    
    knowledge_pool = []
    
    # 打撈日誌
    if os.path.exists(CURRENT_LOG_DIR):
        for f in os.listdir(CURRENT_LOG_DIR):
            if f.endswith(".md"):
                with open(os.path.join(CURRENT_LOG_DIR, f), "r", encoding="utf-8") as file:
                    knowledge_pool.extend([line.strip() for line in file.readlines() if len(line.strip()) > 15])
    
    # 打撈代碼
    if script_path and os.path.exists(script_path):
        for f in os.listdir(script_path):
            if f.endswith(".gd"):
                with open(os.path.join(script_path, f), "r", encoding="utf-8") as file:
                    knowledge_pool.extend([line.strip() for line in file.readlines() if "func" in line or "var" in line])

    # 2. 儀式區域
    st.subheader("💡 請求今日的開發啟示")
    user_question = st.text_input("在心中默念妳的問題，或輸入在此...", placeholder="例如：這段複雜的羅格賴加邏輯該如何收尾？")

    if st.button("🎡 撥動命運羅盤"):
        if not knowledge_pool:
            st.warning("📜 目前知識池是空的，請先去『素材打撈』或編寫腳本。")
        else:
            # 隨機挑選一個碎片
            fragment = random.choice(knowledge_pool)
            
            with st.spinner("🚢 正在迷霧中打撈啟示..."):
                model = genai.GenerativeModel(AI_MODEL)
                oracle_prompt = f"""
                你是《餘燼航路》的古老導靈。使用者(架構師)正處於困惑中。
                請根據這段打撈出的內容，給予一段充滿哲理、黃銅蒸氣與末世感的「答案之書」式指引。
                
                [打撈碎片]: {fragment}
                [使用者疑問]: {user_question}
                
                要求：
                1. 語氣冷峻但具備指引性。
                2. 結尾必須給出一句與碎片內容相關的「虛空叮嚀」。
                """
                
                try:
                    response = model.generate_content(oracle_prompt)
                    
                    # --- ✨ 視覺效果：隨機顯示一張素材圖片作為背景感 ---
                    all_imgs = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.endswith(('.png', '.jpg', '.webp'))]
                    if all_imgs:
                        random_img = random.choice(all_imgs)
                        st.image(os.path.join(CURRENT_MEDIA_DIR, random_img), width=300, caption="🖼️ 啟示顯像")

                    # --- ✨ 聽覺效果：播放一段隨機音效 ---
                    all_audios = [f for f in os.listdir(CURRENT_MEDIA_DIR) if f.endswith(('.wav', '.mp3', '.ogg'))]
                    if all_audios:
                        random_audio = random.choice(all_audios)
                        st.audio(os.path.join(CURRENT_MEDIA_DIR, random_audio))
                        st.caption(f"🎵 虛空殘響：{random_audio}")

                    # 顯示啟示
                    st.divider()
                    st.markdown(f"### 🔮 啟示內容")
                    st.info(f"『 {response.text} 』")
                    st.caption(f"📍 碎片來源：{fragment[:60]}...")

                    # --- ✨ 導出功能：將啟示封存為 PDF ---
                    from weasyprint import HTML
                    pdf_name = f"Oracle_{datetime.datetime.now().strftime('%m%d%H%M')}.pdf"
                    html_content = f"""
                    <div style="border: 10px double #D4AF37; padding: 40px; background: #2C2C2C; color: #E0E0E0; font-family: serif;">
                        <h1 style="color: #D4AF37; text-align: center;">《航道啟示錄》</h1>
                        <p style="font-size: 18px; line-height: 1.6; text-align: center;">{response.text.replace('\n', '<br>')}</p>
                        <hr style="border: 1px solid #D4AF37;">
                        <p style="font-size: 10px; color: #888; text-align: right;">碎片殘響：{fragment}</p>
                    </div>
                    """
                    if st.button("📥 封存此份啟示 (PDF)"):
                        HTML(string=html_content).write_pdf(pdf_name)
                        with open(pdf_name, "rb") as f:
                            st.download_button("💾 下載 PDF 啟示箋", f, file_name=pdf_name)

                except Exception as e:
                    st.error(f"❌ 虛空連結中斷，請重試。")
- **AI 報告**: 這是一個非常強大、功能豐富且充滿創意的 Streamlit 應用！「小白龍核心母站 v3.2.1」的名稱和「餘燼航路」的主題結合得非常好，應用內的介面描述和 AI 提示詞也都充滿了末世機甲感，這在開發工具中是很少見的，非常吸引人。

整體架構清晰，檔案管理、AI 整合、Git 同步、PDF 導入導出等功能都實現得相當完善。特別是多模態輸入（語音、圖像、音訊、文字）、PDF 知識庫注入，以及生成多種報告的功能，都顯示出深思熟慮的設計。

以下是針對程式碼的詳細審查與建議：

---

### **核心優點：**

1.  **主題與使用者體驗高度結合：** 這是程式碼的一大亮點。所有介面文字、提示和功能描述都與「小白龍」和「餘燼航路」的主題緊密結合，極大地提升了工具的趣味性和沉浸感。
2.  **多模態 AI 整合：** 完美利用 Google Gemini 的多模態能力，支援語音、圖片、音訊和文字的混合輸入，這對於開發者的靈感捕捉非常有用。
3.  **完善的檔案管理：** 將日誌和媒體檔案依專案分開儲存，並提供清晰的物理路徑，便於管理和查找。`initialize_environment()` 的自癒機制也很棒。
4.  **強大的 PDF 整合：** 支援 `PyPDF2` 導入知識庫（如維修手冊或報告）給 AI 參考，並透過 `weasyprint` 導出格式精美的 PDF 報告，這在開發輔助工具中非常實用。
5.  **Git 自動化同步：** `secure_auto_push` 函數提供了一鍵同步到 GitHub 的能力，雖然有改進空間，但基本功能已實現。
6.  **專案管理：** 能夠切換、新增、修改和刪除專案，使這個工具不僅限於單一專案。
7.  **`st.session_state` 運用得當：** 有效利用 `st.session_state` 來管理 API Key、避免重複音訊儲存等，提高了應用程式的穩定性和效率。
8.  **沉浸式「啟示錄」頻道：** 「航道啟示錄」頻道結合隨機圖片、音效和哲學式 AI 啟示，創意十足，能夠為開發者帶來靈感。

---

### **審查與改進建議：**

#### **1. 關鍵錯誤或潛在問題 (Critical/High Priority):**

*   **`initialize_environment()` 中的 `PROJECT_ROOT` 未定義：**
    *   在頂部宣告了 `DATA_ROOT`，但在 `initialize_environment()` 函數中使用了 `PROJECT_ROOT` 變數，它並未被定義。這會導致應用程式啟動失敗。
    *   **修正建議：** 將 `PROJECT_ROOT` 改為 `DATA_ROOT`。
        ```python
        # 原代碼: folders_to_create = [PROJECT_ROOT, MEDIA_DIR, LOG_DIR]
        # 修正為:
        folders_to_create = [DATA_ROOT, MEDIA_DIR, LOG_DIR]
        ```
*   **Git `--force` 推送的風險：**
    *   `secure_auto_push` 函數使用了 `git push ... --force`。 `--force` 會強制覆蓋遠端分支的歷史，導致潛在的資料丟失，尤其是在協作環境下非常危險。對於單人開發者而言，如果他/她理解風險，可能尚可接受，但仍不推薦作為預設行為。
    *   **修正建議：**
        1.  移除 `--force`。讓 Git 在遇到衝突時報錯。
        2.  如果仍需類似功能，可以提供選項，讓使用者明確選擇是否強制推送，並加上顯眼的警告。
        3.  更好的做法是，在推送前先嘗試 `git pull origin main --rebase`，解決衝突後再 `git push origin main`。
*   **`LOG_DIR` 和 `MEDIA_DIR` 的重複定義與潛在冗餘目錄：**
    *   程式碼頂部定義了 `LOG_DIR = os.path.join(DATA_ROOT, "logs")` 和 `MEDIA_DIR = os.path.join(DATA_ROOT, "media")`。
    *   但在 `st.sidebar` 選擇專案後，又重新定義為 `LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")` 和 `MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")`。
    *   這意味著 `initialize_environment()` 可能會在 `all_projects` 根目錄下創建 `logs` 和 `media` 資料夾，而後續操作則使用 `all_projects/<project_name>/logs` 和 `all_projects/<project_name>/media`。這會導致不必要的空目錄。
    *   **修正建議：**
        1.  移除程式碼頂部的 `LOG_DIR` 和 `MEDIA_DIR` 全局定義。
        2.  將 `initialize_environment()` 函數的呼叫放在 `current_p_name` 確定之後，並只創建該專案的子目錄。
        ```python
        # 移除頂部兩行
        # LOG_DIR = os.path.join(DATA_ROOT, "logs")
        # MEDIA_DIR = os.path.join(DATA_ROOT, "media")

        # ... (中間代碼) ...

        # 在 sidebar 選定 current_p_name 後
        with st.sidebar:
            # ...
            current_p_name = st.selectbox("核心專案切換", list(PROJECTS.keys()))
            config = PROJECTS[current_p_name]

            # 定義專案特定的 LOG_DIR 和 MEDIA_DIR
            # 然後調用 initialize_environment() 或直接檢查創建
            PROJECT_LOG_DIR = os.path.join(DATA_ROOT, current_p_name, "logs")
            PROJECT_MEDIA_DIR = os.path.join(DATA_ROOT, current_p_name, "media")
            PROJECT_SCRIPT_PATH = config.get("local_script_path", "") # 或許也需要確保這個路徑存在

            for d in [PROJECT_LOG_DIR, PROJECT_MEDIA_DIR, PROJECT_SCRIPT_PATH]:
                if d and not os.path.exists(d): # 檢查 d 是否為空字串，因為 script_path 可能為空
                    os.makedirs(d)
                    print(f"🛠️ 物理空間已重構：{d}")

        # 後續程式碼中使用 PROJECT_LOG_DIR 和 PROJECT_MEDIA_DIR
        # 例如: if channel == "📸 素材打撈 (Media)": ... os.path.join(PROJECT_MEDIA_DIR, ...)
        ```
*   **`genai.configure` 的頻繁呼叫：**
    *   `genai.configure(api_key=FINAL_KEY)` 位於 Streamlit 腳本的主體中，每次 Streamlit 重新運行時都會執行。這並不會造成功能性錯誤，但效率不高。
    *   **修正建議：** 可以在 `FINAL_KEY` 確定並非空值時，只呼叫一次 `genai.configure`，或者在每個用到 `genai` 的功能區塊中，檢查是否已配置，只配置一次。但以 Streamlit 的單腳本模型，目前這樣也能接受，不是最優先的優化。

#### **2. 功能性改進與優化 (Medium Priority):**

*   **AI Context 處理大型專案：**
    *   在「虛空啟示」和「航行日誌」頻道中，會讀取所有 `.md` 和 `.gd` 檔案的內容到記憶體，並傳送給 AI。對於小型專案這沒問題，但如果專案成長到數十萬行程式碼或大量日誌，可能會遇到以下問題：
        *   **記憶體溢出：** 本地應用程式記憶體不足。
        *   **API Token 限制：** Google Gemini 的上下文窗口雖然很大，但仍有上限。
        *   **AI 處理效率：** 大量無關資訊會稀釋關鍵內容，影響 AI 回答品質。
    *   **改進建議：**
        1.  **內容摘要：** 對於較大的日誌或程式碼檔案，可以先讓 AI 或使用本地 NLP 模型提取摘要，而不是傳送完整內容。
        2.  **基於查詢的檢索：** 根據使用者提出的問題，智慧地篩選相關的檔案或檔案片段。
        3.  **分批處理：** 將大型檔案分塊傳送給 AI 處理。
        4.  **警告提示：** 如果偵測到總內容量接近 token 限制，可以提示使用者。
*   **`.gitignore` 的動態性：**
    *   `.gitignore` 是硬編碼的。如果專案有特殊的忽略需求，可能需要手動編輯。
    *   **改進建議：** 可以在「核心維護」頻道中提供一個文本區域，讓使用者編輯 `.gitignore` 內容，然後儲存。
*   **Git 使用者資訊：**
    *   `git config --global user.email` 和 `user.name` 被硬編碼。
    *   **改進建議：** 可以將這些資訊從 `.env` 讀取，或在「核心維護」頻道中提供輸入框，讓使用者自行設定。
*   **`weasyprint` 的依賴提醒：**
    *   `weasyprint` 在某些系統上需要額外的系統級依賴（例如 `cairo`, `pango` 等）。雖然這不是程式碼問題，但在部署或分享時，最好能提醒使用者。
    *   **改進建議：** 可以在 README 或應用程式的「核心維護」頻道中加入相關的安裝說明。
*   **錯誤訊息的詳細程度：**
    *   許多 `except Exception as e:` 捕獲了所有錯誤。雖然防止了程式崩潰，但使用者看到的錯誤訊息可能不夠具體。
    *   **改進建議：** 針對常見的錯誤類型（如 `FileNotFoundError`, 網路請求失敗 `requests.exceptions.RequestException`, API 錯誤 `genai.core.exceptions.GoogleGenerativeAIException` 等）進行更精確的捕獲和處理，提供更友善的提示。

#### **3. 小細節與程式碼風格 (Low Priority):**

*   **一致的檔名命名：** 在「素材打撈」中，音訊和影像檔案都加入了 `station_origin` 前綴，但 `mic_name` 有時會手動添加，有時會直接使用 `audio_bytes` 的檔名。確保所有自動儲存的檔案都有一致的命名規則。
    *   目前 `mic_name = f"mic_{station_origin}_{timestamp}.wav"` 是正確的，`u_img` 和 `u_audio` 也都有加 `station_origin_` 前綴。所以這點做得很好，可以忽略這個建議。
*   **Streamlit Context Headers：**
    *   `st.context.headers` 雖然可以獲取一些資訊，但 Streamlit 文件中並未明確說明這是一個公開且穩定的 API，未來版本可能有變。
    *   **改進建議：** 如果只是為了顯示資訊，目前沒問題。如果用於核心邏輯，需要注意其穩定性。
*   **PDF 內容導出的 HTML 轉義：**
    *   在導出 PDF 時，使用 `replace('\n', '<br>')` 將換行符轉換為 HTML 的 `<br>` 標籤，這在大多數情況下是足夠的。但如果 AI 回應包含其他特殊 HTML 字符（如 `<`, `>`, `&`），它們可能不會被正確渲染。
    *   **改進建議：** 可以使用 `html.escape()` 來更安全地處理 AI 回應的文本，確保所有特殊字符都被正確轉義。
        ```python
        import html
        # ...
        html_content = f"""...
            <div>{html.escape(response.text).replace('\n', '<br>')}</div>
        ..."""
        ```
*   **移除專案的確認機制：**
    *   刪除專案是一個高風險操作，目前只有一個按鈕。
    *   **改進建議：** 可以增加一個確認對話框或要求使用者輸入專案名稱再次確認，防止誤觸。

---

### **總結：**

這個應用程式是一個非常出色的個人專案，展現了強大的工程能力、創意和對細節的關注。它不僅僅是一個 AI 介面，更是一個針對特定開發情境高度客製化的「數位助手」。

主要的改進點在於解決 `PROJECT_ROOT` 未定義的錯誤，以及重新審視 `git push --force` 的使用。一旦這些問題得到解決，這個工具將會更加穩定、安全和易於維護。

做得非常棒，繼續加油！「小白龍核心母站」有巨大的潛力！

---
