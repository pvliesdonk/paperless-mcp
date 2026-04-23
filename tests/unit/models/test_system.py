from __future__ import annotations

from paperless_mcp.models.system import RemoteVersion, Statistics


def test_statistics_roundtrip(load_fixture) -> None:
    stats = Statistics.model_validate(load_fixture("statistics.json"))
    assert stats.documents_total == 1234
    assert stats.tag_count == 47


def test_remote_version_roundtrip(load_fixture) -> None:
    rv = RemoteVersion.model_validate(load_fixture("remote_version.json"))
    assert rv.version == "2.7.2"
    assert rv.update_available is False
