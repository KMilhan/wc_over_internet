"""Configuration for wordcounter"""

ALLOWED_PROTOCOLS = ("http", "https")
MAX_CONTENT_SIZE = 2 ** (10 + 10 + 4)  # 16.0 MiB
MAX_GRPC_SERVER_THREADS = 16
INSECURE_HOST = "localhost"
INSECURE_PORT = 50001

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
CACHE_EXPIRE = "600"

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "wc_doc_cache"
MONGO_COLLECTION = "wc_doc_collection"
MONGO_TTL = 3600
