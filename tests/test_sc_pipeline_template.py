"""Tests for SC Pipeline agent template notebook support configuration."""

import inspect
import re
from pathlib import Path

import pytest
import yaml

from pantheon.toolset import parse_tool_desc
from pantheon.toolsets.notebook import IntegratedNotebookToolSet

HERE = Path(__file__).parent
TEMPLATE_PATH = HERE.parent / "pantheon" / "factory" / "templates" / "agents" / "sc_pipeline.md"


@pytest.fixture(scope="module")
def template_text():
    """Read the raw template file."""
    return TEMPLATE_PATH.read_text()


@pytest.fixture(scope="module")
def frontmatter(template_text):
    """Parse YAML frontmatter from the template."""
    match = re.match(r"^---\n(.*?)\n---", template_text, re.DOTALL)
    assert match, "Template must have YAML frontmatter delimited by ---"
    return yaml.safe_load(match.group(1))


@pytest.fixture(scope="module")
def template_body(template_text):
    """Return the body text after the YAML frontmatter."""
    match = re.match(r"^---\n.*?\n---\n(.*)", template_text, re.DOTALL)
    assert match, "Template must have body text after frontmatter"
    return match.group(1)


# ────────────────────────────────────────────────────────────
# 1. Parse the agent template (frontmatter checks)
# ────────────────────────────────────────────────────────────


class TestFrontmatter:
    """Verify YAML frontmatter declares correct notebook configuration."""

    def test_toolsets_includes_notebook(self, frontmatter):
        assert "notebook" in frontmatter["toolsets"], (
            "sc_pipeline toolsets must include 'notebook'"
        )

    def test_include_tools_has_notebook_edit(self, frontmatter):
        notebook_tools = frontmatter["include_tools"]["notebook"]
        assert "notebook_edit" in notebook_tools

    def test_include_tools_has_notebook_execute(self, frontmatter):
        notebook_tools = frontmatter["include_tools"]["notebook"]
        assert "notebook_execute" in notebook_tools

    def test_include_tools_has_notebook_read(self, frontmatter):
        notebook_tools = frontmatter["include_tools"]["notebook"]
        assert "notebook_read" in notebook_tools

    @pytest.mark.parametrize(
        "old_name",
        ["create_notebook", "add_cell", "execute_cell", "read_cells"],
    )
    def test_no_old_tool_names_in_include_tools(self, frontmatter, old_name):
        notebook_tools = frontmatter["include_tools"]["notebook"]
        assert old_name not in notebook_tools, (
            f"Old tool name '{old_name}' must not appear in include_tools.notebook"
        )


# ────────────────────────────────────────────────────────────
# 2. Verify tool filtering on IntegratedNotebookToolSet
# ────────────────────────────────────────────────────────────


class TestToolFiltering:
    """Verify that LLM-facing tools are exactly the unified trio."""

    @pytest.fixture(scope="class")
    def toolset(self):
        return IntegratedNotebookToolSet(name="test_notebook")

    def test_llm_tools_are_unified_trio(self, toolset):
        llm_tool_names = set(toolset.tool_functions.keys())
        expected = {"notebook_edit", "notebook_execute", "notebook_read"}
        assert expected == llm_tool_names, (
            f"LLM-facing tools should be exactly {expected}, got {llm_tool_names}"
        )

    @pytest.mark.parametrize(
        "excluded_name",
        [
            "create_notebook",
            "add_cell",
            "execute_cell",
            "read_cells",
            "update_cell",
            "delete_cell",
            "move_cell",
        ],
    )
    def test_old_tools_excluded_from_llm(self, toolset, excluded_name):
        assert excluded_name not in toolset.tool_functions, (
            f"'{excluded_name}' must be exclude=True (not in tool_functions)"
        )

    @pytest.mark.parametrize(
        "excluded_name",
        [
            "create_notebook",
            "add_cell",
            "execute_cell",
            "read_cells",
        ],
    )
    def test_old_tools_still_exist_in_all_functions(self, toolset, excluded_name):
        assert excluded_name in toolset.functions, (
            f"'{excluded_name}' should still exist in .functions (just excluded from LLM)"
        )


# ────────────────────────────────────────────────────────────
# 3. Verify notebook_edit schema includes language parameter
# ────────────────────────────────────────────────────────────


class TestNotebookEditSchema:
    """Verify the notebook_edit tool schema exposes a language parameter."""

    @pytest.fixture(scope="class")
    def schema(self):
        toolset = IntegratedNotebookToolSet(name="test_notebook")
        # Get the bound method from tool_functions
        method, _kwargs = toolset.tool_functions["notebook_edit"]
        return parse_tool_desc(method)

    def test_language_in_parameters(self, schema):
        param_names = [p["name"] for p in schema["inputs"]]
        assert "language" in param_names, (
            f"'language' must be in notebook_edit inputs, got {param_names}"
        )

    def test_language_is_optional(self, schema):
        lang_param = next(p for p in schema["inputs"] if p["name"] == "language")
        # Required params use sentinel string "not_defined"; optional params have a real default
        assert lang_param["default"] != "not_defined", (
            "'language' parameter must be optional (should have a default, not 'not_defined')"
        )

    def test_language_default_is_none(self):
        sig = inspect.signature(IntegratedNotebookToolSet.notebook_edit)
        lang_param = sig.parameters["language"]
        assert lang_param.default is None, (
            f"'language' default should be None, got {lang_param.default}"
        )


# ────────────────────────────────────────────────────────────
# 4. Verify agent template body content
# ────────────────────────────────────────────────────────────


class TestTemplateBody:
    """Verify the system prompt body references the correct tools and sections."""

    def test_mentions_notebook_edit(self, template_body):
        assert "notebook_edit" in template_body, (
            "Template body must mention 'notebook_edit'"
        )

    def test_does_not_mention_create_notebook_as_tool(self, template_body):
        # The body should not instruct the agent to call create_notebook
        # (it may mention it in passing context, but should not be a tool call instruction)
        assert "create_notebook(" not in template_body, (
            "Template body should not instruct calling 'create_notebook()' directly"
        )

    def test_mentions_language_r(self, template_body):
        assert 'language="r"' in template_body, (
            "Template body must mention language=\"r\" for R notebook creation"
        )

    def test_has_error_handling_rules(self, template_body):
        assert "success" in template_body and "false" in template_body, (
            "Template body must have error checking rules (success/false)"
        )

    def test_has_notebook_playground_section(self, template_body):
        assert "Notebook playground" in template_body, (
            "Template body must have a 'Notebook playground' section"
        )
