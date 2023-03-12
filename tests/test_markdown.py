"""Tests for translate_md/markdown.py. """

import pytest
from pathlib import Path
from translate_md import markdown as md
import tempfile

filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)

mdproc = md.MarkdownProcessor(md.read_file(filename))


def test_read_file():
    content = md.read_file(filename)
    assert isinstance(content, str)


@pytest.fixture
def mdprocessor():
    return md.MarkdownProcessor(md.read_file(filename))


class TestMarkdownProcessor:

    def test_tokens(self):
        toks = mdproc.tokens
        assert isinstance(toks, list)
        assert isinstance(toks[0], md.Token)

    def test_repr(self):
        assert repr(mdproc) == "MarkdownProcessor(72)"

    def test_get_pieces(self):
        assert len(mdproc.get_pieces()) == 16
        assert all([isinstance(p, str) and len(p) > 0 for p in mdproc.get_pieces()])

    def test_update(self, mdprocessor):
        pieces = mdprocessor.get_pieces()
        with pytest.raises(ValueError):
            mdprocessor.update(["wrong length"])
        new_pieces = [""] * len(pieces)
        new_pieces[0] = "texto traducido"
        mdprocessor.update(new_pieces)
        assert mdprocessor.tokens[mdprocessor._positions[0]].content == "texto traducido"
        assert all([mdprocessor._tokens[p].content == "" for p in mdprocessor._positions[1:]])

    def test_render(self, mdprocessor):
        # Update with silly content
        pieces = mdprocessor.get_pieces()
        assert len(mdprocessor._content) == 6250
        # new_pieces = [""] * len(pieces)
        new_pieces = ["hola"] * len(pieces)
        mdprocessor.update(new_pieces)
 
        out = mdprocessor.render()
        assert len(out) == 1615
        assert "hola" in out

    def test_write_to(self, mdprocessor):
        # Update with silly content
        pieces = mdprocessor.get_pieces()
        new_pieces = ["hola"] * len(pieces)
        mdprocessor.update(new_pieces)

        with tempfile.TemporaryDirectory() as tmp:
            mdprocessor.write_to(Path(tmp) / "testfile.md")
            assert (Path(tmp) / "testfile.md").is_file()
            assert len(md.read_file(Path(tmp) / "testfile.md")) == 1615
 

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
