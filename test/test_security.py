import pytest

from simplewc.exceptions import AccessLocalURI, NotAllowedScheme
from simplewc.model import HTMLDocumentModel, raise_if_not_safe
from simplewc.storage import MockDocumentStorage, MockQueryCache

LINK_TO_VERY_BIG_RESOURCE = (
    "http://ftp.riken.jp/Linux/ubuntu-releases/18.04"
    ".2/ubuntu-18.04.2-desktop-amd64.iso"
)


def test_raise_if_local():
    with pytest.raises(NotAllowedScheme):
        raise_if_not_safe("ftp://google.com/index.html")

    with pytest.raises(NotAllowedScheme):
        raise_if_not_safe("file:///etc/resolv.conf.d/resolv.conf")

    with pytest.raises(AccessLocalURI):
        raise_if_not_safe("https://127.0.0.1/index.html")

    mock_doc_storage = MockDocumentStorage("")
    mock_query_cache = MockQueryCache("")

    with pytest.raises(NotAllowedScheme):
        HTMLDocumentModel(
            "ftp://google.com/index.html", mock_doc_storage, mock_query_cache
        )

    with pytest.raises(NotAllowedScheme):
        HTMLDocumentModel(
            "file:///etc/resolv.conf.d/resolv.conf",
            mock_doc_storage,
            mock_query_cache,
        )

    with pytest.raises(AccessLocalURI):
        HTMLDocumentModel(
            "https://127.0.0.1/index.html", mock_doc_storage, mock_query_cache
        )
