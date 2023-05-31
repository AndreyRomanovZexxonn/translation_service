import json
import logging
import random
from typing import TYPE_CHECKING

import httpx
from fastapi import HTTPException
from starlette import status
from tenacity import stop_after_attempt, AsyncRetrying, RetryError, wait_fixed

from src.infra.provider.google.web import urls
from src.infra.provider.google.web.constants import (
    DEFAULT_CLIENT_SERVICE_URLS,
    DEFAULT_FALLBACK_SERVICE_URLS,
    DEFAULT_USER_AGENT, LANGUAGES, Lang
)
from src.infra.provider.google.web.gtoken import TokenAcquirer
from src.infra.provider.google.web.models import GoogleTranslatedWord, TranslatedPart

if TYPE_CHECKING:
    from httpx._types import ProxiesTypes


RPC_ID = 'MkEWBc'
LOG = logging.getLogger(__name__)


class Translator:
    """Google Translate ajax API implementation class

    You have to create an instance of Translator to use this API

    :param service_urls: Google Translate url list. URLs will be used randomly.
                         For example ``["translate.google.com", "translate.google.co.kr']``
                         To preferably use the non webapp api, service url should be translate.googleapis.com
    :type service_urls: a sequence of strings

    :param user_agent: the User-Agent header to send when making requests.
    :type user_agent: :class:`str`

    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :type proxies: dictionary

    :param timeout: Definition of timeout for httpx library.
                    Will be used for every request.
    :type timeout: number or a double of numbers
    :param proxies: proxies configuration.
                    Dictionary mapping protocol or protocol and host to the URL of the proxy
                    For example ``{'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}``
    :param raise_exception: if `True` then raise exception if smth will go wrong
    :param http2: whether to use HTTP2 (default: True)
    :param use_fallback: use a fallback method
    :type raise_exception: boolean
    """

    def __init__(
            self,
            service_urls=DEFAULT_CLIENT_SERVICE_URLS,
            user_agent=DEFAULT_USER_AGENT,
            proxies: "ProxiesTypes" = None,
            timeout: httpx.Timeout = None,
            http2: bool = True,
            use_fallback: bool = False
    ):

        self.proxies = proxies
        self.timeout = timeout
        self.headers = {
            'User-Agent': user_agent,
            'Referer': 'https://translate.google.com',
        }

        self.client = httpx.Client(http2=http2)
        self.client.headers.update(self.headers)
        if proxies is not None:
            self.client.proxies = proxies
        if timeout is not None:
            self.client.timeout = timeout

        if use_fallback:
            self.service_urls = DEFAULT_FALLBACK_SERVICE_URLS
            self.client_type = 'gtx'
        else:
            # default way of working: use the defined values from user app
            self.service_urls = service_urls
            self.client_type = 'tw-ob'
            self.token_acquirer = TokenAcquirer(
                client=self.client, host=self.service_urls[0]
            )

    @classmethod
    def _build_rpc_request(cls, text: str, dest: Lang, src: str):
        return json.dumps([[
            [
                RPC_ID,
                json.dumps([[text, src, dest.value, True], [None]], separators=(',', ':')),
                None,
                'generic',
            ],
        ]], separators=(',', ':'))

    def _pick_service_url(self):
        if len(self.service_urls) == 1:
            return self.service_urls[0]
        return random.choice(self.service_urls)

    async def _call_translate(self, text: str, dest: Lang, src: str):
        url = urls.TRANSLATE_RPC.format(host=self._pick_service_url())
        data = {
            'f.req': self._build_rpc_request(text, dest, src),
        }
        params = {
            'rpcids': RPC_ID,
            'bl': 'boq_translate-webserver_20201207.13_p0',
            'soc-app': 1,
            'soc-platform': 1,
            'soc-device': 1,
            'rt': 'c',
        }

        client_kwargs = dict(headers=self.headers)
        if self.timeout:
            client_kwargs["timeout"] = self.timeout
        if self.proxies:
            client_kwargs["proxies"] = self.proxies
        async with httpx.AsyncClient(**client_kwargs) as client:
            r = await client.post(url, params=params, data=data)

        if r.status_code != status.HTTP_200_OK:
            raise Exception(
                f"Unexpected status code '{r.status_code}' from {self.service_urls}"
            )

        return r.text, r

    @classmethod
    def _prepare_src(cls, src: str) -> str:
        if src != 'auto' and src not in LANGUAGES:
            raise ValueError('invalid source language')
        return src

    @classmethod
    def _prepare_dest(cls, dest: Lang) -> Lang:
        if dest not in LANGUAGES:
            raise ValueError('invalid destination language')
        return dest

    async def translate(
            self, text: str, dest: Lang = Lang.EN, src: str = "auto"
    ) -> GoogleTranslatedWord:
        try:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(3), wait=wait_fixed(1)):
                with attempt:
                    return await self._translate(text=text, dest=dest, src=src)
        except RetryError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FAILED_TO_TRANSLATE"}
            )

    async def _translate(
            self, text: str, dest: Lang = Lang.EN, src: str = "auto"
    ) -> GoogleTranslatedWord:

        dest: Lang = self._prepare_dest(dest)
        src: str = self._prepare_src(src)

        origin = text
        response_data, response = await self._call_translate(text, dest, src)
        return self._parse_translation(response_data, origin=origin, dest=dest, src=src)

    def _parse_translation(
            self, response_data, origin: str, dest: Lang = Lang.EN, src: str = "auto"
    ):
        resp: str = self._parse_translation_response(response_data)
        data: list = json.loads(resp)
        parsed: list = json.loads(data[0][2])
        should_spacing = parsed[1][0][0][3]
        translated_parts = list(map(
            lambda part: TranslatedPart(text=part[0], candidates=part[1] if len(part) >= 2 else []),
            parsed[1][0][0][5]
        ))
        translated = (' ' if should_spacing else '').join(map(lambda part: part.text, translated_parts))

        if src == 'auto':
            try:
                src = parsed[2]
            except:
                pass
        if src == 'auto':
            try:
                src = parsed[0][2]
            except:
                pass

        # currently not available
        confidence = None

        try:
            origin_pronunciation = parsed[0][0]
        except IndexError:
            origin_pronunciation = None

        try:
            pronunciation = parsed[1][0][0][1]
        except IndexError:
            pronunciation = None

        extra_data = {
            'confidence': confidence,
            'parts': translated_parts,
            'origin_pronunciation': origin_pronunciation,
            'parsed': parsed,
        }
        result = GoogleTranslatedWord(
            src=src, dest=dest, origin=origin,
            text=translated, pronunciation=pronunciation,
            parts=translated_parts,
            extra_data=extra_data,
            translations=GoogleTranslatedWord.translations_from_parsed_data(parsed),
            definitions=GoogleTranslatedWord.definitions_from_parsed_data(parsed),
            examples=GoogleTranslatedWord.examples_from_parsed_data(parsed),
        )
        LOG.debug(
            f"Translated {result.origin} -> {result.text}, "
            f"lang {result.src} -> {result.dest}, synonyms={result.translations}"
        )
        return result

    @classmethod
    def _parse_translation_response(cls, data: str) -> str:
        token_found = False
        resp = ''
        square_bracket_counts = [0, 0]
        for line in data.split('\n'):
            token_found = token_found or f'"{RPC_ID}"' in line[:30]
            if not token_found:
                continue

            is_in_string = False
            for index, char in enumerate(line):
                if char == '\"' and line[max(0, index - 1)] != '\\':
                    is_in_string = not is_in_string
                if not is_in_string:
                    if char == '[':
                        square_bracket_counts[0] += 1
                    elif char == ']':
                        square_bracket_counts[1] += 1

            resp += line
            if square_bracket_counts[0] == square_bracket_counts[1]:
                break
        return resp
