"""Notebook toolsets for Jupyter integration"""

from .notebook_contents import NotebookContentsToolSet
from .integrated_notebook import IntegratedNotebookToolSet
from .jupyter_kernel import JupyterKernelToolSet
from .jedi_integration import EnhancedCompletionService
from .language_detection import (
    detect_notebook_language,
    get_kernel_spec,
    get_language_info,
    kernel_name_for_language,
    normalize_language_name,
)

NotebookToolSet = IntegratedNotebookToolSet

__all__ = [
    "NotebookContentsToolSet",
    "IntegratedNotebookToolSet",
    "NotebookToolSet",
    "JupyterKernelToolSet",
    "EnhancedCompletionService",
    "detect_notebook_language",
    "get_kernel_spec",
    "get_language_info",
    "kernel_name_for_language",
    "normalize_language_name",
]
