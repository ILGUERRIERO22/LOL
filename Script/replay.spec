import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

project_dir = os.getcwd()

datas = []
for f in [
    "API.emv",
    "riot_id.json",
    "token.pickle",
    "Fn4oZGDX0AAmn_V.ico"
]:
    fp = os.path.join(project_dir, f)
    if os.path.exists(fp):
        datas.append((fp, f))

a = Analysis(
    ['replay.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PIL.Image",
        "PIL.ImageTk",
        "googleapiclient.discovery",
        "googleapiclient.http",
        "google_auth_oauthlib.flow",
        "google.auth.transport.requests",
        "dotenv"
    ],
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
    name='Replay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="Fn4oZGDX0AAmn_V.ico" if os.path.exists("Fn4oZGDX0AAmn_V.ico") else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Replay'
)
