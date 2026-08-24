"""Domain-specific config-wizard tests for Paperless MCP.

This file is owned by the generated project (kept across ``copier update`` via
``_skip_if_exists``). The template seeds it once with a single skipped
placeholder test; add browser assertions here that depend on *this project's*
``wizard-spec.json`` — e.g. that a specific field renders, that a chosen option
emits the expected env var, or that a guard message appears. The generic
framework tests live in ``test_config_wizard_smoke.py`` (template-owned) and
must not be edited here.

Import the page/browser fixtures from ``test_config_wizard_smoke.py`` (e.g.
``from tests.test_config_wizard_smoke import page, site_url, browser``). This
module is marked ``browser`` so the tests you add run in the docs CI lane, which
invokes ``pytest ... -m browser``.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

pytest_plugins = ("test_config_wizard_smoke",)

pytestmark = pytest.mark.browser


def test_tool_visibility_emits_only_the_selected_list(page: Page) -> None:
    """Switching policy excludes a stale list from generated configuration."""
    page.locator("#cfg-wizard .cfg-advanced summary").click()
    page.select_option('[data-qid="tool_visibility"] select', "allow")
    page.locator("#cfg-wizard .cfg-advanced summary").click()
    page.locator('[data-qid="tools_allow"] input').fill("search_documents")

    page.locator("#cfg-wizard .cfg-advanced summary").click()
    page.select_option('[data-qid="tool_visibility"] select', "deny")
    page.locator("#cfg-wizard .cfg-advanced summary").click()
    page.locator('[data-qid="tools_deny"] input').fill("delete_document")

    output = page.inner_text(".cfg-output")
    assert "PAPERLESS_MCP_TOOLS_DENY=delete_document" in output
    assert "PAPERLESS_MCP_TOOLS_ALLOW=search_documents" not in output
