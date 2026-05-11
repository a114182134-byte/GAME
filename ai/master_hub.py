import streamlit as st
import google.generativeai as genai
from PIL import Image
import os, datetime, json, random, requests

# ==========================================
# 0. 核心自動更新系統 (穩壓版 - 避免無限循環)
# ==========================================
CURRENT_VERSION = "3.1.2"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/a114182134-byte/GAME/main/ai/master_hub.py"

def auto_update():
    try:
        # 1. 抓取雲端最新代碼
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            new_code = response.text
            
            # 2. 提取雲端版本號
            remote_version_line = [l for l in new_code.split('\n') if 'CURRENT_VERSION =' in l]
            if remote_version_line:
                # 取得引號內的版本號
                remote_v = remote_version_line[0].split('"')[1]
                
                # 3. 版本號不一致才更新
                if remote_v != CURRENT_VERSION:
                    with open(__file__, "w", encoding="utf-8") as f:
                        f.write(new_code)
                    st.toast(f"🚀 偵測到新版本 {remote_v}，已自動完成物理同步！")
                    st.rerun() 
    except Exception:
        pass

auto_update()

# ==========================================
# 1. 系統初始化與路徑守衛
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
        return json.load(f)

PROJECTS = init_system()

# ==========================================
# 2. 側邊欄：中控配置
# ==========================================
with st.sidebar:
    st.title("⚙️ 核心中控台")
    current_p = st.selectbox("切換開發專案", list(PROJECTS.keys()))
    config = PROJECTS[current_p]
    
    st.divider()
    st.subheader(f"🏷️ 版本: {CURRENT_VERSION}")
    AI_MODEL = st.selectbox("AI 模型", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"])
    
    saved_keys = config.get("keys_list", [])
    sel_key = st.selectbox("金鑰清單", ["手動輸入"] + saved_keys) if saved_keys else "手動輸入"
    input_key = st.text_input("🔑 API Key", value="" if sel_key == "手動輸入" else sel_key, type="password")
    
    if st.button("🔐 鎖定並儲存"):
        st.session_state.session_key = input_key
        if input_key and input_key not in saved_keys:
            PROJECTS[current_p].setdefault("keys_list", []).append(input_key)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
        st.success("配置已保存")

    st.divider()
    channel = st.radio("功能頻道", ["💡 跨模態分析", "📜 AI 自動寫腳本", "📂 專案檔案總管", "🔍 歷史查詢", "📖 智慧答案之書", "🛠️ 管理部署"])

ACTIVE_KEY = st.session_state.session_key if st.session_state.session_key else input_key
st.markdown(f"<style>.main {{ background-color: {config['bg_color']}; color: {config['theme_color']}; }}</style>", unsafe_allow_html=True)

# 建立專案子資料夾
LOG_DIR = os.path.join(BASE_PATH, current_p, "logs")
MEDIA_DIR = os.path.join(BASE_PATH, current_p, "media")
for d in [LOG_DIR, MEDIA_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# ==========================================
# 3. 頻道功能實作
# ==========================================

# --- 💡 跨模態分析 ---
if channel == "💡 跨模態分析":
    st.title("💡 跨模態分析與儲存")
    u_text = st.text_area("✍️ 指令")
    u_img = st.file_uploader("🖼️ 圖片", type=['png', 'jpg', 'jpeg'])
    u_audio = st.file_uploader("🎵 音訊", type=['mp3', 'wav'])
    
    if st.button("🚀 執行分析"):
        if not ACTIVE_KEY: st.error("❌ 未鎖定金鑰")
        else:
            genai.configure(api_key=ACTIVE_KEY)
            model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
            content = [u_text if u_text else "請分析"]
            if u_img:
                img = Image.open(u_img)
                content.append(img)
                img.save(os.path.join(MEDIA_DIR, f"img_{datetime.datetime.now().strftime('%m%d_%H%M')}.png"))
            if u_audio:
                audio_data = u_audio.read()
                content.append({"mime_type": u_audio.type, "data": audio_data})
                with open(os.path.join(MEDIA_DIR, u_audio.name), "wb") as f: f.write(audio_data)
            
            res = model.generate_content(content)
            st.session_state.last_ai_res = res.text
            st.markdown(res.text)
            with open(os.path.join(LOG_DIR, f"media_{datetime.datetime.now().strftime('%m%d_%H%M')}.md"), "w", encoding="utf-8") as f:
                f.write(res.text)

# --- 📜 AI 自動寫腳本 ---
elif channel == "📜 AI 自動寫腳本":
    st.title("📜 AI 自動寫腳本")
    task = st.text_area("🔧 需求描述", height=150)
    if st.button("🪄 生成"):
        genai.configure(api_key=ACTIVE_KEY)
        model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
        res = model.generate_content(f"Godot 4.x。{task}")
        st.session_state.last_ai_res = res.text
        st.markdown(res.text)
        with open(os.path.join(LOG_DIR, f"script_{datetime.datetime.now().strftime('%m%d_%H%M')}.md"), "w", encoding="utf-8") as f:
            f.write(res.text)

# --- 🔍 歷史查詢 (修復版) ---
elif channel == "🔍 歷史查詢":
    st.title("🔍 歷史日誌查詢")
    q = st.text_input("關鍵字搜尋")
    if os.path.exists(LOG_DIR):
        files = sorted(os.listdir(LOG_DIR), reverse=True)
        for fn in files:
            f_path = os.path.join(LOG_DIR, fn)
            # 關鍵修正：跳過資料夾
            if os.path.isfile(f_path) and fn.endswith('.md'):
                with open(f_path, "r", encoding="utf-8") as f:
                    c = f.read()
                    if not q or q.lower() in c.lower():
                        with st.expander(f"📅 {fn}"): st.markdown(c)

# --- 📂 專案檔案總管 ---
elif channel == "📂 專案檔案總管":
    st.title("📂 實體檔案管理")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        files = [f for f in os.listdir(path) if f.endswith('.gd')]
        sel = st.selectbox("選取檔案", files)
        if sel:
            f_p = os.path.join(path, sel)
            with open(f_p, "r", encoding="utf-8") as f:
                new_c = st.text_area("編輯內容", f.read(), height=400)
            if st.button("💾 儲存至硬碟"):
                with open(f_p, "w", encoding="utf-8") as f: f.write(new_c)
                st.success("已更新")

# --- 📖 智慧答案之書 (修復版) ---
elif channel == "📖 智慧答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 擷取啟示"):
        all_lines = []
        if os.path.exists(LOG_DIR):
            for fn in os.listdir(LOG_DIR):
                f_path = os.path.join(LOG_DIR, fn)
                # 關鍵修正：確保它是檔案且是 .md 檔，才讀取
                if os.path.isfile(f_path) and fn.endswith('.md'):
                    with open(f_path, "r", encoding="utf-8") as f:
                        all_lines.extend([l.strip() for l in f.readlines() if len(l.strip()) > 15])
        if all_lines: 
            st.info(random.choice(all_lines))
        else:
            st.warning("日誌庫中沒有足夠的文字啟示。")

# --- 🛠️ 管理部署 ---
elif channel == "🛠️ 管理部署":
    st.title("🛠️ 專案配置")
    with st.form("set"):
        p_path = st.text_input("Godot Scripts 路徑", config.get("local_script_path", ""))
        p_prompt = st.text_area("AI 指令公約", config.get("prompt", ""))
        if st.form_submit_button("儲存設定"):
            PROJECTS[current_p].update({"local_script_path": p_path, "prompt": p_prompt})
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
            st.success("設定成功")

# --- 🔥 物理干涉置底 ---
if st.session_state.last_ai_res and channel in ["💡 跨模態分析", "📜 AI 自動寫腳本"]:
    st.divider()
    st.subheader("🚀 物理同步引擎")
    p = config.get("local_script_path", "")
    if p and os.path.exists(p):
        target = st.selectbox("🎯 目標腳本", ["新檔案"] + [f for f in os.listdir(p) if f.endswith('.gd')])
        if target == "新檔案": target = st.text_input("新檔名", value="harpoon.gd")
        if st.button("🔥 物理寫入硬碟"):
            blocks = st.session_state.last_ai_res.split("```")
            code = blocks[-2].split("\n", 1)[1] if len(blocks) >= 3 else st.session_state.last_ai_res
            with open(os.path.join(p, target), "w", encoding="utf-8") as f: f.write(code.strip())
            st.success(f"✅ 已成功覆寫檔案：{target}")

