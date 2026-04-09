"""Tests for kernel session creation and R kernel fallback behavior.

Verifies that:
- Python3 kernel sessions can be created and cleaned up
- Missing R kernel (IRkernel not installed) produces a clear error
- Python3 still works after an R kernel failure
- IntegratedNotebookToolSet raises on R notebooks when IRkernel is missing
"""

import json
from pathlib import Path

import nbformat
import pytest

from pantheon.toolsets.notebook.jupyter_kernel import JupyterKernelToolSet


@pytest.fixture
async def kernel_toolset(tmp_path):
    """Create a JupyterKernelToolSet with a temporary working directory."""
    ts = JupyterKernelToolSet(name="test_kernel", workdir=str(tmp_path))
    yield ts
    # Cleanup all sessions after each test
    await ts.cleanup()


async def test_create_session_python3_succeeds(kernel_toolset):
    """create_session('python3') should succeed and return a valid session."""
    result = await kernel_toolset.create_session("python3")

    assert result["success"] is True, f"Expected success but got: {result}"
    assert "session_id" in result
    assert result["kernel_spec"] == "python3"
    assert result["status"] == "idle"

    # Verify session is tracked
    session_id = result["session_id"]
    assert session_id in kernel_toolset.sessions

    # Clean up
    shutdown = await kernel_toolset.shutdown_session(session_id)
    assert shutdown["success"] is True


async def test_create_session_ir_fails_with_clear_error(kernel_toolset):
    """create_session('ir') should fail with an error mentioning the kernel name."""
    result = await kernel_toolset.create_session("ir")

    assert result["success"] is False, "Expected failure for missing R kernel"
    error = result["error"].lower()
    assert "ir" in error, f"Error should mention 'ir' kernel: {result['error']}"
    # The error comes from jupyter_client: "No such kernel named ir"
    assert "kernel" in error, f"Error should mention 'kernel': {result['error']}"

    # Verify no session was created (no silent Python fallback)
    assert len(kernel_toolset.sessions) == 0, (
        "No session should exist after failed ir kernel creation"
    )


async def test_python3_works_after_ir_failure(kernel_toolset):
    """Python3 kernel should still work after a failed ir kernel attempt."""
    # First, fail with ir
    ir_result = await kernel_toolset.create_session("ir")
    assert ir_result["success"] is False

    # Then, succeed with python3
    py_result = await kernel_toolset.create_session("python3")
    assert py_result["success"] is True, f"Python3 should work after ir failure: {py_result}"
    assert py_result["kernel_spec"] == "python3"

    # Clean up
    await kernel_toolset.shutdown_session(py_result["session_id"])


async def test_integrated_notebook_r_kernel_raises(tmp_path):
    """_get_or_create_context should raise when notebook has R kernel and IRkernel is missing."""
    from pantheon.toolsets.notebook.integrated_notebook import IntegratedNotebookToolSet

    # Create a notebook file with R kernel metadata
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "R",
        "language": "R",
        "name": "ir",
    }
    nb.metadata["language_info"] = {
        "name": "R",
    }
    notebook_path = tmp_path / "test_r_notebook.ipynb"
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    # Create the IntegratedNotebookToolSet
    toolset = IntegratedNotebookToolSet(
        name="test_notebook",
        workdir=str(tmp_path),
        streaming_mode="local",  # no NATS needed
    )
    # Run setup for child toolsets (kernel, contents)
    await toolset.kernel_toolset.run_setup()
    await toolset.notebook_contents.run_setup()

    # _get_or_create_context should raise because IR kernel is unavailable
    with pytest.raises(Exception, match="(?i)kernel"):
        await toolset._get_or_create_context(
            notebook_path=str(notebook_path),
            session_id="test-session-r",
        )

    # Verify no kernel sessions were leaked
    assert len(toolset.kernel_toolset.sessions) == 0

    # Cleanup
    await toolset.kernel_toolset.cleanup()
