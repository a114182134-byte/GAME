import streamlit as st
import google.generativeai as genai
from PIL import Image
import os, datetime, json, random

# ==========================================
# 1. 系統核心初始化
# ==========================================
BASE_PATH = "all_projects"
CONFIG_FILE = os.path.join(BASE_PATH, "projects_config.json")

st.set_page_config(page_title="小白龍開發母站 - 旗艦完全體", layout="wide", page_icon="⚓")

# 狀態保持
if "session_key" not in st.session_state: st.session_state.session_key = ""
if "last_ai_res" not in st.session_state: st.session_state.last_ai_res = ""

def init_system():
    if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)
    if not os.path.exists(CONFIG_FILE):
        init = {"餘燼航路": {
            "theme_color": "#D4AF37", 
            "bg_color": "#1A1A1A", 
            "prompt": "你是遊戲架構師，專精 Godot 4.x 與黃銅蒸氣美學。", 
            "local_script_path": "", 
            "keys_list": []
        }}
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
# 2. 側邊欄：中控配置台
# ==========================================
with st.sidebar:
    st.title("⚙️ 核心中控台")
    current_p = st.selectbox("切換開發專案", list(PROJECTS.keys()))
    config = PROJECTS[current_p]
    
    st.divider()
    st.subheader("🤖 AI 模型配置")
    AI_MODEL = st.selectbox("切換 AI 模型", [
        "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"
    ], help="2.5 Pro 擁有最強邏輯，適合複雜腳本修改。")
    
    # 金鑰清單管理
    saved_keys = config.get("keys_list", [])
    sel_key = st.selectbox("選擇已儲存的金鑰", ["手動輸入"] + saved_keys) if saved_keys else "手動輸入"
    input_key = st.text_input("🔑 API Key", value="" if sel_key == "手動輸入" else sel_key, type="password")
    
    c_lock, c_save = st.columns(2)
    with c_lock:
        if st.button("🔐 鎖定當前"):
            st.session_state.session_key = input_key
            st.success("已鎖定")
    with c_save:
        if st.button("💾 存入清單"):
            if input_key and input_key not in saved_keys:
                PROJECTS[current_p]["keys_list"].append(input_key)
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
                st.rerun()

    st.divider()
    channel = st.radio("功能頻道", [
        "💡 跨模態分析", "📜 AI 自動寫腳本", "📂 專案檔案總管", "📖 智慧答案之書", "🛠️ 管理部署"
    ])

# 套用主題色
ACTIVE_KEY = st.session_state.session_key if st.session_state.session_key else input_key
st.markdown(f"<style>.main {{ background-color: {config['bg_color']}; color: {config['theme_color']}; }} .stButton>button {{ border: 1px solid {config['theme_color']}; }}</style>", unsafe_allow_html=True)

# 資料夾準備
LOG_DIR = os.path.join(BASE_PATH, current_p, "logs")
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

# ==========================================
# 3. 頻道功能實作
# ==========================================

# --- 頻道：AI 自動寫腳本 ---
if channel == "📜 AI 自動寫腳本":
    st.title(f"📜 核心代碼生成器 ({AI_MODEL})")
    task_desc = st.text_area("🔧 描述功能需求", height=200, placeholder="例如：修改 harpoon.gd 增加魚叉冷卻時間與重力影響...")
    
    if st.button("🪄 生成架構代碼"):
        if not ACTIVE_KEY: st.error("❌ 請先鎖定金鑰")
        else:
            with st.spinner("AI 正在重構邏輯..."):
                try:
                    genai.configure(api_key=ACTIVE_KEY)
                    model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
                    res = model.generate_content(f"使用 Godot 4.x GDScript。任務：{task_desc}。請務必提供完整的代碼塊。")
                    st.session_state.last_ai_res = res.text
                    st.markdown(res.text)
                    # 儲存日誌
                    with open(os.path.join(LOG_DIR, f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"), "w", encoding="utf-8") as f:
                        f.write(res.text)
                except Exception as e: st.error(f"生成失敗: {e}")

# --- 頻道：跨模態分析 ---
elif channel == "💡 跨模態分析":
    st.title("💡 跨模態分析引擎")
    col1, col2 = st.columns(2)
    with col1:
        txt = st.text_area("✍️ 指令")
        img = st.file_uploader("🖼️ 圖片素材", type=['png', 'jpg', 'jpeg'])
    with col2:
        audio = st.file_uploader("🎵 音訊素材", type=['mp3', 'wav'])
        if audio: st.audio(audio)
    
    if st.button("🚀 啟動分析"):
        if not ACTIVE_KEY: st.error("❌ 未鎖定金鑰")
        else:
            genai.configure(api_key=ACTIVE_KEY)
            model = genai.GenerativeModel(AI_MODEL, system_instruction=config["prompt"])
            payload = [txt] if txt else ["分析此素材"]
            if img: payload.append(Image.open(img))
            if audio: payload.append({"mime_type": audio.type, "data": audio.read()})
            res = model.generate_content(payload)
            st.markdown(res.text)

# --- 頻道：專案檔案總管 ---
elif channel == "📂 專案檔案總管":
    st.title("📂 實體檔案編輯器")
    path = config.get("local_script_path", "")
    if path and os.path.exists(path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        selected = st.selectbox("選取檔案", files)
        if selected:
            f_p = os.path.join(path, selected)
            with open(f_p, "r", encoding="utf-8") as f:
                content = st.text_area(f"檔案內容：{selected}", f.read(), height=400)
            if st.button("💾 儲存修改至硬碟"):
                with open(f_p, "w", encoding="utf-8") as f: f.write(content)
                st.success("檔案已物理更新！")
    else: st.warning("請在『管理部署』設定正確的 Godot 路徑")

# --- 頻道：智慧答案之書 ---
elif channel == "📖 智慧答案之書":
    st.title("📖 答案之書")
    if st.button("🔮 擷取啟示"):
        lines = []
        for r, _, fs in os.walk(LOG_DIR):
            for f in fs:
                if f.endswith(".md"):
                    try:
                        with open(os.path.join(r, f), "r", encoding="utf-8") as file:
                            # 過濾掉太短的行
                            lines.extend([l.strip() for l in file.readlines() if len(l.strip()) > 15])
                    except: continue
        if lines:
            insp = random.choice(lines)
            st.markdown(f"""<div style="padding:30px; border-radius:15px; border:2px solid {config['theme_color']}; background-color:rgba(255,255,255,0.05); text-align:center;"><h2 style="color:{config['theme_color']};">『 {insp} 』</h2></div>""", unsafe_allow_html=True)
            st.balloons()
        else: st.warning("日誌庫目前是空的。")

# --- 頻道：管理部署 ---
elif channel == "🛠️ 管理部署":
    st.title("🛠️ 配置中心")
    with st.expander("🆕 建立新專案"):
        n_name = st.text_input("專案名稱")
        if st.button("初始化"):
            if n_name and n_name not in PROJECTS:
                PROJECTS[n_name] = {"theme_color": "#D4AF37", "bg_color": "#1A1A1A", "prompt": "你是分析師", "local_script_path": "", "keys_list": []}
                os.makedirs(os.path.join(BASE_PATH, n_name, "logs"), exist_ok=True)
                with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
                st.success("專案已建立"); st.rerun()

    st.divider()
    with st.form("settings"):
        p_path = st.text_input("💻 Godot Scripts 資料夾絕對路徑", config.get("local_script_path", ""))
        p_prompt = st.text_area("🤖 AI 公約設定", config.get("prompt", ""))
        p_color = st.color_picker("主題視覺色", config.get("theme_color", "#D4AF37"))
        if st.form_submit_button("💾 儲存並套用"):
            PROJECTS[current_p].update({"local_script_path": p_path, "prompt": p_prompt, "theme_color": p_color})
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(PROJECTS, f, indent=4, ensure_ascii=False)
            st.success("設定更新成功"); st.rerun()

# ==========================================
# 4. 🔥 物理干涉引擎：修正紅字版 (AI 直接修改檔案)
# ==========================================
if st.session_state.last_ai_res and channel == "📜 AI 自動寫腳本":
    st.divider()
    st.subheader("🧬 物理同步面板 (AI 直接修改硬碟檔案)")
    
    path = config.get("local_script_path", "")
    if not path or not os.path.exists(path):
        st.error("❌ 尚未設定 Godot 路徑，無法進行物理修改。")
    else:
        existing_gd = [f for f in os.listdir(path) if f.endswith('.gd')]
        col_f, col_btn = st.columns([2, 1])
        
        with col_f:
            target_file = st.selectbox("🎯 選擇要覆寫的腳本", ["建立新檔案"] + existing_gd)
            if target_file == "建立新檔案":
                target_file = st.text_input("輸入新檔名", value="harpoon.gd")
        
        with col_btn:
            st.write("") # 視覺對齊
            if st.button("🔥 執行物理同步"):
                # --- 核心邏輯：分割法抓取代碼 (徹底避開紅字) ---
                blocks = st.session_state.last_ai_res.split("```")
                final_code = ""
                
                if len(blocks) >= 3:
                    # 抓取最後一個被 ``` 包裹的區塊
                    raw_block = blocks[-2]
                    # 剔除第一行的語言標籤 (例如 gdscript)
                    block_lines = raw_block.split("\n")
                    if len(block_lines) > 1:
                        final_code = "\n".join(block_lines[1:]).strip()
                    else:
                        final_code = raw_block.strip()
                else:
                    final_code = st.session_state.last_ai_res.strip()
                
                full_path = os.path.join(path, target_file)
                try:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(final_code)
                    st.success(f"✅ AI 已成功物理修改檔案：{target_file}")
                    st.balloons()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")
