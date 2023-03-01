"""Markdown related facilities. """

from pathlib import Path
from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdformat.renderer import MDRenderer

md = MarkdownIt("zero")


def read_file(filename: Path) -> str:
    with open(filename, "r") as f:
        return f.read()


class MarkdownProcessor:
    def __init__(self, markdown_content: str) -> None:
        self.md = MarkdownIt("zero")
        self._tokens = None
        self._positions = None
        self._content = markdown_content

    @property
    def tokens(self) -> list[Token]:
        """Parsed pieces of the markdown file. 
        The content will be extracted from these pieces, updated and 
        created back.
        The setter method deals with updating the appropriate positions.
        """
        if self._tokens:
            self._tokens = self.md.parse(self._content)
        return self._tokens

    @tokens.setter
    def tokens(self, toks: list[Token]) -> None:

        self._tokens = toks

    def get_pieces(self) -> list[str]:
        """Gets the pieces of the markdown file to be translated. 

        TODO:
        The relevant tokens are:
        - type == 'inline'
        """
        self._positions = []
        toks = []
        for i, t in enumerate(self.tokens):
            if t == 1:  # Set the logic to 
                toks.append(t)
                self._positions.append(i)
        return toks

    def update_content(self, text: list[str]) -> None:
        """Takes the translated text and inserts it back to the tokens
        it belongs to. """
        self.

    def render() -> str:
        """Obtain the markdown file in the target language.
        
        This content may be written directly to a file.
        """
        options, env = {}, {}  # dummy variables
        renderer = MDRenderer()
        output_markdown = renderer.render(tokens, options, env)
        # mdformat adds some extra \, remove it before writing the content back.
        output_markdown = output_markdown.replace("\\", "")
        return output_markdown
