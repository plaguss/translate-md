"""Markdown related facilities. """

from pathlib import Path
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

md = MarkdownIt("zero")


def read_file(filename: Path) -> str:
    """Read a whole markdown file to a string."""
    with open(filename, "r") as f:
        return f.read()


class MarkdownProcessor:
    """Class that allows to work with a markdown file, extracting
    the text content to be translated.

    The expected format of the markdown file is the one used in hugo
    for blogging.

    Notes:
        See https://gohugo.io/ for type of markdown files
    """

    def __init__(self, markdown_content: str) -> None:
        """
        Args:
            markdown_content (str):
                The content of a markdown file as a string.
        """
        self.md = MarkdownIt("zero")
        self._tokens = None
        self._positions = None
        self._content = markdown_content

    @property
    def tokens(self) -> list[Token]:
        """Parsed pieces of the markdown file.
        The content will be extracted from these pieces, updated and
        created back.
        TODO
        The setter method deals with updating the appropriate positions.
        """
        if self._tokens is None:
            self._tokens = self.md.parse(self._content)
        return self._tokens

    def __repr__(self) -> str:
        return type(self).__name__ + f"({len(self.tokens)})"

    def get_pieces(self) -> list[str]:
        """Gets the pieces of the markdown file to be translated.

        The relevant pieces are those tokens considered of type
        'inline' and which aren't the front matter, a figure, code
        or markdown comments.

        Internally stores the position of the corresponding tokens
        for later use.
        """
        self._positions = []
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
                pieces.append(t.content)
                self._positions.append(i)
        return pieces

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
            get_pieces
        """
        if len(self._positions) != len(texts):
            raise ValueError(
                "There should be the same number of texts that you obtained from get_pieces"
            )
        for i, t in zip(self._positions, texts):
            self._tokens[i].content = t

    def render(self) -> str:
        """Get a new markdown file with the paragraphs translated."""
        options, env = {}, {}  # dummy variables
        renderer = MDRenderer()
        output_markdown = renderer.render(self._tokens, options, env)
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

    The check seeks if the string starts with --- and
    the word `title` after a single line jump (it will fail if some
    space is inserted between them), and ends with ---.

    Args:
        text (str): Text to check.
            Expects to be applied to the tokens from a markdown parsed.

    Returns:
        bool
    """
    return text.startswith("---\ntitle") and text.endswith("---")


def is_figure(text: str) -> bool:
    """Check if a paragraph is just a picture in the doc.

    Some lines may contain just a picture, and there is no
    reason to translate those.
    i.e.
    '![helpner](/images/helpner-arch-part1.png)'
    The check is not perfect, it just fits my needs.

    Args:
        text (str): text

    Returns:
        bool:
    """
    text = text.strip()
    return text.startswith("![") and text.endswith(")")


def is_code(text: str) -> bool:
    text = text.strip()
    return text.startswith("```") and text.endswith("```")


def is_comment(text: str) -> bool:
    text = text.strip()
    return text.startswith("<!--") and text.endswith("-->")
