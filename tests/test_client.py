"""Tests for translate_md/client.py. """

import tempfile
from pathlib import Path
from translate_md import client
import json
import pytest

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


    def test_translate_batch_error(self, mocker):
        mocker.patch(
            "translate_md.client.SpanglishClient._request",
            return_value="['one text', 'one err'"
        )
        with pytest.raises(ValueError):
            assert spanglish_client.translate_batch(["text one", "text two"]) == ["texto uno", "texto dos"]


    def test_translate_file(self, mocker):
        translation = ["hola"] * 16  # The number of pieces the file contains once processed
        mocker.patch(
            "translate_md.client.SpanglishClient._multi_request",
            return_value=translation
        )
        with tempfile.TemporaryDirectory() as tmp:
            spanglish_client.translate_file(filename)
            assert (filename.parent / f"{filename.stem}.es{filename.suffix}").is_file()
            (filename.parent / f"{filename.stem}.es{filename.suffix}").unlink()
            spanglish_client.translate_file(filename, new_filename=Path(tmp) / "testfile.md")
            assert (Path(tmp) / "testfile.md").is_file()
