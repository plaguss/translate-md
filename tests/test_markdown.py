"""Tests for translate_md/markdown.py. """

import pytest
from pathlib import Path
from translate_md import markdown as md

filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)

mdproc = md.MarkdownProcessor(md.read_file(filename))


def test_read_file():
    content = md.read_file(filename)
    assert isinstance(content, str)


class TestMarkdownProcessor:

    def test_tokens(self):
        toks = mdproc.tokens
        assert isinstance(toks, list)
        assert isinstance(toks[0], md.Token)

    def test_repr(self):
        assert repr(mdproc) == "MarkdownProcessor(72)"

    def test_test(self):
        # print([t.type for t in mdproc.tokens])
        # print(mdproc.tokens[1].content)
        assert 1==2


def test_is_front_matter():
    text = """---\ntitle: "A NER Model for Command Line Help Messages (Part 1: The command line program)"\ndate: 2023-02-21T18:55:27+01:00\ndraft: false\ncategories: ["NLP"]\ntags: ["NLP", "NER", "spaCy", "Python", "rich"]\n---"""
    assert md.is_front_matter(text) is True
    assert md.is_front_matter(text.replace("---", "")) is False


def test_is_figure():
    text = '![helpner](/images/helpner-arch-part1.png)'
    assert md.is_figure(text) is True
    assert md.is_figure(text.replace("!", "-")) is False


def test_is_code():
    text = '```console\n$ pip install helpner\n```'
    assert md.is_code(text) is True
    assert md.is_code(text.replace("`", "-")) is False


def test_is_comment():
    text = '<!-- ### Related posts\nadd here -->'
    assert md.is_comment(text) is True
    assert md.is_comment(text.replace("<!--", "-")) is False
