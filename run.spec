# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [

    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/venv/lib/python3.12/site-packages/streamlit/runtime", "./streamlit/runtime"), 
    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/streamlit_app.py", "."),
    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/matching.py", "."), 
    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/plots.py", "."),
    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/Sopht_logo.png", "./assets"),
    ("/Users/nathaliecrevoisier/Documents/Sopht/Matching/MatchingDashboard/streamlit_dash/.streamlit", "."),

    ]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")


block_cipher = None


a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=['seaborn'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
