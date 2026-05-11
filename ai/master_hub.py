import streamlit as st
import google.generativeai as genai
from PIL import Image
import os, datetime, json, random, requests

# ==========================================
# 0. 核心自動更新系統 (啟動即同步)
# ==========================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/a114182134-byte/GAME/main/ai/master_hub.py"

def auto_update():
    try:
        # 抓取雲端最新代碼
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            new_code = response.text
            # 讀取本地目前運行的檔案內容
            with open(__file__, "r", encoding="utf-8") as f:
                current_code = f.read()
            
            # 如果內容不一致，執行物理覆寫
            if new_code.strip() != current_code.strip():
                with open(__file__, "w", encoding="utf-8") as f:
                    f.write(new_code)
                st.toast("🚀 偵測到新版本，已自動完成物理同步！")
                st.rerun() 
    except Exception:
        pass # 離線或錯誤時跳過，確保程式能正常啟動

# 啟動時先執行檢查
auto_update()

# ==========================================
# 1. 系統初始化
# ==========================================
BASE_PATH = "all_projects"
CONFIG_FILE = os.path.join(BASE_PATH, "projects_config.json")

st.set_page_config(page_title="小白龍開發母站 - 旗艦完全體", layout="wide", page_icon="⚓")

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
        for p in data:
            if "keys_list" not in data[p]: data[p]["keys_list"] = []
            if "local_script_path" not in data[p]: data[p]["local_script_path"] = ""
        return data

PROJECTS = init_system()

# ==========================================
# 2. 側邊欄與頻道切換
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
            PROJECTS[current_p]["keys_list"].append(input_key)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
        st.success("已更新金鑰配置")

    st.divider()
    channel = st.radio("功能頻道", ["📜 AI 自動寫腳本", "📂 專案檔案總管", "📖 智慧答案之書", "🛠️ 管理部署"])

ACTIVE_KEY = st.session_state.session_key if st.session_state.session_key else input_key
st.markdown(f"<style>.main {{ background-color: {config['bg_color']}; color: {config['theme_color']}; }}</style>", unsafe_allow_html=True)

LOG_DIR = os.path.join(BASE_PATH, current_p, "logs")
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

# ==========================================
# 3. 頻道功能實作
# ==========================================

# --- 腳本生成與物理同步 ---
if channel == "📜 AI 自動寫腳本":
    st.title(f"📜 核心代碼生成器 ({AI_MODEL})")
    task_desc = st.text_area("🔧 描述需求", height=150)
    
    if st.button("🪄 生成架構"):
        if not ACTIVE_KEY: st.error("❌ 未鎖定金鑰")
        else:
            with st.spinner("AI 思考中..."):
                genai.configure(api_key=ACTIVE_KEY)
                model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
                res = model.generate_content(f"Godot 4.x。{task_desc}")
                st.session_state.last_ai_res = res.text
                st.markdown(res.text)
                with open(os.path.join(LOG_DIR, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"), "w", encoding="utf-8") as f:
                    f.write(res.text)

# --- 智慧答案之書 ---
elif channel == "📖 智慧答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 擷取啟示"):
        lines = []
        for r, _, fs in os.walk(LOG_DIR):
            for f in fs:
                if f.endswith(".md"):
                    with open(os.path.join(r, f), "r", encoding="utf-8") as file:
                        lines.extend([l.strip() for l in file.readlines() if len(l.strip()) > 15])
        if lines:
            st.info(f"『 {random.choice(lines)} 』")
            st.balloons()

# (檔案總管與管理部署保持之前的邏輯...)
elif channel == "📂 專案檔案總管":
    st.title("📂 實體檔案管理")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        selected = st.selectbox("選取檔案", files)
        if selected:
            f_p = os.path.join(path, selected)
            with open(f_p, "r", encoding="utf-8") as f:
                content = st.text_area("檔案內容", f.read(), height=400)
            if st.button("💾 儲存修改"):
                with open(f_p, "w", encoding="utf-8") as f: f.write(content)
                st.success("已更新實體檔案")

elif channel == "🛠️ 管理部署":
    st.title("🛠️ 配置中心")
    with st.form("settings"):
        p_path = st.text_input("💻 Godot Scripts 資料夾絕對路徑", config.get("local_script_path", ""))
        p_prompt = st.text_area("🤖 AI 公約", config.get("prompt", ""))
        if st.form_submit_button("💾 儲存配置"):
            PROJECTS[current_p].update({"local_script_path": p_path, "prompt": p_prompt})
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
            st.success("設定更新成功")

# ==========================================
# 4. 🔥 物理干涉：字串分割版 (修正紅字)
# ==========================================
if st.session_state.last_ai_res and channel == "📜 AI 自動寫腳本":
    st.divider()
    st.subheader("🚀 物理同步面板")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        existing_gd = [f for f in os.listdir(path) if f.endswith('.gd')]
        target_file = st.selectbox("🎯 目標腳本", ["建立新檔案"] + existing_gd)
        if target_file == "建立新檔案": target_file = st.text_input("新檔名", value="new_script.gd")
        
        if st.button("🔥 執行物理同步"):
            blocks = st.session_state.last_ai_res.split("```")
            if len(blocks) >= 3:
                raw_block = blocks[-2]
                block_lines = raw_block.split("\n")
                final_code = "\n".join(block_lines[1:]).strip() if len(block_lines) > 1 else raw_block.strip()
            else:
                final_code = st.session_state.last_ai_res.strip()
            
            with open(os.path.join(path, target_file), "w", encoding="utf-8") as f:
                f.write(final_code)
            st.success(f"✅ AI 已直接修改硬碟檔案：{target_file}")
            st.balloons()
