"""
https://docs.aiohttp.org/en/stable/client_quickstart.html

ref:
https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class
"""

import json
from urllib.parse import urljoin

import requests

SPANGLISH_URL = r"http://localhost:8000/"


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

    def translate_batch(self, texts: list[str]) -> str:
        """Translates a batch of texts.

        Instead of calling repeatedly on a loop the method `translate`, 
        this method should be preferred, send a list of texts to 
        translate and get them back in the same order.

        Args:
            texts (list[str]): Texts to translate

        Returns:
            str: _description_

        Examples:
            ```python
            >>> client.translate_batch(["hello", "world", "one", "two"])
            ["hola", "mundo", "uno", "dos"]
            ```
        """
        return json.loads(self._request("/batched", payload=json.dumps(texts)))

    def translate_file(self, filename: str) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self._spanglish_url})"

    def _request(self, endpoint: str, payload: str) -> str | list[str]:
        """Internal method to deal with the requests.

        Args:
            endpoint (str): Endpoint of the app (`/single` or `/batched`)
            payload (str): The parameter values of the endpoint.

        Returns:
            st | list[str]: API response.
        """
        url = urljoin(self._spanglish_url, endpoint)
        with requests.Session() as session:
            response = session.request("GET", url, params={"text": payload})
            try:
                return response.json()
            except Exception as exc:
                raise ValueError("Unexpected error on the response") from exc
