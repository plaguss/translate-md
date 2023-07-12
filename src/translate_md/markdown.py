"""Markdown related facilities. """

import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping, MutableMapping

import nltk
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

md = MarkdownIt("zero")


ParserName = Literal["zero", "commonmark", "js-default", "gfm-like"]


def read_file(filename: Path) -> str:
    """Read a whole markdown file to a string, just a helper function."""
    with open(filename, "r") as f:
        return f.read()


class MarkdownProcessor:
    """Class that allows to work with a markdown file, extracting
    the text content to be translated.

    The expected format of the markdown file is the one used in hugo
    for blogging.

    Args:
        markdown_content (str):
            The content of a markdown file as a string.

    Notes:
        See [gohugo](https://gohugo.io/) for type of markdown files
    """

    def __init__(self, markdown_content: str, parser_name: ParserName = "zero") -> None:
        self.md = MarkdownIt(parser_name)
        self._tokens: list[Token] = []
        self._positions: list[int] = []
        self._content = markdown_content
        # Stores the links that may be captured when extracting the
        # pieces of the markdown.
        # List of paragraphs, containing a list of sentences, with maybe
        # a list of links.
        self._replaced: list[list[list[str]]] = []

    @property
    def tokens(self) -> list[Token]:
        """Parsed pieces of the markdown file.
        The content will be extracted from these pieces, updated and
        created back.
        """
        if len(self._tokens) == 0:
            self._tokens = self.md.parse(self._content)
        return self._tokens

    def __repr__(self) -> str:
        return type(self).__name__ + f"({len(self.tokens)})"

    # def get_pieces(self) -> list[list[str]]:
    def get_pieces(self) -> list[str]:
        """Gets the pieces of the markdown file to be translated.

        The relevant pieces are those tokens considered of type
        'inline' and which aren't the front matter, a figure, code
        or markdown comments.

        Internally stores the position of the corresponding tokens
        for later use.
        """
        pieces = []
        for i, t in enumerate(self.tokens):
            if t.type == "inline":
                if any(
                    (
                        is_front_matter(t.content),
                        is_figure(t.content),
                        is_code(t.content),
                        is_comment(t.content),
                    )
                ):
                    continue
                # TODO: Check for markup in the tokens.
                # If contains at least one #, store the content and
                # the markup to recreate the section name.
                if t.content.startswith("#"):
                    # TODO: Parse the sections as independent elements
                    print((i, t.content))

                # Split the paragraphs on phrases
                sentences_ = nltk.sent_tokenize(t.content)
                sentences = []
                replaced_per_paragraph = []
                for sentence in sentences_:
                    (sentence, replaced) = replace_links(sentence)
                    replaced_per_paragraph.append(replaced)
                    sentences.append(sentence)

                self._replaced.append(replaced_per_paragraph)

                pieces.append(sentences)
                # TODO: Detect links, store separated and insert a placeholder.
                # pieces.append(t.content)
                self._positions.append(i)
        return pieces

    def _replace_links(self):
        pass

    def update(self, texts: list[str]) -> None:
        """Update the content with the translated pieces.

        Args:
            texts (list[str]): List of texts to insert back to the
            document translated.

        Raises:
            ValueError: If the number of texts to update
                don't match the number of texts obtained
                from get_pieces method.

        See Also:
            [`get_pieces`](src.translate_md.markdown.MarkdownProcessor.write_to)
        """
        if len(self._positions) != len(texts):
            raise ValueError(
                "There should be the same number of texts that you obtained from "
                f"get_pieces: positions: {len(self._positions)}, texts: {len(texts)}"
            )
        for i, t in zip(self._positions, texts):
            self._tokens[i].content = t
            # Not clear why it should be changed the children yet, but...
            self._tokens[i].children[0].content = t  # type: ignore
            # The previous type is ignored because we only deal with inline tokens here,
            # which in fact contain children

    def render(self) -> str:
        """Get a new markdown file with the paragraphs translated.

        Args:
            texts (list[str]): List of texts to insert back to the
            document translated.
        """
        # dummy variables for render
        options: Mapping[str, Any] = {}
        env: MutableMapping = {}
        renderer = MDRenderer()
        output_markdown = renderer.render(self.tokens, options, env)
        # mdformat adds some extra \, remove it before writing the content back.
        output_markdown = output_markdown.replace("\\", "")
        return output_markdown

    def write_to(self, filename: Path) -> None:
        """Write the content of the updated markdown to disk.

        Args:
            filename (Path): Name of the new file.
        """
        translated_file = self.render()
        with open(filename, "w") as f:
            f.write(translated_file)


def is_front_matter(text: str) -> bool:
    """Check if a token pertains to the front matter.

    The check seeks if the string starts with '---' and
    the word `title` after a single line jump (it will fail if some
    space is inserted between them), and ends with '---'.

    Args:
        text (str):
            text obtained in the Token's content.
            Expects to be applied to the tokens from a markdown parsed.

    Returns:
        bool
    """
    return text.startswith("---\n") and text.endswith("\n---")


def is_figure(text: str) -> bool:
    """Check if a paragraph is just a picture in the doc.

    Some lines may contain just a picture, and there is no
    reason to translate those.
    i.e.
    '![helpner](/images/helpner-arch-part1.png)'
    The type of check is not perfect, it just fits my needs.

    Args:
        text (str): text obtained in the Token's content.

    Returns:
        bool:
    """
    text = text.strip()
    return text.startswith("![") and text.endswith(")")


def is_code(text: str) -> bool:
    """Check if a blob of text is a chunk of code.

    Args:
        text (str): text obtained in the Token's content.

    Returns:
        bool
    """
    text = text.strip()
    return text.startswith("```") and text.endswith("```")


def is_comment(text: str) -> bool:
    text = text.strip()
    return text.startswith("<!--") and text.endswith("-->")


# Regular expressions pattern to find links, images and badges.
_pat_placeholder = "\[.*?\]"
_pat_destination = "\(.*?\)"
# _pat_mdlink = "(\[.*\]\(.*\))"
_pat_mdlink = f"{_pat_placeholder}{_pat_destination}"
_pat_figure = f"!{_pat_mdlink}"
PATTERN_MDLINK = re.compile(f"({_pat_mdlink})")
PATTERN_MDLINK_FIGURE = re.compile(f"({_pat_figure})")
PATTERN_MDLINK_BADGE = re.compile(f"(\[{_pat_figure}\]{_pat_destination})")
PATTERN_HEADINGS = re.compile("(#{0,6}).*?")
# Text to replace
PLACEHOLDER_MDLINK = "-MDLINK-"


def replace_links(text: str) -> tuple[str, list[str]]:
    """Finds links in a markdown text, replaces them with a placeholder and
    returns replaced text and the links found.

    Args:
        text (str)

    Returns:
        tuple[str, list[str]]:
            The first element is the text with the links replaced and the second
            the links found.
    """
    all_links = []
    badges = re.findall(PATTERN_MDLINK_BADGE, text)
    all_links += badges
    replaced = deepcopy(text)
    for b in badges:
        replaced = replaced.replace(b, PLACEHOLDER_MDLINK)

    figures = re.findall(PATTERN_MDLINK_FIGURE, replaced)
    all_links += figures
    for f in figures:
        replaced = replaced.replace(f, PLACEHOLDER_MDLINK)

    links = re.findall(PATTERN_MDLINK, replaced)
    all_links += links
    for l in links:
        replaced = replaced.replace(l, PLACEHOLDER_MDLINK)

    return (replaced, all_links)


@dataclass
class Piece:
    """Each of the pieces extracted from the Token Stream of the processor.

    Keeps the relevant information for the text to be translated and how to
    recreate it again.
    """

    content: str
    position: int
    sentences: list[str] = []
    is_header: bool = False
    headings: str = ""
    translation: str = ""
    _replaced: list[list[str]] = []
    _is_processed: bool = False

    def process(self) -> list[str]:
        if self._is_processed:
            return

        if self.content.lstrip().startswith("#"):
            self.is_header = True
            # TODO: A section heading can also be a link, check for it
            self.headings = re.findall(PATTERN_HEADINGS, self.content.lstrip()).lstrip()

        sentences_ = nltk.sent_tokenize(self.content)
        replaced_per_paragraph = []
        for sentence in sentences_:
            (sentence, replaced) = replace_links(sentence)
            replaced_per_paragraph.append(replaced)
            self.sentences.append(sentence)

        self._replaced.append(replaced_per_paragraph)
        # In case its called more than once, avoid reprocessing.
        self._is_processed = True
        return self.sentences

    def get_content(self) -> list[str]:
        """Get the pieces of text to be translated.

        Returns:
            list[str]: Text, sentences to be translated.
        """
        pass

    def rebuild(self, translation: list[str]) -> str:
        """Rebuilds back the content to be a string like it was originally."""
        if self.is_header:
            return self.headings + " " + translation[0]

        new_content = []
        for sent, replaced in zip(translation, self._replaced):
            for link in replaced:
                sent = sent.replace(PLACEHOLDER_MDLINK, link)
            new_content.append(sent)

        # TODO: Insert the links in case there are any
        return ". ".join(new_content)
