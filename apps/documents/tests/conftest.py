import pytest


@pytest.fixture(autouse=True)
def _isolated_media_root(tmp_path, settings):
    """Every test in this package gets its own throwaway MEDIA_ROOT —
    tests write real files to storage, and none of them should touch
    the real media/ directory or leak files between runs."""
    settings.MEDIA_ROOT = tmp_path
