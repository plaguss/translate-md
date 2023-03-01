"""Tests for translate_md/markdown.py. """

import pytest
from pathlib import Path
from translate_md import markdown as md

filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)


def test_read_file():
    content = md.read_file(filename)
    assert isinstance(content, str)


class TestMarkdownProcessor:
    def test_tokens():
        pass
