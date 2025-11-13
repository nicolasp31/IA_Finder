# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['IA_Finder.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('exiftool/exiftool.exe', 'exiftool'),
        ('exiftool/exiftool_files', 'exiftool/exiftool_files'),
        ('Gui.py', '.'),
        ('config.py', '.'),
        ('metadata_analisis.py', '.'),
        ('pantalla_carga.py', '.'),
        ('exiftool.ico', '.'),
        ('Manual_Usuario.pdf', '.'),
        ('Worker.py', '.'),
    ],
    hiddenimports=[
        'Gui', 'config', 'metadata_analisis', 'pantalla_carga', 'Worker',
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
        'platform', 'json', 'subprocess', 'os', 'sys', 
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='Detector de IA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Detector de IA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True, 
    icon="exiftool.ico", 
)
