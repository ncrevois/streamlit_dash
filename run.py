import streamlit
import streamlit.web.cli as stcli
import os
import sys

if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    print("sys.executable:", sys.executable)
    print("__file__:", __file__)
    
    if getattr(sys, 'frozen', False):
        print("Running as frozen application")
        bundle_dir = sys._MEIPASS
    else:
        print("Running in normal Python environment")
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Bundle directory:", bundle_dir)
    
    streamlit_app_path = os.path.join(bundle_dir, 'streamlit_app.py')
    print("Streamlit app path:", streamlit_app_path)
    print("Does streamlit_app.py exist?", os.path.exists(streamlit_app_path))
    
    print("Contents of bundle directory:")
    for item in os.listdir(bundle_dir):
        print(item)
    
    sys.argv = [
        "streamlit",
        "run",
        streamlit_app_path,
        "--global.developmentMode=false",
        "--theme.backgroundColor=#2C2C2C",
        "--theme.primaryColor=#d7ffcd",
        "--theme.secondaryBackgroundColor=#373737",
        "--theme.textColor=#E8E8E8",
        "--theme.font=\'sans serif\'"
    ]

    print("sys.argv:", sys.argv)
    
    sys.exit(stcli.main())