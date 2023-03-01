"""Tests for translate_md/client.py. """

import pytest
from pathlib import Path
from translate_md import client

filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)


@pytest.fixture
def spanglish_client():
    return client.SpanglishClient()


class TestClient:
    def test_repr(self, spanglish_client):
        assert repr(spanglish_client).startswith("SpanglishClient(")
