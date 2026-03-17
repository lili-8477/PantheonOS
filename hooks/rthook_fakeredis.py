"""Runtime hook: ensure fakeredis can find commands.json.

fakeredis/model/_command_info.py loads commands.json via a relative path:
    os.path.join(os.path.dirname(__file__), "..", "commands.json")

In PyInstaller onefile mode, __file__ for bytecode inside PYZ may not
resolve to the real filesystem. This hook creates the expected directory
structure in the extraction directory so the relative path works.
"""
import os
import sys
import shutil

# PyInstaller sets _MEIPASS to the temp extraction directory
meipass = getattr(sys, '_MEIPASS', None)
if meipass:
    src = os.path.join(meipass, 'fakeredis', 'commands.json')
    model_dir = os.path.join(meipass, 'fakeredis', 'model')
    dst = os.path.join(model_dir, '..', 'commands.json')
    # Ensure model/ directory exists so __file__ based paths resolve
    if os.path.exists(src) and not os.path.isdir(model_dir):
        os.makedirs(model_dir, exist_ok=True)
