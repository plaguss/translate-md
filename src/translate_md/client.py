"""Client for spanglish. """

import json
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests

import translate_md.markdown as md
from translate_md.logger import get_logger

SPANGLISH_URL = r"http://localhost:8000/"


logger = get_logger("client")


class SpanglishClient:
    def __init__(self, url: str = SPANGLISH_URL) -> None:
        self._spanglish_url = url

    def translate(self, text: str) -> str:
        """Translate a piece of text from english to spanish.

        Args:
            text (str): string to translate.

        Returns:
            str: translated text

        Examples:
           ```python
            >>> client.translate("hello world")
            'hola mundo'
            ```
        """
        return self._request("/single", payload=text)

    def translate_batch(self, texts: list[str]) -> list[str]:
        """Translates a batch of texts.

        Instead of calling repeatedly on a loop the method `translate`,
        this method should be preferred, send a list of texts to
        translate and get them back in the same order.

        Args:
            texts (list[str]): Texts to translate

        Returns:
            list[str]: list of texts translated.

        Examples:
            ```python
            >>> client.translate_batch(["hello", "world", "one", "two"])
            ["hola", "mundo", "uno", "dos"]
            ```
        """
        return json.loads(self._request("/batched", payload=json.dumps(texts)))

    def translate_file(
        self, filename: Path, new_filename: Optional[Path] = None
    ) -> None:
        """Takes the filename of a markdown file in disk and processes to
        obtain the paragraphs which contain text, sends them to translate
        them and replaces the new text. Finally writes the new document
        to disk.

        Args:
            filename (Path): Path to the markdown file.
            new_filename (Optional[Path], optional):
                New filename to write the contents back. Defaults to None.
        """
        logger.info("reading file")
        md_content = md.read_file(filename)
        mdproc = md.MarkdownProcessor(md_content)
        pieces = mdproc.get_pieces()
        # TODO: Check if the file is big (say more than 5000 characters)
        # and send the content in pieces.
        translated_text = self.translate_batch(pieces)
        logger.info("updating content")
        mdproc.update(translated_text)
        if new_filename is None:
            new_filename = filename.parent / f"{filename.stem}.es{filename.suffix}"
        mdproc.write_to(new_filename)
        logger.info(f"file written at: {new_filename}")

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self._spanglish_url})"

    def _request(self, endpoint: str, payload: str) -> str | list[str]: # pragma: no cover
        """Internal method to deal with the requests.

        Args:
            endpoint (str): Endpoint of the app (`/single` or `/batched`)
            payload (str): The parameter values of the endpoint.

        Returns:
            str | list[str]: API response.
        """
        url = urljoin(self._spanglish_url, endpoint)
        with requests.Session() as session:
            logger.info(f"sending request to url: {url}")
            response = session.request("GET", url, params={"text": payload})
            try:
                return response.json()
            except Exception as exc:
                raise ValueError("Unexpected error on the response") from exc
