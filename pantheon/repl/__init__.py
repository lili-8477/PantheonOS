import os

# Prevent litellm from making blocking network calls to GitHub on startup
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

from .core import Repl

__all__ = ["Repl"]