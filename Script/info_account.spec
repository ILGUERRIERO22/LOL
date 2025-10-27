import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

project_dir = os.getcwd()

datas = []
for f in [
    "API.emv",
    "riot_id.json",
    "settings.json",
    "Fn4oZGDX0AAmn_V.ico"
]:
    fp = os.path.join(project_dir, f)
    if os.path.exists(fp):
        datas.append((fp, f))

a = Analysis(
    ['info account.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "requests",
        "tkinter",
        "urllib3",
        "PIL.Image",
        "PIL.ImageTk"
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Info Account',
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
    name='Info Account'
)
