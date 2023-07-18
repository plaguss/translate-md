"""Tests for translate_md/markdown.py. """

import pytest
from pathlib import Path
from translate_md import markdown as md
import tempfile
import textwrap
from collections import Counter


filename = (
    Path(__file__).parent
    / "data"
    / "a-NER-model-for-command-line-help-messages-part1.en.md"
)

filename_rich = Path(__file__).parent / "data" / "README-rich.md"

mdproc = md.MarkdownProcessor(md.read_file(filename))


def test_read_file():
    content = md.read_file(filename)
    assert isinstance(content, str)


@pytest.fixture
def mdprocessor():
    return md.MarkdownProcessor(md.read_file(filename))


@pytest.mark.skip(reason="old version to be replaced")
class TestMarkdownProcessorOld:
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
        assert (
            mdprocessor.tokens[mdprocessor._positions[0]].content == "texto traducido"
        )
        assert all(
            [mdprocessor._tokens[p].content == "" for p in mdprocessor._positions[1:]]
        )

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
    text = "![helpner](/images/helpner-arch-part1.png)"
    assert md.is_figure(text) is True
    assert md.is_figure(text.replace("!", "-")) is False


def test_is_code():
    text = "```console\n$ pip install helpner\n```"
    assert md.is_code(text) is True
    assert md.is_code(text.replace("`", "-")) is False


def test_is_comment():
    text = "<!-- ### Related posts\nadd here -->"
    assert md.is_comment(text) is True
    assert md.is_comment(text.replace("<!--", "-")) is False


@pytest.mark.parametrize(
    "text, length_links, has_placeholder",
    [
        (
            "[English readme](https://github.com/textualize/rich/blob/master/README.md)",
            1,
            True,
        ),
        (
            "![Logo](https://github.com/textualize/rich/raw/master/imgs/logo.svg)",
            1,
            True,
        ),
        (
            "This is a badge [![Supported Python Versions](https://img.shields.io/pypi/pyversions/rich/13.2.0)](https://pypi.org/project/rich/).",
            1,
            True,
        ),
        (
            "[![Supported Python Versions](https://img.shields.io/pypi/pyversions/rich/13.2.0)](https://pypi.org/project/rich/) [![PyPI version](https://badge.fury.io/py/rich.svg)](https://badge.fury.io/py/rich)",
            2,
            True,
        ),
        (
            "Rich is a Python library for _rich_ text and beautiful formatting in the terminal.",
            0,
            False,
        ),
        (
            "For a video introduction to Rich see [calmcode.io](https://calmcode.io/rich/introduction.html) by [@fishnets88](https://twitter.com/fishnets88).",
            2,
            True,
        ),
    ],
)
def test_grab_mdlinks(text, length_links, has_placeholder):
    text, replaced = md.replace_links(text)
    assert len(replaced) == length_links
    assert (md.PLACEHOLDER_MDLINK in text) is has_placeholder



def test_insert_links():
    t1 = textwrap.dedent(
            """For a video introduction to Rich see [calmcode.io](https://calmcode.io/rich/introduction.html) by [@fishnets88](https://twitter.com/fishnets88)."""
        )
    content, replaced = md.replace_links(t1)
    assert content == f"""For a video introduction to Rich see {md.PLACEHOLDER_MDLINK} by {md.PLACEHOLDER_MDLINK}."""
    text = md.insert_links(content, replaced)
    assert text == t1


class TestPiece:
    @pytest.fixture(scope="class")
    def section_heading(self):
        return "## [Documentation](https://readthedocs.io)"

    def test_piece_badge(self):
        badge = textwrap.dedent(
            """[![Supported Python Versions](https://img.shields.io/pypi/pyversions/rich/13.2.0)](https://pypi.org/project/rich/) [![PyPI version](https://badge.fury.io/py/rich.svg)](https://badge.fury.io/py/rich)        """
        )
        piece = md.Piece(badge, 0)
        assert piece.position == 0
        assert piece._is_processed is False
        piece.process()
        assert piece._is_processed is True
        assert piece.is_header is False
        assert len(piece.sentences) == 1
        assert len(piece.replaced) == 2

    def test_piece_paragraph_with_links(self):
        paragraph_with_links = textwrap.dedent(
            """For a video introduction to Rich see [calmcode.io](https://calmcode.io/rich/introduction.html) by [@fishnets88](https://twitter.com/fishnets88)."""
        )
        piece = md.Piece(paragraph_with_links, 0)
        sentences = piece.process()
        assert len(sentences) == 1
        assert len(piece.replaced) == 2
        ctr = Counter(sentences[0].replace(".", "").split(" "))
        assert ctr[md.PLACEHOLDER_MDLINK] == 2

    def test_long_paragraph(self):
        long_paragraph = textwrap.dedent(
            """Rich works with Linux, OSX, and Windows. True color / emoji works with new Windows Terminal, classic terminal is limited to 16 colors. Rich requires Python 3.7 or later."""
        )
        piece = md.Piece(long_paragraph, 0)
        sentences = piece.process()
        assert len(sentences) == 3
        assert len(piece.replaced) == 0

    def test_section(self):
        section = "## Compatibility"
        piece = md.Piece(section, 0)
        sentences = piece.process()
        assert len(sentences) == 1
        assert piece.is_header is True
        assert piece.headings == "##"
        assert sentences[0] == "Compatibility"
        # Try to build it back after translating the content
        rebuilt = piece.rebuild(["Compatibilidad"])
        assert rebuilt == "## Compatibilidad"

    def test_section_heading(self):
        section_heading = "## [Documentation](https://readthedocs.io)"
        piece = md.Piece(section_heading, 0)
        sentences = piece.process()
        assert len(sentences) == 1
        assert piece.is_header is True
        assert piece.headings == "##"
        assert sentences[0] == md.PLACEHOLDER_MDLINK
        rebuilt = piece.rebuild([md.PLACEHOLDER_MDLINK])
        assert rebuilt == section_heading

    def test_two_sentences_with_link(self):
        two_sentences_with_link = "For more control over rich terminal content. Import and construct a [Console](https://rich.readthedocs.io/en/latest/reference/console.html#rich.console.Console) object."
        piece = md.Piece(two_sentences_with_link, 0)
        sentences = piece.process()
        assert len(sentences) == 2
        assert len(piece.replaced) == 1
        assert md.PLACEHOLDER_MDLINK in sentences[1]
        rebuilt = piece.rebuild(sentences)
        assert rebuilt == two_sentences_with_link

    def test_rebuild_piece_with_header(self):
        section = "## Compatibility"
        piece = md.Piece(section, 0)
        sentences = piece.process()
        assert len(sentences) == 1
        assert piece.is_header is True
        assert piece.headings == "##"
        assert sentences[0] == "Compatibility"
        # Try to build it back after translating the content
        rebuilt = piece.rebuild(["Compatibilidad"])
        assert rebuilt == "## Compatibilidad"

    def test_rebuild_piece_paragraph(self):
        paragraph = "Rich works with Linux, OSX, and Windows. More text here."
        piece = md.Piece(paragraph, 0)
        sentences = piece.process()
        assert len(sentences) == 2
        assert piece.is_header is False
        assert piece.headings == ""
        assert sentences[0] == "Rich works with Linux, OSX, and Windows."
        # Try to build it back after translating the content
        rebuilt = piece.rebuild(["text 1.", "text 2"])
        assert rebuilt == "text 1. text 2"

    def test_rebuild_piece_paragraph_with_links(self):
        paragraph = "to Rich see [calmcode.io](https://calmcode.io/rich/introduction.html)."
        piece = md.Piece(paragraph, 0)
        sentences = piece.process()
        assert len(sentences) == 1
        assert piece.is_header is False
        assert piece.headings == ""
        assert sentences[0] == "to Rich see -MDLINK-."
        # Try to build it back after translating the content
        rebuilt = piece.rebuild(["new text -MDLINK-."])
        assert rebuilt == "new text [calmcode.io](https://calmcode.io/rich/introduction.html)."


parser_name = "zero"

mdproc_rich = md.MarkdownProcessor(md.read_file(filename_rich), parser_name=parser_name)


@pytest.fixture
def mdprocessor_rich() -> md.MarkdownProcessor:
    return md.MarkdownProcessor(md.read_file(filename_rich), parser_name=parser_name)


class TestMarkdownProcessorNew:
    def test_tokens(self):
        toks = mdproc_rich.tokens
        assert isinstance(toks, list)
        assert isinstance(toks[0], md.Token)

    def test_repr(self):
        assert repr(mdproc_rich) == "MarkdownProcessor(459)"

    def test_get_pieces(self):
        pieces = mdproc_rich.get_pieces()
        assert len(pieces) == 119
        assert all([isinstance(p, md.Piece) for p in pieces])
        # assert all([isinstance(p, list) and len(p) > 0 for p in pieces])

    def test_update(self, mdprocessor_rich):
        pieces = mdprocessor_rich.get_pieces()
        # Process every piece
        [p.process() for p in pieces]
        new_pieces = pieces
        new_pieces[0].rebuild(["texto traducido"])

        mdprocessor_rich.update(new_pieces)

        # Simple text on the new content of the corresponding token
        assert mdprocessor_rich._tokens[new_pieces[0].position].content == "texto traducido"

    def test_render(self, mdprocessor_rich):
        # Update with silly content
        pieces = mdprocessor_rich.get_pieces()
        assert len(mdprocessor_rich._content) == 17146
        new_pieces = []
        for p in pieces:
            p.rebuild(["hi"])
            new_pieces.append(p)

        mdprocessor_rich.update(new_pieces)

        out = mdprocessor_rich.render()
        assert len(out) == 2953
        assert "hi" in out

    def test_write_to(self, mdprocessor_rich):
        # Update with silly content
        pieces = mdprocessor_rich.get_pieces()
        new_pieces = []
        for p in pieces:
            p.rebuild(["hi"])
            new_pieces.append(p)

        mdprocessor_rich.update(new_pieces)

        with tempfile.TemporaryDirectory() as tmp:
            mdprocessor_rich.write_to(Path(tmp) / "testfile.md")
            assert (Path(tmp) / "testfile.md").is_file()
            assert len(md.read_file(Path(tmp) / "testfile.md")) == 2953
