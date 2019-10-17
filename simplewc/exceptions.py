"""Exceptions for WordCounter"""


class AccessLocalURI(PermissionError):
    """
    User requested Local URI
      * Local file (file:///etc/resolv.conf.d/resolv.conf)
      * Intranet URI (https://cluster.local/dashboard)
    """


class NotAllowedScheme(AccessLocalURI):
    """
    User requested not expected protocol.
      * Only `https` and `http` are allowed
      * The other protocols are considered "potentially" local
    """


class NotReacheableLocation(IOError):
    """No routing possible"""


class TooBigResource(IOError):
    """User requested resource is too big to count a word"""


class NotInResultCacheQuery(KeyError):
    """We don't have such result in cache"""


class NotInDocumentStorage(KeyError):
    """We don't have such result in document storage"""


class CannotAccessToRedis(ConnectionError):
    """Cannot connect to Redis"""


class CannotAccessToMongo(ConnectionError):
    """Cannot connect to MongoDB"""
