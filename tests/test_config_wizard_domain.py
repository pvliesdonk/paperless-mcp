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

from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page

# Reuse the complete project fixture chain, under private Python names, so it
# overrides pytest-playwright's built-in blank-page fixture in docs CI.
from test_config_wizard_smoke import browser as _smoke_browser
from test_config_wizard_smoke import page as _smoke_page
from test_config_wizard_smoke import site_url as _smoke_site_url

pytestmark = pytest.mark.browser


@pytest.fixture(scope="module")
def domain_site_url() -> Iterator[str]:
    """Serve the built documentation through the smoke-test fixture."""
    yield from _smoke_site_url.__wrapped__()  # type: ignore[attr-defined]


@pytest.fixture(scope="module")
def domain_browser(domain_site_url: str) -> Iterator[Browser]:
    """Launch the smoke-test browser against the domain test server."""
    yield from _smoke_browser.__wrapped__(domain_site_url)  # type: ignore[attr-defined]


@pytest.fixture
def page(domain_browser: Browser, domain_site_url: str) -> Iterator[Page]:
    """Open a fresh domain-test page at the configuration wizard."""
    yield from _smoke_page.__wrapped__(  # type: ignore[attr-defined]
        domain_browser, domain_site_url
    )


def test_paperless_settings_emit_config_without_sharing_api_token(page: Page) -> None:
    """Paperless settings produce startup config while hiding its token from URLs."""
    page.locator('[data-qid="paperless_url"] input').fill("http://paperless.test")
    page.locator('[data-qid="api_token"] input').fill("secret-token")

    page.wait_for_function("location.hash.includes('paperless_url=')")
    output = page.inner_text(".cfg-output")
    assert "PAPERLESS_MCP_PAPERLESS_URL=http://paperless.test" in output
    assert "PAPERLESS_MCP_API_TOKEN=secret-token" in output
    assert "api_token" not in page.url


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
