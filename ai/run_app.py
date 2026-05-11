import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

if __name__ == "__main__":
    # 這裡填寫你原本母站的主程式檔名
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("master_hub.py"), # 確保檔名正確
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())