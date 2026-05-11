import streamlit as st
import google.generativeai as genai
from PIL import Image
import os, datetime, json, random, re

# ==========================================
# 1. 初始化
# ==========================================
BASE_PATH = "all_projects"
CONFIG_FILE = os.path.join(BASE_PATH, "projects_config.json")

st.set_page_config(page_title="小白龍開發母站", layout="wide", page_icon="⚓")

if "session_key" not in st.session_state: st.session_state.session_key = ""
if "last_ai_res" not in st.session_state: st.session_state.last_ai_res = ""

def init_system():
    if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)
    if not os.path.exists(CONFIG_FILE):
        init = {"餘燼航路": {"theme_color": "#D4AF37", "bg_color": "#1A1A1A", "prompt": "你是分析師", "api_key": "", "local_script_path": ""}}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(init, f, indent=4, ensure_ascii=False)
        return init
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for p in data:
            if "local_script_path" not in data[p]: data[p]["local_script_path"] = ""
        return data

PROJECTS = init_system()

# ==========================================
# 2. 側邊欄
# ==========================================
with st.sidebar:
    st.title("⚙️ 中控台")
    current_p = st.selectbox("專案", list(PROJECTS.keys()))
    config = PROJECTS[current_p]
    
    key_display = st.session_state.session_key if st.session_state.session_key else config.get("api_key", "")
    input_key = st.text_input("🔑 API Key", value=key_display, type="password")
    
    if st.button("🔐 鎖定金鑰"):
        st.session_state.session_key = input_key
        PROJECTS[current_p]["api_key"] = input_key
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
        st.success("✅ 已鎖定")
        st.rerun()
    
    channel = st.radio("頻道", ["💡 跨模態分析", "📂 資源檔案庫", "📜 歷史搜尋", "📖 智慧答案之書", "🛠️ 管理部署"])

ACTIVE_KEY = st.session_state.session_key if st.session_state.session_key else config.get("api_key", "")
st.markdown(f"<style>.main {{ background-color: {config['bg_color']}; color: {config['theme_color']}; }}</style>", unsafe_allow_html=True)

LOG_DIR = os.path.join(BASE_PATH, current_p, "logs")
ASSET_DIR = os.path.join(BASE_PATH, current_p, "assets")
for d in [LOG_DIR, ASSET_DIR]:
    if not os.path.exists(d): os.makedirs(d)

# ==========================================
# 3. 頻道功能
# ==========================================

if channel == "💡 跨模態分析":
    st.title("🔍 分析引擎")
    idea_txt = st.text_area("✍️ 想法", height=100)
    if st.button("🚀 啟動分析"):
        if not ACTIVE_KEY: st.error("❌ 無金鑰")
        else:
            try:
                genai.configure(api_key=ACTIVE_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=config["prompt"])
                res = model.generate_content([idea_txt])
                st.session_state.last_ai_res = res.text
                st.markdown(res.text)
                with open(os.path.join(LOG_DIR, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"), "w", encoding="utf-8") as f:
                    f.write(res.text)
            except Exception as e: st.error(f"失敗: {e}")

    if st.session_state.last_ai_res:
        st.divider()
        target_f = st.text_input("檔名", value="harpoon.gd")
        if st.button("🧬 物理覆寫"):
            path = config.get("local_script_path", "")
            if not path or not os.path.exists(path): st.error("❌ 路徑錯誤")
            else:
                # 使用 ASCII 避開正則表達式語法錯誤
                p = chr(96)*3 + r"(?:\w+)?\n([\s\S]*?)\n" + chr(96)*3
                blocks = re.findall(p, st.session_state.last_ai_res)
                code = blocks[-1].strip() if blocks else st.session_state.last_ai_res
                with open(os.path.join(path, target_f), "w", encoding="utf-8") as f:
                    f.write(code)
                st.success("🔥 寫入成功")

elif channel == "📂 資源檔案庫":
    st.title("📂 資源存儲")
    up = st.file_uploader("上傳", type=['png', 'jpg', 'mp3', 'wav'])
    name = st.text_input("備註名稱")
    if st.button("確認上傳") and up and name:
        with open(os.path.join(ASSET_DIR, f"{name}.{up.name.split('.')[-1]}"), "wb") as f:
            f.write(up.read())
        st.rerun()
    
    for a in os.listdir(ASSET_DIR):
        p = os.path.join(ASSET_DIR, a)
        st.write(f"📄 {a}")
        if a.lower().endswith(('.png', '.jpg')): st.image(p)
        elif a.lower().endswith(('.mp3', '.wav')): st.audio(p)
        if st.button("🗑️ 刪除", key=a): os.remove(p); st.rerun()

elif channel == "📜 歷史搜尋":
    st.title("📜 歷史紀錄")
    for f in sorted(os.listdir(LOG_DIR), reverse=True):
        if st.button(f"📅 {f}"):
            with open(os.path.join(LOG_DIR, f), "r", encoding="utf-8") as file: st.markdown(file.read())

elif channel == "📖 智慧答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 擷取啟示"):
        lines = []
        for r, _, fs in os.walk(LOG_DIR):
            for f in fs:
                with open(os.path.join(r, f), "r", encoding="utf-8") as file:
                    lines.extend([l for l in file.readlines() if len(l) > 10])
        if lines: st.info(random.choice(lines))

elif channel == "🛠️ 管理部署":
    st.title("🛠️ 設定")
    with st.form("set"):
        p = st.text_input("💻 Godot 腳本資料夾路徑", config.get("local_script_path", ""))
        if st.form_submit_button("儲存"):
            PROJECTS[current_p]["local_script_path"] = p
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
            st.rerun()