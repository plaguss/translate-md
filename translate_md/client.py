"""
https://docs.aiohttp.org/en/stable/client_quickstart.html

ref:
https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class
"""

from urllib.parse import urljoin
import json
from typing import Any
import translate_md.markdown as md

import requests

SPANGLISH_URL = r"http://localhost:8000/"


class SpanglishClient:
    def __init__(self) -> None:
        self._spanglish_url = SPANGLISH_URL

    def translate(self, text: str) -> str:
        return self._request("/single", payload=text)

    def translate_batch(self, texts: list[str]) -> str:
        # json encode the request parameters
        return self._request("/batch", payload=json.dumps(texts))

    def translate_file(self, filename: str) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self._spanglish_url})"

    def _request(self, endpoint: str, payload: str) -> Any:
        """_summary_

        Args:
            endpoint (str): TODO. Endpoint of the app.
            payload (str): TODO. Document according to the app.
                It should be a json encoded string:
                payload = json.dumps(["Hello world one", "hello world two"])
                or directly the string to translate.

        Returns:
            Any: _description_
        """
        url = urljoin(self._spanglish_url, endpoint)
        with requests.Session() as session:
            response = session.request("GET", url, params={"text": payload})
            try:
                return response.json()
            except Exception as exc:
                raise ValueError("Unexpected error on the response") from exc
