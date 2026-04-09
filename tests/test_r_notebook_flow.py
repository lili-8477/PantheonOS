"""
Tests for notebook creation flow with R language support.

Exercises:
1. Language detection module (get_kernel_spec, get_language_info, etc.)
2. NotebookContentsToolSet.create_notebook with language="r"
3. NotebookContentsToolSet.create_notebook with language=None (default to python)
4. JupyterKernelToolSet.create_session("ir") failure handling
5. IntegratedNotebookToolSet.notebook_edit language parameter
"""

import inspect
import json

import pytest

from pantheon.toolsets.notebook.language_detection import (
    KERNEL_NAME_TO_LANGUAGE,
    KERNEL_SPECS,
    detect_notebook_language,
    get_kernel_spec,
    get_language_info,
    kernel_name_for_language,
    language_from_kernel_name,
    normalize_language_name,
)
from pantheon.toolsets.notebook.notebook_contents import NotebookContentsToolSet
from pantheon.toolsets.notebook.jupyter_kernel import JupyterKernelToolSet
from pantheon.toolsets.notebook.integrated_notebook import IntegratedNotebookToolSet


# ═══════════════════════════════════════════════════════════════════
# 1. Language detection module
# ═══════════════════════════════════════════════════════════════════


class TestLanguageDetection:
    """Tests for the language_detection module helpers."""

    def test_get_kernel_spec_r(self):
        """get_kernel_spec('r') returns correct R kernel spec with name='ir'."""
        spec = get_kernel_spec("r")
        assert spec["name"] == "ir"
        assert spec["language"] == "R"
        assert spec["display_name"] == "R"

    def test_get_kernel_spec_python(self):
        """get_kernel_spec('python') returns correct Python spec with name='python3'."""
        spec = get_kernel_spec("python")
        assert spec["name"] == "python3"
        assert spec["language"] == "python"
        assert spec["display_name"] == "Python 3"

    def test_get_kernel_spec_returns_copy(self):
        """get_kernel_spec returns a copy, not the original dict."""
        spec1 = get_kernel_spec("r")
        spec2 = get_kernel_spec("r")
        assert spec1 is not spec2
        assert spec1 == spec2

    def test_get_language_info_r(self):
        """get_language_info('r') returns R language info."""
        info = get_language_info("r")
        assert info["name"] == "R"
        assert info["mimetype"] == "text/x-r-source"
        assert info["file_extension"] == ".r"

    def test_get_language_info_python(self):
        """get_language_info('python') returns Python language info."""
        info = get_language_info("python")
        assert info["name"] == "python"
        assert info["mimetype"] == "text/x-python"
        assert info["file_extension"] == ".py"

    def test_kernel_name_for_language_r(self):
        """kernel_name_for_language('r') returns 'ir'."""
        assert kernel_name_for_language("r") == "ir"

    def test_kernel_name_for_language_python(self):
        """kernel_name_for_language('python') returns 'python3'."""
        assert kernel_name_for_language("python") == "python3"

    def test_language_from_kernel_name_ir(self):
        """language_from_kernel_name('ir') returns 'r'."""
        assert language_from_kernel_name("ir") == "r"

    def test_language_from_kernel_name_python3(self):
        """language_from_kernel_name('python3') returns 'python'."""
        assert language_from_kernel_name("python3") == "python"

    def test_language_from_kernel_name_python(self):
        """language_from_kernel_name('python') returns 'python'."""
        assert language_from_kernel_name("python") == "python"

    def test_language_from_kernel_name_unknown_defaults_to_python(self):
        """Unknown kernel names default to 'python'."""
        assert language_from_kernel_name("unknown_kernel") == "python"

    def test_normalize_language_name_r_variants(self):
        """R-like identifiers normalize to lowercase 'r'."""
        assert normalize_language_name("R") == "r"
        assert normalize_language_name("r") == "r"
        assert normalize_language_name("ir") == "r"

    def test_detect_notebook_language_prefers_metadata(self):
        """Notebook language detection normalizes common metadata variants."""
        assert detect_notebook_language({"language": "R"}) == "r"
        assert detect_notebook_language({"language_info": {"name": "R"}}) == "r"
        assert detect_notebook_language({"kernelspec": {"name": "ir"}}) == "r"
        assert detect_notebook_language({"kernelspec": {"language": "python"}}) == "python"

    def test_kernel_specs_dict_structure(self):
        """KERNEL_SPECS has entries for both python and r."""
        assert "python" in KERNEL_SPECS
        assert "r" in KERNEL_SPECS
        for lang in ("python", "r"):
            assert "kernelspec" in KERNEL_SPECS[lang]
            assert "language_info" in KERNEL_SPECS[lang]

    def test_kernel_name_to_language_mapping(self):
        """KERNEL_NAME_TO_LANGUAGE maps ir->r, python3->python, python->python."""
        assert KERNEL_NAME_TO_LANGUAGE["ir"] == "r"
        assert KERNEL_NAME_TO_LANGUAGE["python3"] == "python"
        assert KERNEL_NAME_TO_LANGUAGE["python"] == "python"


# ═══════════════════════════════════════════════════════════════════
# 2. NotebookContentsToolSet.create_notebook with language="r"
# ═══════════════════════════════════════════════════════════════════


class TestCreateNotebookWithLanguage:
    """Tests for create_notebook with language parameter."""

    @pytest.fixture
    def contents_toolset(self, tmp_path):
        """Create a NotebookContentsToolSet rooted at tmp_path."""
        return NotebookContentsToolSet(name="test_contents", workdir=str(tmp_path))

    async def test_create_notebook_r_kernelspec(self, contents_toolset, tmp_path):
        """create_notebook(language='r') sets kernelspec.name == 'ir'."""
        nb_path = str(tmp_path / "test_r.ipynb")
        result = await contents_toolset.create_notebook(nb_path, title="Test", language="r")
        assert result["success"], f"create_notebook failed: {result}"

        # Read back and verify kernel spec
        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        ks = nb_data["metadata"]["kernelspec"]
        assert ks["name"] == "ir"
        assert ks["language"] == "R"
        assert ks["display_name"] == "R"

    async def test_create_notebook_r_language_info(self, contents_toolset, tmp_path):
        """create_notebook(language='r') sets language_info.name == 'R'."""
        nb_path = str(tmp_path / "test_r_info.ipynb")
        result = await contents_toolset.create_notebook(nb_path, title="Test", language="r")
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        li = nb_data["metadata"]["language_info"]
        assert li["name"] == "R"
        assert li["mimetype"] == "text/x-r-source"
        assert li["file_extension"] == ".r"

    async def test_create_notebook_python_kernelspec(self, contents_toolset, tmp_path):
        """create_notebook(language='python') sets kernelspec.name == 'python3'."""
        nb_path = str(tmp_path / "test_py.ipynb")
        result = await contents_toolset.create_notebook(nb_path, title="Test", language="python")
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        ks = nb_data["metadata"]["kernelspec"]
        assert ks["name"] == "python3"
        assert ks["language"] == "python"

    async def test_create_notebook_python_language_info(self, contents_toolset, tmp_path):
        """create_notebook(language='python') sets language_info.name == 'python'."""
        nb_path = str(tmp_path / "test_py_info.ipynb")
        result = await contents_toolset.create_notebook(
            nb_path, title="Test", language="python"
        )
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        li = nb_data["metadata"]["language_info"]
        assert li["name"] == "python"
        assert li["mimetype"] == "text/x-python"

    async def test_create_notebook_nbformat_version(self, contents_toolset, tmp_path):
        """Created notebooks use nbformat 4.5 for stable cell ids."""
        nb_path = str(tmp_path / "test_ver.ipynb")
        result = await contents_toolset.create_notebook(nb_path, language="r")
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        assert nb_data["nbformat"] == 4
        assert nb_data["nbformat_minor"] == 5

    async def test_create_notebook_empty_cells(self, contents_toolset, tmp_path):
        """Created notebook starts with empty cells array."""
        nb_path = str(tmp_path / "test_empty.ipynb")
        result = await contents_toolset.create_notebook(nb_path, language="r")
        assert result["success"]
        assert result["cell_count"] == 0

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        assert nb_data["cells"] == []

    async def test_update_notebook_kernel_switches_metadata_to_r(
        self, contents_toolset, tmp_path
    ):
        """update_notebook_kernel should persist R kernelspec and language metadata."""
        nb_path = str(tmp_path / "switch_to_r.ipynb")
        create_result = await contents_toolset.create_notebook(nb_path, language="python")
        assert create_result["success"]

        switch_result = await contents_toolset.update_notebook_kernel(nb_path, language="r")
        assert switch_result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        assert nb_data["metadata"]["kernelspec"]["name"] == "ir"
        assert nb_data["metadata"]["language_info"]["name"] == "R"
        assert nb_data["metadata"]["language"] == "r"


# ═══════════════════════════════════════════════════════════════════
# 3. NotebookContentsToolSet.create_notebook with language=None
# ═══════════════════════════════════════════════════════════════════


class TestCreateNotebookDefaultLanguage:
    """Tests that create_notebook defaults to Python when no language is given."""

    @pytest.fixture
    def contents_toolset(self, tmp_path):
        return NotebookContentsToolSet(name="test_defaults", workdir=str(tmp_path))

    async def test_default_language_is_python(self, contents_toolset, tmp_path):
        """create_notebook with no language defaults to Python kernel spec."""
        nb_path = str(tmp_path / "test_default.ipynb")
        result = await contents_toolset.create_notebook(nb_path, title="Default")
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        ks = nb_data["metadata"]["kernelspec"]
        assert ks["name"] == "python3"
        assert ks["language"] == "python"

        li = nb_data["metadata"]["language_info"]
        assert li["name"] == "python"

    async def test_language_none_is_python(self, contents_toolset, tmp_path):
        """create_notebook(language=None) defaults to Python kernel spec."""
        nb_path = str(tmp_path / "test_none.ipynb")
        result = await contents_toolset.create_notebook(nb_path, title="None", language=None)
        assert result["success"]

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        ks = nb_data["metadata"]["kernelspec"]
        assert ks["name"] == "python3"
        assert ks["language"] == "python"


# ═══════════════════════════════════════════════════════════════════
# 4. JupyterKernelToolSet.create_session("ir") failure handling
# ═══════════════════════════════════════════════════════════════════


class TestKernelSessionCreation:
    """Tests for create_session with unavailable kernels."""

    @pytest.fixture
    def kernel_toolset(self, tmp_path):
        return JupyterKernelToolSet(name="test_kernel", workdir=str(tmp_path))

    async def test_create_session_ir_fails_gracefully(self, kernel_toolset):
        """create_session('ir') returns success=False when IRkernel is not installed."""
        result = await kernel_toolset.create_session("ir")
        assert result["success"] is False
        assert "error" in result
        assert "ir" in result["error"].lower() or "not available" in result["error"].lower()

    async def test_create_session_ir_does_not_fallback_to_python(self, kernel_toolset):
        """create_session('ir') must NOT silently fall back to python3."""
        result = await kernel_toolset.create_session("ir")
        # If it fell back to Python silently, success would be True
        assert result["success"] is False
        # No session should have been created
        assert len(kernel_toolset.sessions) == 0

    async def test_create_session_ir_error_message_is_informative(self, kernel_toolset):
        """Error message should mention the kernel name that was not found."""
        result = await kernel_toolset.create_session("ir")
        assert result["success"] is False
        # The error should clearly indicate which kernel was not found
        error_lower = result["error"].lower()
        assert "ir" in error_lower, f"Error should mention 'ir' kernel: {result['error']}"
        assert "kernel" in error_lower, f"Error should mention 'kernel': {result['error']}"

    async def test_create_session_python3_works(self, kernel_toolset):
        """create_session('python3') should still work fine."""
        result = await kernel_toolset.create_session("python3")
        assert result["success"] is True
        assert result["kernel_spec"] == "python3"
        assert "session_id" in result

        # Clean up the kernel
        session_id = result["session_id"]
        if session_id in kernel_toolset.kernel_managers:
            km = kernel_toolset.kernel_managers[session_id]
            await km.shutdown_kernel(now=True)

    async def test_create_session_default_is_python3(self, kernel_toolset):
        """create_session() with default args starts a python3 kernel."""
        result = await kernel_toolset.create_session()
        assert result["success"] is True
        assert result["kernel_spec"] == "python3"

        # Clean up the kernel
        session_id = result["session_id"]
        if session_id in kernel_toolset.kernel_managers:
            km = kernel_toolset.kernel_managers[session_id]
            await km.shutdown_kernel(now=True)


# ═══════════════════════════════════════════════════════════════════
# 5. IntegratedNotebookToolSet.notebook_edit language parameter
# ═══════════════════════════════════════════════════════════════════


class TestNotebookEditLanguageParameter:
    """Tests that notebook_edit exposes the language parameter."""

    def test_notebook_edit_has_language_parameter(self):
        """notebook_edit's function signature includes 'language' parameter."""
        sig = inspect.signature(IntegratedNotebookToolSet.notebook_edit)
        params = list(sig.parameters.keys())
        assert "language" in params, (
            f"'language' not in notebook_edit params: {params}"
        )

    def test_language_parameter_is_optional(self):
        """The language parameter should be Optional with default None."""
        sig = inspect.signature(IntegratedNotebookToolSet.notebook_edit)
        lang_param = sig.parameters["language"]
        assert lang_param.default is None

    def test_notebook_edit_in_tool_functions(self, tmp_path):
        """notebook_edit should be present in tool_functions (LLM-facing tools)."""
        toolset = IntegratedNotebookToolSet(
            name="test_edit_check",
            workdir=str(tmp_path),
            streaming_mode="local",
        )
        tool_funcs = toolset.tool_functions
        assert "notebook_edit" in tool_funcs, (
            f"'notebook_edit' not found in tool_functions. "
            f"Available: {list(tool_funcs.keys())}"
        )

    def test_notebook_edit_tool_schema_has_language(self, tmp_path):
        """The LLM-facing tool schema for notebook_edit should expose language."""
        toolset = IntegratedNotebookToolSet(
            name="test_schema_check",
            workdir=str(tmp_path),
            streaming_mode="local",
        )
        tool_funcs = toolset.tool_functions
        assert "notebook_edit" in tool_funcs

        method, kwargs = tool_funcs["notebook_edit"]
        sig = inspect.signature(method)
        assert "language" in sig.parameters


class TestNotebookReadLanguageNormalization:
    """Tests notebook read APIs used by the frontend render path."""

    @pytest.fixture
    def contents_toolset(self, tmp_path):
        return NotebookContentsToolSet(name="test_read_contents", workdir=str(tmp_path))

    @pytest.fixture
    def integrated_toolset(self, tmp_path):
        return IntegratedNotebookToolSet(
            name="test_read_integrated",
            workdir=str(tmp_path),
            streaming_mode="local",
        )

    async def test_read_notebook_sets_cell_metadata_language_to_r(
        self, contents_toolset, tmp_path
    ):
        """read_notebook should normalize R metadata for frontend cell editors."""
        nb_path = str(tmp_path / "analysis.ipynb")
        result = await contents_toolset.create_notebook(nb_path, language="r")
        assert result["success"]

        add_result = await contents_toolset.add_cell(nb_path, "code", "x <- 1")
        assert add_result["success"]

        read_result = await contents_toolset.read_notebook(nb_path)
        assert read_result["success"]
        code_cell = read_result["notebook"]["cells"][0]
        assert code_cell["metadata"]["language"] == "r"
        assert code_cell["source"] == "x <- 1"

    async def test_read_cells_reports_lowercase_r_language(
        self, integrated_toolset, tmp_path
    ):
        """read_cells should emit lowercase language ids for the frontend."""
        nb_path = str(tmp_path / "analysis.ipynb")
        create_result = await integrated_toolset.notebook_contents.create_notebook(
            nb_path, language="r"
        )
        assert create_result["success"]

        add_result = await integrated_toolset.notebook_contents.add_cell(
            nb_path, "code", "x <- 1"
        )
        assert add_result["success"]

        read_result = await integrated_toolset.read_cells(nb_path, include_details=True)
        assert read_result["success"]
        assert len(read_result["cells"]) == 1
        assert read_result["cells"][0]["language"] == "r"
        assert read_result["cells"][0]["source"] == "x <- 1"


class TestManageKernelSwitch:
    """Tests kernel switching without requiring a live kernel process."""

    @pytest.fixture
    def integrated_toolset(self, tmp_path):
        return IntegratedNotebookToolSet(
            name="test_switch_integrated",
            workdir=str(tmp_path),
            streaming_mode="local",
        )

    async def test_manage_kernel_switch_updates_context_and_metadata(
        self, integrated_toolset, tmp_path
    ):
        nb_path = str(tmp_path / "analysis.ipynb")
        create_result = await integrated_toolset.notebook_contents.create_notebook(
            nb_path, language="python"
        )
        assert create_result["success"]

        session_id = "test-session"
        kernel_session_id = "kernel-1"
        context = integrated_toolset._get_context(nb_path, session_id)
        if context is None:
            from pantheon.toolsets.notebook.integrated_notebook import NotebookContext

            context = NotebookContext(
                notebook_path=nb_path,
                session_id=session_id,
                kernel_session_id=kernel_session_id,
                created_at="now",
                notebook_title="analysis.ipynb",
                kernel_spec="python3",
                notebook_is_new=False,
            )
            integrated_toolset.notebook_contexts[(nb_path, session_id)] = context

        class _DummySession:
            def __init__(self, status: str):
                self.status = type("Status", (), {"value": status})()

        async def _shutdown(session_id_arg):
            integrated_toolset.kernel_toolset.sessions.pop(session_id_arg, None)
            return {"success": True}

        async def _create(kernel_spec_arg, kernel_session_id=None):
            integrated_toolset.kernel_toolset.sessions[kernel_session_id] = _DummySession(
                "idle"
            )
            return {
                "success": True,
                "session_id": kernel_session_id,
                "kernel_spec": kernel_spec_arg,
                "status": "idle",
            }

        integrated_toolset.kernel_toolset.sessions[kernel_session_id] = _DummySession(
            "idle"
        )
        integrated_toolset.kernel_toolset.shutdown_session = _shutdown
        integrated_toolset.kernel_toolset.create_session = _create
        integrated_toolset.get_session_id = lambda: session_id

        result = await integrated_toolset.manage_kernel(
            nb_path, action="switch", kernel_spec="ir"
        )
        assert result["success"]
        assert result["kernel_spec"] == "ir"
        assert integrated_toolset.notebook_contexts[(nb_path, session_id)].kernel_spec == "ir"

        with open(nb_path, "r") as f:
            nb_data = json.load(f)

        assert nb_data["metadata"]["kernelspec"]["name"] == "ir"
        assert nb_data["metadata"]["language"] == "r"
