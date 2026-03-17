"""PyInstaller hook for fakeredis.

fakeredis/model/_command_info.py loads commands.json via:
    os.path.join(os.path.dirname(__file__), "..", "commands.json")

This resolves to fakeredis/commands.json. PyInstaller collects the .pyc
for model/_command_info but does NOT automatically include the JSON data
file. We collect it here so the relative path works at runtime.
"""
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('fakeredis', includes=['commands.json'])
hiddenimports = ['lupa', 'lupa.lua51']
