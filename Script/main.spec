# main.spec - build completa per ILGUERRIERO22/LOL Launcher FIX per Python 3.13 / __file__

import os
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# Invece di usare __file__, usiamo la cartella da cui lanciamo pyinstaller
project_dir = os.getcwd()

# Elenco dei file di dati e configurazione che vogliamo portare nella build
data_files = [
    "API.emv", "cache.json", "channels.json", "hotkeys_config.json",
    "license_key.json", "license_keys.json", "riot_id.json",
    "settings.json", "search_history.json",
    "Client.png", "Fn4oZGDX0AAmn_V.ico",
    "lol_wallet.log", "lol_accept_queue.log",
    "token.pickle", "my_session.session"
]

datas = []
for f in data_files:
    fp = os.path.join(project_dir, f)
    if os.path.exists(fp):
        datas.append((fp, f))

# Includiamo anche TUTTI i .py del progetto (tranne main.py che viene compilato)
for f in os.listdir(project_dir):
    if f.endswith(".py") and f != "main.py":
        datas.append((os.path.join(project_dir, f), f))

# Import dinamici (per sicurezza con roba tipo dotenv, PIL, ecc.)
hiddenimports = collect_submodules('')

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LOL Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(project_dir, "Fn4oZGDX0AAmn_V.ico")
        if os.path.exists(os.path.join(project_dir, "Fn4oZGDX0AAmn_V.ico"))
        else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LOL Launcher'
)
