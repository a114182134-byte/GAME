import streamlit as st
import google.generativeai as genai
from PIL import Image
import os, datetime, json, random, requests

# ==========================================
# 0. 核心自動更新系統
# ==========================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/a114182134-byte/GAME/main/ai/master_hub.py"

def auto_update():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            new_code = response.text
            with open(__file__, "r", encoding="utf-8") as f:
                current_code = f.read()
            if new_code.strip() != current_code.strip():
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(new_code)
                st.toast("🚀 偵測到新版本，已自動完成物理同步！")
                st.rerun() 
    except Exception: pass

auto_update()

# ==========================================
# 1. 系統初始化
# ==========================================
BASE_PATH = "all_projects"
CONFIG_FILE = os.path.join(BASE_PATH, "projects_config.json")

st.set_page_config(page_title="小白龍開發母站 - 全功能旗艦版", layout="wide", page_icon="⚓")

if "session_key" not in st.session_state: st.session_state.session_key = ""
if "last_ai_res" not in st.session_state: st.session_state.last_ai_res = ""

def init_system():
    if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)
    if not os.path.exists(CONFIG_FILE):
        init = {"餘燼航路": {"theme_color": "#D4AF37", "bg_color": "#1A1A1A", "prompt": "你是架構師", "local_script_path": "", "keys_list": []}}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(init, f, indent=4, ensure_ascii=False)
        return init
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

PROJECTS = init_system()

# ==========================================
# 2. 側邊欄中控
# ==========================================
with st.sidebar:
    st.title("⚙️ 核心中控台")
    current_p = st.selectbox("切換開發專案", list(PROJECTS.keys()))
    config = PROJECTS[current_p]
    
    st.divider()
    AI_MODEL = st.selectbox("AI 模型", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"])
    
    saved_keys = config.get("keys_list", [])
    sel_key = st.selectbox("金鑰清單", ["手動輸入"] + saved_keys) if saved_keys else "手動輸入"
    input_key = st.text_input("🔑 API Key", value="" if sel_key == "手動輸入" else sel_key, type="password")
    
    if st.button("🔐 鎖定並儲存金鑰"):
        st.session_state.session_key = input_key
        if input_key and input_key not in saved_keys:
            PROJECTS[current_p].setdefault("keys_list", []).append(input_key)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
        st.success("金鑰已備份")

    st.divider()
    channel = st.radio("功能頻道", ["💡 跨模態分析", "📜 AI 自動寫腳本", "📂 專案檔案總管", "🔍 歷史查詢", "📖 智慧答案之書", "🛠️ 管理部署"])

ACTIVE_KEY = st.session_state.session_key if st.session_state.session_key else input_key
st.markdown(f"<style>.main {{ background-color: {config['bg_color']}; color: {config['theme_color']}; }}</style>", unsafe_allow_html=True)

# 資料夾建立
LOG_DIR = os.path.join(BASE_PATH, current_p, "logs")
MEDIA_DIR = os.path.join(BASE_PATH, current_p, "media")
for d in [LOG_DIR, MEDIA_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# ==========================================
# 3. 頻道功能實作
# ==========================================

# --- 💡 跨模態分析 (含圖片/音效儲存) ---
if channel == "💡 跨模態分析":
    st.title("💡 跨模態分析引擎")
    col_input, col_preview = st.columns([1, 1])
    
    with col_input:
        user_text = st.text_area("✍️ 輸入指令或描述", placeholder="分析圖片美學或處理音效需求...")
        uploaded_img = st.file_uploader("🖼️ 上傳圖片 (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
        uploaded_audio = st.file_uploader("🎵 上傳音訊 (MP3/WAV)", type=['mp3', 'wav'])
        
    if st.button("🚀 執行多模態分析"):
        if not ACTIVE_KEY: st.error("❌ 請先鎖定金鑰")
        else:
            with st.spinner("AI 正在處理素材..."):
                genai.configure(api_key=ACTIVE_KEY)
                model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
                payload = [user_text if user_text else "請分析這些素材"]
                
                if uploaded_img:
                    img_data = Image.open(uploaded_img)
                    payload.append(img_data)
                    # 實體儲存
                    img_data.save(os.path.join(MEDIA_DIR, f"img_{datetime.datetime.now().strftime('%m%d_%H%M')}.png"))
                
                if uploaded_audio:
                    audio_bytes = uploaded_audio.read()
                    payload.append({"mime_type": uploaded_audio.type, "data": audio_bytes})
                    # 實體儲存
                    with open(os.path.join(MEDIA_DIR, uploaded_audio.name), "wb") as f:
                        f.write(audio_bytes)
                
                res = model.generate_content(payload)
                st.session_state.last_ai_res = res.text
                st.markdown(res.text)
                # 儲存對話日誌
                with open(os.path.join(LOG_DIR, f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"), "w", encoding="utf-8") as f:
                    f.write(res.text)

# --- 📜 AI 自動寫腳本 (含物理同步) ---
elif channel == "📜 AI 自動寫腳本":
    st.title(f"📜 核心代碼生成器 ({AI_MODEL})")
    task_desc = st.text_area("🔧 描述腳本功能", height=150)
    if st.button("🪄 生成代碼"):
        if not ACTIVE_KEY: st.error("❌ 未鎖定金鑰")
        else:
            with st.spinner("AI 重構中..."):
                genai.configure(api_key=ACTIVE_KEY)
                model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
                res = model.generate_content(f"使用 Godot 4.x。{task_desc}")
                st.session_state.last_ai_res = res.text
                st.markdown(res.text)
                with open(os.path.join(LOG_DIR, f"script_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"), "w", encoding="utf-8") as f:
                    f.write(res.text)

# --- 🔍 歷史查詢功能 ---
elif channel == "🔍 歷史查詢":
    st.title("🔍 專案歷史查詢")
    search_q = st.text_input("輸入關鍵字搜尋日誌内容...")
    
    log_files = sorted(os.listdir(LOG_DIR), reverse=True)
    for f_name in log_files:
        f_path = os.path.join(LOG_DIR, f_name)
        with open(f_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not search_q or search_q.lower() in content.lower():
                with st.expander(f"📅 {f_name}"):
                    st.markdown(content)

# --- 其他功能保持不變 ---
elif channel == "📂 專案檔案總管":
    st.title("📂 實體檔案管理")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.gd')]
        sel_f = st.selectbox("編輯腳本", files)
        if sel_f:
            with open(os.path.join(path, sel_f), "r", encoding="utf-8") as f:
                new_c = st.text_area("內容", f.read(), height=400)
            if st.button("💾 物理儲存"):
                with open(os.path.join(path, sel_f), "w", encoding="utf-8") as f: f.write(new_c)
                st.success("已更新")

elif channel == "📖 智慧答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 擷取啟示"):
        all_txt = []
        for fn in os.listdir(LOG_DIR):
            with open(os.path.join(LOG_DIR, fn), "r", encoding="utf-8") as f:
                all_txt.extend([l for l in f.readlines() if len(l) > 20])
        if all_txt: st.info(random.choice(all_txt))

elif channel == "🛠️ 管理部署":
    st.title("🛠️ 配置中心")
    with st.form("set"):
        p_path = st.text_input("💻 Godot Scripts 資料夾絕對路徑", config.get("local_script_path", ""))
        p_prompt = st.text_area("🤖 AI 指令公約", config.get("prompt", ""))
        if st.form_submit_button("💾 儲存設定"):
            PROJECTS[current_p].update({"local_script_path": p_path, "prompt": p_prompt})
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
            st.success("設定成功")

# --- 🔥 物理干涉引擎 (置底顯示) ---
if st.session_state.last_ai_res and channel in ["💡 跨模態分析", "📜 AI 自動寫腳本"]:
    st.divider()
    st.subheader("🚀 物理同步面板")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        target = st.selectbox("🎯 目標檔案", ["新檔案"] + [f for f in os.listdir(path) if f.endswith('.gd')])
        if target == "新檔案": target = st.text_input("命名", value="new_script.gd")
        if st.button("🔥 物理寫入"):
            blocks = st.session_state.last_ai_res.split("```")
            code = blocks[-2].split("\n", 1)[1] if len(blocks) >= 3 else st.session_state.last_ai_res
            with open(os.path.join(path, target), "w", encoding="utf-8") as f: f.write(code.strip())
            st.success(f"✅ 已寫入：{target}")
