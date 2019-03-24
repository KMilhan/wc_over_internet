class AccessLocalURI(PermissionError):
    """
    User requested Local URI
      * Local file (file:///etc/resolv.conf.d/resolv.conf)
      * Intranet URI (https://cluster.local/dashboard)
    """
    pass


class NotAllowedScheme(AccessLocalURI):
    """
    User requested not expected protocol.
      * Only `https` and `http` are allowed
      * The other protocols are considered "potentially" local
    """
    pass


class NotReacheableLocation(IOError):
    """No routing possible"""
    pass


class TooBigResource(IOError):
    """User requested resource is too big to count a word"""
    pass


class NotInResultCacheQuery(KeyError):
    """We don't have such result in cache"""
    pass


class NotInDocumentStorage(KeyError):
    """We don't have such result in document storage"""
    pass


class CannotAccessToRedis(ConnectionError):
    """Cannot connect to Redis"""
    pass


class CannotAccessToMongo(ConnectionError):
    """Cannot connect to MongoDB"""
    pass
