from io import BytesIO
import hashlib
from unittest.mock import Mock
import pytest
from ml.download_sentiment import download_file


def test_download_integrity_and_reuse(tmp_path, monkeypatch):
    content = b'test fixture, not a model'
    urlopen = Mock(return_value=BytesIO(content))
    monkeypatch.setattr('ml.download_sentiment.urllib.request.urlopen', urlopen)
    target = tmp_path / 'weights.bin'
    download_file('https://example.test/fixture', target, len(content), hashlib.sha256(content).hexdigest())
    assert target.read_bytes() == content
    download_file('https://example.test/fixture', target, len(content), hashlib.sha256(content).hexdigest())
    assert urlopen.call_count == 1


def test_reject_corrupted_weights(tmp_path, monkeypatch):
    monkeypatch.setattr('ml.download_sentiment.urllib.request.urlopen', lambda *args, **kwargs: BytesIO(b'corrupt'))
    with pytest.raises(ValueError, match='Integrity'):
        download_file('https://example.test/fixture', tmp_path / 'weights.bin', 7, '0' * 64)
