"""Represent Data Model Layer"""
import socket
from collections import Counter
from ipaddress import IPv6Address, ip_address
from string import punctuation
from typing import Generator, Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from simplewc.config import ALLOWED_PROTOCOLS, MAX_CONTENT_SIZE
from simplewc.exceptions import (
    AccessLocalURI,
    NotAllowedScheme,
    NotInDocumentStorage,
    NotInResultCacheQuery,
    NotReacheableLocation,
    TooBigResource,
)
from simplewc.storage import DocumentStorage, QueryCache


def raise_if_not_safe(uri: str):
    """
    Check if given URI is pointing publicly available resource
    :param uri: URI to user requested resource
    :return: None
    :raises: `NotAllowedScheme` for unexpected protocol and `AccessLocalURI`
    for local resources
    """
    up = urlparse(uri)
    if up.scheme not in ALLOWED_PROTOCOLS:
        raise NotAllowedScheme
    try:
        ip = ip_address(socket.gethostbyname(up.netloc))
    except socket.gaierror:
        raise NotReacheableLocation

    if ip.is_link_local:
        raise AccessLocalURI("Access to %s is to local resource" % uri)
    if isinstance(ip, IPv6Address) and ip.is_site_local:
        raise AccessLocalURI("Access to %s is to local resource" % uri)
    if not ip.is_global or ip.is_loopback or ip.is_reserved:
        raise AccessLocalURI("Access to %s is to non public resource" % uri)


def tokenize_html_to_words(
    content: Union[str, bytes]
) -> Generator[str, None, None]:
    """
    Parse HTML content and split into word tokens.
      * Words are case insensitive. IOW, Always lower case.
      * Punctuations in the beginning and the end are stripped out
        - e.g., "fit." is treated as "fit"
      * HTML tags are considered as white spaces between words
        - e.g., "fit</p>" is considered as "fit" and "</p>".
      * Tedious work including decoding/encoding is done by BeautifulSoup
    :param content: HTML document
    :return: Each token we find in html document
    """
    soup = BeautifulSoup(content, "html.parser")
    for tok in soup.prettify().split():
        yield tok.strip(punctuation).lower()
    return


def retrieve_html(uri: str) -> bytes:
    """
    Retrieve HTML document in given uri
    :param uri: URI to the HTML document
    :return: HTML document response's content
    """

    # TODO(KMilhan): Implement retry
    rqg = requests.get(uri, stream=True)
    if int(rqg.headers["Content-length"]) < MAX_CONTENT_SIZE:
        return rqg.content

    raise TooBigResource(
        "%s is too big file to parse" % rqg.headers["Content-length"]
    )


class HTMLDocumentModel:
    """Represents HTML Document and its behaviors"""

    def __init__(
        self, uri: str, doc_store: DocumentStorage, query_cache: QueryCache
    ):
        """
        Create HTMLDocumentModel
        :param uri: Where the HTML Document is serviced
        :param doc_store: Document Storage for cache service
        :param query_cache: Query result cache
        """
        raise_if_not_safe(uri)
        self.uri = uri
        self.doc_store = doc_store
        self.query_cache = query_cache
        self.get_html = retrieve_html  # Define how we retrieve HTML document
        self._local_counter_cache: Counter = None  # Local HTML document cache

    def count_word(self, word: str) -> int:
        """
        Facade for counting word
        :param word: Count the given `word`'s appearance in this HTML document
        :return: An appearance of `word` in this HTML document
        """
        word = word.lower()
        try:
            # Try to use cache first. And do not extend TTL
            return self.query_cache.get(self.uri, word)
        except NotInResultCacheQuery:
            # Try to use document storage. Update query cache
            self.query_cache.store(
                self.uri, word, self.local_counter_cache[word]
            )
            return self.local_counter_cache[word]

    @property
    def local_counter_cache(self) -> Counter:
        """
        Returns counter(internal form of HTML document) cache
          * If we can find html doc in Document storage, load it
          * else, get it over the internet and store it in Document storage
        :return: Locally loaded cache of HTML document
        """
        if self._local_counter_cache:
            #  If we already cached it, early return
            return self._local_counter_cache
        try:
            # Try to use document storage
            self._local_counter_cache = self.doc_store.get(self.uri)
        except NotInDocumentStorage:
            # We failed to query document storage.

            # Then, actually access web
            self._local_counter_cache = Counter(
                tokenize_html_to_words(self.get_html(self.uri))
            )
            # Store the result
            self.doc_store.store(self.uri, self._local_counter_cache)

        return self._local_counter_cache
