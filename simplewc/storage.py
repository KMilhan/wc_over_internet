"""Data storage layer"""
import sys
from abc import ABC
from collections import Counter, defaultdict
from datetime import datetime

import redis
from pymongo import MongoClient
from pymongo.errors import OperationFailure

from simplewc.config import (
    CACHE_EXPIRE,
    MONGO_COLLECTION,
    MONGO_DB,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_TTL,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)
from simplewc.exceptions import (
    CannotAccessToMongo,
    CannotAccessToRedis,
    NotInDocumentStorage,
    NotInResultCacheQuery,
)


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
    """Pure in-memory mocking document storage for testing purpose"""

    def __init__(self, host: str):
        super(MockDocumentStorage, self).__init__(host)
        self.mock_db = dict()

    def store(self, uri: str, counter: Counter):
        self.mock_db[uri] = counter

    def get(self, uri: str):
        if uri in self.mock_db:
            return self.mock_db[uri]

        raise NotInDocumentStorage


class MockQueryCache(QueryCache):
    """Pure in-memory mocking query storage for testing purpose"""

    def __init__(self, host: str):
        super(MockQueryCache, self).__init__(host)
        self.mock_cache = defaultdict(int)

    def get(self, uri: str, word: str) -> int:
        if (uri, word) in self.mock_cache:
            return self.mock_cache[(uri, word)]

        raise NotInResultCacheQuery

    def store(self, uri: str, word: str, count: int):
        self.mock_cache[(uri, word)] = count


class RedisQueryCache(QueryCache):
    """Redis as a LRU query cache"""

    def __init__(self, host: str, port: int, db: int, **redis_opt):
        """
        Instantiate RedisQueryCache
        :param host: Redis host
        :param port: Redis port
        :param db: Redis DB
        :param redis_opt: Redis additional options such as cert and password
        """
        super(RedisQueryCache, self).__init__(host)
        self._pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis = redis.Redis(connection_pool=self._pool, **redis_opt)
        self.expire = CACHE_EXPIRE

        try:
            self.redis.exists("wc_test_val")
        except ConnectionError:
            raise CannotAccessToRedis

    def get(self, uri: str, word: str) -> int:
        """
        Get ResultCache from Redis Server
        :param uri: Where HTML document originates
        :param word: A word to count
        :return: Occurrence of `word` in HTML doc at `uri`
        :raise: NotInResultCacheQuery in case we didn't hit cache
        """
        cache = self.redis.hget(uri, word)
        if cache is not None:
            return int(cache)

        raise NotInResultCacheQuery

    def store(self, uri: str, word: str, count: int):
        """
        Store cache in RedisQueryCache server. The first time it stores document(uri), it sets lifespan of cache.
        Thus, after certain time, all caches in a document must be refreshed together
        :param uri: Where HTML document originates
        :param word: A word to count
        :param count: Occurrence of `word` in HTML doc at `uri` to save
        :return:
        """
        if self.redis.exists(uri):
            self.redis.hset(uri, word, str(count))
            return

        self.redis.hset(uri, word, str(count))
        self.redis.expire(uri, self.expire)


class MongoDocumentStorage(DocumentStorage):
    """MongoDB as a document storage"""

    def __init__(
        self,
        host: str,
        port: int,
        mongo_db_name: str,
        mongo_collection: str,
        mongo_ttl: int,
        **mongo_opt,
    ):
        """
        :param host: MongoDB host
        :param port: MongoDB port
        :param mongo_db_name: MongoDB database name
        :param mongo_collection: MongoDB collection name for HTML documents
        :param mongo_ttl: MongoDB document's life span
        :param mongo_opt: Additional option (auth for example) for MongoDB connection
        """
        super(MongoDocumentStorage, self).__init__(host)
        self._mongo = MongoClient(host, port, **mongo_opt)
        try:
            self._mongo.server_info()
            self._mongo_db = self._mongo.get_database(mongo_db_name)
            self.collection = self._mongo_db.get_collection(mongo_collection)
        except ConnectionError:
            raise CannotAccessToMongo

        try:
            self.collection.create_index("added", expireAfterSeconds=mongo_ttl)
        except OperationFailure:
            print(
                "Warning: TTL value for MongoDB document set with different value",
                file=sys.stderr,
            )

    @classmethod
    def to_mongo_key(cls, key: str) -> str:
        """MongoDB does not support `$` and `.` in key. Converting it to unicode is MongoDB's official recommendation"""
        return key.replace("$", "＄").replace(".", "．")

    @classmethod
    def to_plain_key(cls, key: str) -> str:
        """Revert escaped MongoDB key string to original string"""
        return key.replace("＄", "$").replace("．", ".")

    @classmethod
    def to_mongo_hash(cls, counter: Counter) -> dict:
        """MongoDB does not support `$` and '.' in hash key"""
        return {cls.to_mongo_key(key): counter[key] for key in counter}

    @classmethod
    def to_counter(cls, mongo_hash: dict) -> Counter:
        """Cast hash from MongoDB data and return it as Python `Counter` object"""
        c = Counter()
        for key in mongo_hash:
            c[cls.to_plain_key(key)] = mongo_hash[key]
        return c

    def store(self, uri: str, counter: Counter):
        """
        Save (word-counted) HTML document into MongoDB
        :param uri: Where HTML document originates
        :param counter: HTML document in a form of Counter{Word:str, Occurrence:int}
        :return: None
        """
        uri = self.to_mongo_key(uri)
        self.collection.insert_one(
            {
                "added": datetime.utcnow(),
                "uri": uri,
                "counter": self.to_mongo_hash(counter),
            }
        )

    def get(self, uri: str) -> Counter:
        """
        Get (word-counted) HTML document from MongoDB
        :param uri: Where HTML document originates
        :return: HTML document in a form of Counter{Word:str, Occurrence:int}
        :raise: NotInDocumentStorage when we can't find it in MongoDB
        """
        uri = self.to_mongo_key(uri)
        doc = self.collection.find_one({"uri": uri})
        if doc:
            return self.to_counter(doc["counter"])

        raise NotInDocumentStorage


_RQC = None
_MDS = None


def get_redis_cache():
    """Get singleton redis cache instance"""
    global _RQC
    if _RQC is not None:
        return _RQC
    _RQC = RedisQueryCache(REDIS_HOST, REDIS_PORT, REDIS_DB)
    return _RQC


def get_mongo_db():
    """Get singleton mongodb document storage instance"""
    global _MDS
    if _MDS:
        return _MDS
    _MDS = MongoDocumentStorage(
        MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION, MONGO_TTL
    )
    return _MDS
