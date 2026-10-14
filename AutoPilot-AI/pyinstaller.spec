# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['autopilot/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config/default_config.json', 'config'),
        ('config/profiles.json', 'config'),
    ],
    hiddenimports=[
        'autopilot.adapters.cursor',
        'autopilot.adapters.claude_code',
        'autopilot.adapters.antigravity',
        'autopilot.adapters.vscode_copilot',
        'autopilot.gui.pyside_app',
        'autopilot.gui.cli_runner',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoPilot-AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
