# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import copy_metadata, collect_data_files

datas = [
    ('pantheon/factory/templates', 'pantheon/factory/templates'),
    ('pantheon/toolsets/database_api/schemas', 'pantheon/toolsets/database_api/schemas'),
    ('pantheon/chatroom/nats-ws.conf', 'pantheon/chatroom'),
    ('pantheon/toolsets/knowledge/config.yaml', 'pantheon/toolsets/knowledge'),
]
datas += copy_metadata('fastmcp')
# litellm needs its JSON data files (model costs, tokenizers, etc.)
datas += collect_data_files('litellm', includes=['**/*.json'])

a = Analysis(
    ['pantheon/chatroom/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'pantheon',
        'pantheon.chatroom',
        'pantheon.endpoint',
        'pantheon.remote',
        'pantheon.toolsets',
        # All toolsets (dynamically imported via importlib)
        'pantheon.toolsets.code',
        'pantheon.toolsets.shell',
        'pantheon.toolsets.python',
        'pantheon.toolsets.file',
        'pantheon.toolsets.file_transfer',
        'pantheon.toolsets.notebook',
        'pantheon.toolsets.image',
        'pantheon.toolsets.database_api',
        'pantheon.toolsets.browser_use',
        'pantheon.toolsets.evolution',
        'pantheon.toolsets.task',
        'pantheon.toolsets.rag',
        'pantheon.toolsets.scfm',
        'nats',
        'litellm',
        'openai',
        'anthropic',
        'fastmcp',
        'fastmcp.server',
        'fastmcp.client',
        'importlib.metadata',
        'importlib_metadata',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ── Knowledge / vector DB (not needed for desktop chatroom) ──
        'lancedb',
        'lance',
        'llama_index',
        'qdrant_client',
        # ── Testing / dev ──
        'pytest',
        'pytest_asyncio',
        # ── Other unused heavy modules ──
        'tkinter',
        '_tkinter',
        'torch',
        'tensorflow',
        'sklearn',
        'cv2',
    ],
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
    name='pantheon-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
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
