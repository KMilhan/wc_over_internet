"""Data storage layer"""
from abc import ABC
from collections import Counter, defaultdict

from simplewc.exceptions import NotInDocumentStorage, NotInResultCacheQuery


class DocumentStorage(ABC):
    """Where we store HTML Document"""

    def __init__(self, host: str, auth=None):
        """
        :param host: access information
        :param auth: authentication information
        """
        self.host = host
        self.auth = auth

    def store(self, uri: str, counter: Counter):
        """Store html document"""
        raise NotImplementedError

    def get(self, uri: str):
        """Get stored html document"""
        raise NotImplementedError


class QueryCache(ABC):
    """Where we store recent result"""

    def __init__(self, host: str, auth=None):
        """
        :param host: access information
        :param auth: authentication information
        """
        self.host = host
        self.auth = auth

    def store(self, uri: str, word: str, count: int):
        """Store recent result"""
        raise NotImplementedError

    def get(self, uri: str, word: str) -> int:
        """Get stored recent result"""
        raise NotImplementedError


class MockDocumentStorage(DocumentStorage):
    def __init__(self, host: str):
        super(MockDocumentStorage, self).__init__(host)
        self.mock_db = dict()

    def store(self, uri: str, counter: Counter):
        self.mock_db[uri] = counter

    def get(self, uri: str):
        if uri in self.mock_db:
            return self.mock_db[uri]
        else:
            raise NotInDocumentStorage


class MockQueryCache(QueryCache):
    def __init__(self, host: str):
        super(MockQueryCache, self).__init__(host)
        self.mock_cache = defaultdict(int)

    def get(self, uri: str, word: str) -> int:
        if (uri, word) in self.mock_cache:
            return self.mock_cache[(uri, word)]
        else:
            raise NotInResultCacheQuery

    def store(self, uri: str, word: str, count: int):
        self.mock_cache[(uri, word)] = count


mds = MockDocumentStorage('')
mqc = MockQueryCache('')
