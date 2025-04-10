import pytest
from anti_judol.normalizer import TextNormalizer


class TestSanitize:
    def test_sanitize_basic(self, normalizer):
        result = normalizer.sanitize('Hello, World!')
        assert isinstance(result, str)
        assert result == 'hello world'

    def test_sanitize_empty_string(self, normalizer):
        result = normalizer.sanitize('')
        assert result == ''

    def test_sanitize_whitespace_only(self, normalizer):
        result = normalizer.sanitize('   ')
        assert result == ''

    def test_sanitize_with_special_chars(self, normalizer):
        result = normalizer.sanitize('Hello ᆢ【】World!')
        assert 'ᆢ' not in result
        assert '【' not in result
        assert '】' not in result
        assert result == 'hello world'

    def test_sanitize_with_exception(self, normalizer, mocker):
        mocker.patch('anti_judol.normalizer.merge_words', side_effect=Exception('Test error'))
        result = normalizer.sanitize('test text')
        assert result == ''
