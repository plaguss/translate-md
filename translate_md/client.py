"""
https://docs.aiohttp.org/en/stable/client_quickstart.html

ref:
https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class
"""

import asyncio
import aiohttp
import json

import translate_md.markdown as md

SPANGLISH_URL = r"http://localhost:8000/"


class SpanglishClient:
    def __init__(self) -> None:
        self._timeout = 300
        self._spanglish_url = SPANGLISH_URL
        self._loop = asyncio.get_event_loop()

    def translate_batch(self, texts: list[str]) -> str:
        return self._loop.run_until_complete(make_request(self._spanglish_url, texts))

    def translate_file(self, filename: str) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self._spanglish_url})"


async def make_request(url: str, params: list[str]):
    payload = json.dumps(params)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"text": payload}) as response:
            response = await response.json()
            return response

