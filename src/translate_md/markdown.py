"""Markdown related facilities. """

import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Mapping, MutableMapping

import nltk
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer
from warnings import warn


ParserName = Literal["zero", "commonmark", "js-default", "gfm-like"]


def read_file(filename: Path) -> str:
    """Read a whole markdown file to a string, just a helper function."""
    with open(filename, "r") as f:
        return f.read()


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
_pat_placeholder = r"\[.*?\]"
_pat_destination = r"\(.*?\)"
# _pat_mdlink = "(\[.*\]\(.*\))"
_pat_mdlink = f"{_pat_placeholder}{_pat_destination}"
_pat_figure = f"!{_pat_mdlink}"
PATTERN_MDLINK = re.compile(f"({_pat_mdlink})")
PATTERN_MDLINK_FIGURE = re.compile(fr"({_pat_figure})")
PATTERN_MDLINK_BADGE = re.compile(fr"(\[{_pat_figure}\]{_pat_destination})")
PATTERN_HEADINGS = re.compile(r"(#{0,6}).*?")
PATTERN_HEADINGS = re.compile(r"(#{0,6})\s+")
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


def insert_links(text: str, links: list[str]) -> str:
    """Function to replace back the links in the placeholders of the text.

    Replaces the placeholders one at a time.

    Args:
        text (str): Text with placeholders.
        links (list[str]): Links to insert in the placeholders.

    Returns:
        str: text with the links inserted back.
    """
    for link in links:
        text = re.sub(PLACEHOLDER_MDLINK, link, text, count=1)
    return text


@dataclass
class Piece:
    """Each of the pieces extracted from the Token Stream of the processor.

    Keeps the relevant information for the text to be translated and how to
    recreate it again.

    Args:
        content (str): The markdown text extracted.
        position (int):
            The position of the token in the MarkdownProcessor, internally
            used to place the content back in the original file.
        sentences (list[str]): Texts to be translated.
        is_header (bool):
            Determines whether the piece is a heading (they are treated
            different).
        headings (str): Headings (only relevant if is_header is True).
        replaced
    """

    content: str
    position: int
    sentences: list[str] = field(default_factory=list)
    is_header: bool = False
    headings: str = ""
    replaced: list[str] = field(default_factory=list)
    _is_processed: bool = False

    def process(self) -> list[str]:
        """Processes the piece of markdown to prepare the information
        as we need it.

        - Checks if its a heading and update accordingly.
        - Replace the possible links at the paragraph level, they will be
        inserted back after the translation is done per sentence, and the
        content joined again.
        - Tokenize the paragraph into sentences to be translated and return
        them.

        Returns:
            list[str]: sentences with the content to be translated.
        """
        if self._is_processed:
            return self.sentences

        if self.content.lstrip().startswith("#"):
            self.is_header = True
            self.headings = re.findall(PATTERN_HEADINGS, self.content.lstrip())[0]
            # Replace the headings with spaces to obtain just the text.
            # Some models to translate text remove the the headings
            # and the information could be lost.
            self.content = self.content.replace(self.headings, "").lstrip()

        (content, replaced) = replace_links(self.content)
        self.replaced = replaced
        self.sentences = nltk.sent_tokenize(content)

        # In case its called more than once, avoid reprocessing.
        self._is_processed = True
        return self.sentences

    def rebuild(self, translation: list[str]) -> str:
        """Rebuilds back the content to be a string like it was originally.

        - In case of a header this means adding the (first) translated sentence
        inserted to the previously obtained headings.
        - Otherwise it joins the translated sentences and replaced the possible
        links.
        """
        if self.is_header:
            # We have to check if it contained any link
            text = translation[0]
            if len(self.replaced) > 0:
                # If thats the case, replace it and return the new heading
                text = insert_links(text, self.replaced)
            return self.headings + " " + text

        # Join with whitespace, nltk is suposed to keep the points after
        # tokenizing a paragraph.
        new_content = " ".join(translation)
        # Insert the links in case there are any
        new_content = insert_links(new_content, self.replaced)
        self.content = new_content
        return new_content


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
        # self._positions: list[int] = []  # Not needed anymore
        self._content = markdown_content
        # Stores the links that may be captured when extracting the
        # pieces of the markdown.
        # List of paragraphs, containing a list of sentences, with maybe
        # a list of links.
        # self._replaced: list[list[list[str]]] = []
        self._pieces: list[Piece] = []

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

    def get_pieces(self) -> list[Piece]:
        """Gets the pieces of the markdown file to be translated.

        The relevant pieces are those tokens considered of type
        'inline' and which aren't the front matter, a figure, code
        or markdown comments.

        Internally stores the position of the corresponding tokens
        for later use.
        """
        self._pieces = []
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
                self._pieces.append(Piece(t.content, i))

        return self._pieces

    def update(self, translated_pieces: list[Piece]) -> None:
        """Update the content with the translated pieces.

        Its up to the user to check the pieces correspond to the original positions,
        otherwise the document can have a bad 
        It will (try) to replace all the pieces inserted.
        A warning will appear if the translated_pieces don't have the same shape
        as the already parsed.
        
        Args:
            translated_pieces (list[Piece]):
                List of pieces with the translated texts to insert back to the
                document.

        See Also:
            [`get_pieces`](src.translate_md.markdown.MarkdownProcessor.write_to)
        """
        if len(self._pieces) != len(translated_pieces):
            warn(
                "There should be the same number of texts that you obtained from "
                f"get_pieces: old pieces: {len(self._positions)}, new pieces: {len(translated_pieces)}. "
                "The remaining content will be left as is."
            )
        for piece in translated_pieces:
            # print(f"piece: {piece.position}")
            pos = piece.position
            self._tokens[pos].content = piece.content
            # Not clear why it should be changed the children yet, but...
            self._tokens[pos].children[0].content = piece.content

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
        print(f"File written to: {filename}.")
