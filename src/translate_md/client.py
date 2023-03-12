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
    r"""Client to interact with the [Spanglish](https://github.com/plaguss/spanglish)
    service.

    Args:
        url (str, optional):
            URL where the service is exposed. Defaults to SPANGLISH_URL.
    """

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
        return self._request("/single", payload={"text": text})

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
        result = self._request("/batched", payload={"texts": json.dumps(texts)})

        try:
            return json.loads(result)
        except json.decoder.JSONDecodeError as e:
            # There are some errors when retrieving a batch of texts.
            # The service returns a list of texts
            raise ValueError(f"Couldn't load the json encoded list: {result}") from e

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
                Filename for the new markdown file to be generated.
                Defaults to None, in which case it is generated
                internally.
        """
        logger.info("reading file")
        md_content = md.read_file(filename)
        mdproc = md.MarkdownProcessor(md_content)
        pieces = mdproc.get_pieces()
        # TODO: Check if the file is big (say more than 5000 characters)
        # and send the content in pieces.
        translated_text = self._multi_request("/single", pieces)
        logger.info("updating content")
        mdproc.update(translated_text)
        if new_filename is None:
            new_filename = filename.parent / f"{filename.stem}.es{filename.suffix}"
        mdproc.write_to(new_filename)
        logger.info(f"file written at: {new_filename}")

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self._spanglish_url})"

    # fmt: off
    def _request(
        self,
        endpoint: str,
        payload: dict[str, str]
    ) -> str:  # pragma: no cover
    # fmt: on
        """Internal method to deal with the requests.

        Args:
            endpoint (str): Endpoint of the app (`/single` or `/batched`)
            payload (str): The parameter values of the endpoint.

        Returns:
            str: API response.
        """
        url = urljoin(self._spanglish_url, endpoint)
        with requests.Session() as session:
            logger.info(f"sending request to url: {url}")
            response = session.request("GET", url, params=payload)
            try:
                return response.json()
            except Exception as exc:
                logger.error("Error parsing a request to json")
                raise ValueError("Unexpected error on the response") from exc

    def _multi_request(
        self, endpoint: str, texts: list[str]
    ) -> list[str]:  # pragma: no cover
        """Internal method to deal with the requests.

        Args:
            endpoint (str): Endpoint of the app (`/single` or `/batched`)
            payload (str): The parameter values of the endpoint.

        Returns:
            str | list[str]: API response.

        Note:
            This method shouldn't be necessary, but there appear some errors
            translating markown texts with multiple headings or a high number
            of symbols through the `/batched` endpoint. For the time being,
            this would do the trick. Let a single method which uses
            properly a ThreadPoolExecutor for multiple requests.
        """
        url = urljoin(self._spanglish_url, endpoint)
        with requests.Session() as session:
            logger.info(f"sending requests to url: {url}")
            responses = [session.request("GET", url, params={"text": t}) for t in texts]
            try:
                return [r.json() for r in responses]
            except Exception as exc:
                raise ValueError("Unexpected error on the response") from exc
