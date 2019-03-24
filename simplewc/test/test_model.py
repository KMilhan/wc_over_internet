from collections import Counter
from pathlib import Path

from simplewc.model import tokenize_html_to_words, retrieve_html, \
    HTMLDocumentModel

here = Path(__file__).absolute().parent


def test_tokenize_html_to_words():
    """Test tokenizing"""
    with open(here / 'virtusize.html.bytes', 'rb') as f:
        """testfile has 993 tokens"""
        assert len(list(tokenize_html_to_words(f.read()))) == 993

    assert list(tokenize_html_to_words('some str')) == ['some', 'str']
    assert list(tokenize_html_to_words(b'some bytes')) == ['some', 'bytes']
    assert list(tokenize_html_to_words(b'some '
                                       b'\xed\x95\x9c\xea\xb5\xad\xec\x96\xb4'
                                       )) == ['some', '한국어']

    assert list(tokenize_html_to_words('fit.</p>')) == ['fit']
    assert list(tokenize_html_to_words('fit</p>')) == ['fit']
    assert list(tokenize_html_to_words('FIT!</p>')) == ['fit']


def test_get():
    """Test web access"""
    assert retrieve_html('https://virtusize.jp')


def test_creation(mock_doc_storage, mock_query_cache):
    assert HTMLDocumentModel('https://virtusize.jp',
                             mock_doc_storage,
                             mock_query_cache
                             ) is not None


def test_mock_query_cache_creation(mock_doc_storage, mock_query_cache):
    model = HTMLDocumentModel('https://virtusize.jp',
                              mock_doc_storage,
                              mock_query_cache
                              )

    fit_query = model.count_word('fit')
    assert fit_query is not None
    assert isinstance(fit_query, int)
    assert model.query_cache.mock_cache[
               ('https://virtusize.jp', 'fit')] == fit_query


def test_mock_document_storage_creation(mock_doc_storage, mock_query_cache):
    model = HTMLDocumentModel('https://virtusize.jp',
                              mock_doc_storage,
                              mock_query_cache
                              )
    model.count_word('fit')
    assert mock_doc_storage.mock_db['https://virtusize.jp']


def test_query(mock_doc_storage, mock_query_cache):
    with open(here / 'virtusize.html.bytes', 'rb') as f:
        """Ground truth counter"""
        gtc = Counter(tokenize_html_to_words(f.read()))

    model = HTMLDocumentModel('https://virtusize.jp',
                              mock_doc_storage,
                              mock_query_cache
                              )
    with open(here / 'virtusize.html.bytes', 'rb') as f:
        """Monkey patch `get_html` method to read local file"""

        model.get_html = lambda x: bytes(f.read())
        assert model.count_word('fit') == gtc['fit']
        assert model.count_word('DOES_NOT_EXIST_STRING') == gtc[
            'DOES_NOT_EXIST_STRING']
