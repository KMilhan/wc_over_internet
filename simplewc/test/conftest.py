import pytest

from simplewc.storage import MockDocumentStorage, MockQueryCache


@pytest.fixture(scope="function")
def mock_doc_storage():
    yield MockDocumentStorage('')


@pytest.fixture(scope="function")
def mock_query_cache():
    yield MockQueryCache('')
