"""The generated config wizard keeps Paperless credentials out of URLs."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WIZARD_SPEC = REPO_ROOT / "docs" / "javascripts" / "config-wizard" / "wizard-spec.json"


def test_generated_wizard_requires_paperless_connection_and_marks_token_secret() -> (
    None
):
    """The shareable wizard config keeps Paperless credentials out of URLs."""
    spec = json.loads(WIZARD_SPEC.read_text(encoding="utf-8"))
    questions = {question["id"]: question for question in spec["questions"]}

    assert questions["paperless_url"]["var"] == "PAPERLESS_MCP_PAPERLESS_URL"
    assert questions["api_token"]["var"] == "PAPERLESS_MCP_API_TOKEN"
    assert "PAPERLESS_MCP_API_TOKEN" in spec["secretKeys"]
