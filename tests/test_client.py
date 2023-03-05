"""Tests for translate_md/client.py. """

import pytest
from pathlib import Path
from translate_md import client
import json

filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)


spanglish_client = client.SpanglishClient()


class TestClient:
    def test_repr(self):
        assert repr(spanglish_client).startswith("SpanglishClient(")

    def test_translate(self, mocker):
        mocker.patch(
            "translate_md.client.SpanglishClient._request",
            return_value="texto traducido"
        )
        assert spanglish_client.translate("translated text") == "texto traducido"

    def test_translate(self, mocker):
        mocker.patch(
            "translate_md.client.SpanglishClient._request",
            return_value="texto traducido"
        )
        assert spanglish_client.translate("translated text") == "texto traducido"

    def test_translate_batch(self, mocker):
        mocker.patch(
            "translate_md.client.SpanglishClient._request",
            return_value=json.dumps(["texto uno", "texto dos"])
        )
        assert spanglish_client.translate_batch(["text one", "text two"]) == ["texto uno", "texto dos"]
