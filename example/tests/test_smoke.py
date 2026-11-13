"""Smoke test: every pipeline module imports and has its entry point.

The agent may not run the pipeline scripts (they call a paid API on real data), so this is
its cheapest check that the code it wrote can at least be loaded. No LLM calls, no data.
"""

import importlib

import pytest

MODULES = [
    "llm",
    "paths",
    "prepare",
    "districts",
    "prompts",
    "spam",
    "topics",
    "classify",
    "report",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(f"project.{name}")


@pytest.mark.parametrize("name", ["spam", "topics", "classify", "report"])
def test_step_has_run(name):
    assert callable(importlib.import_module(f"project.{name}").run)
