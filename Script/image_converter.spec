import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

project_dir = os.getcwd()

datas = []
for f in ["Fn4oZGDX0AAmn_V.ico"]:
    fp = os.path.join(project_dir, f)
    if os.path.exists(fp):
        datas.append((fp, f))

a = Analysis(
    ['image_converter.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=["tkinter", "PIL.Image", "PIL.ImageTk"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='image_converter',
    debug=False, upx=True, console=False,
    icon="Fn4oZGDX0AAmn_V.ico" if os.path.exists("Fn4oZGDX0AAmn_V.ico") else None
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='image_converter')
