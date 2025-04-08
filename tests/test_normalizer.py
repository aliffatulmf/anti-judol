import pytest
import pandas as pd
from typing import Any
from unittest.mock import patch, MagicMock

from anti_judol.normalizer import merge_words, TextNormalizer


class TestMergeWords:
    def test_merge_words_with_valid_input(self):
        # Test with normal text
        text = 'a b c test word'
        result = merge_words(text)
        assert result == 'abc test word'

        # Test with single characters
        text = 'a b c'
        result = merge_words(text)
        assert result == 'abc'

        # Test with mixed content
        text = 'a b test c d word'
        result = merge_words(text)
        assert result == 'ab test cd word'

    def test_merge_words_with_empty_string(self):
        result = merge_words('')
        assert result == ''

    def test_merge_words_with_invalid_type(self):
        with pytest.raises(AssertionError):
            # Type: ignore untuk test case yang memang seharusnya gagal
            merge_words(123)  # type: ignore


class TestTextNormalizer:
    @pytest.fixture
    def mock_nlp_id(self):
        with patch('anti_judol.normalizer.Lemmatizer') as mock_lemmatizer, \
             patch('anti_judol.normalizer.StopWord') as mock_stopword:

            # Configure mocks
            mock_lemmatizer_instance = MagicMock()
            mock_lemmatizer.return_value = mock_lemmatizer_instance
            mock_lemmatizer_instance.lemmatize.side_effect = lambda word: word if word != 'running' else 'run'

            mock_stopword_instance = MagicMock()
            mock_stopword.return_value = mock_stopword_instance
            mock_stopword_instance.get_stopword.return_value = ['ini', 'adalah', 'dan', 'yang']

            yield {
                'lemmatizer': mock_lemmatizer,
                'lemmatizer_instance': mock_lemmatizer_instance,
                'stopword': mock_stopword,
                'stopword_instance': mock_stopword_instance
            }

    @pytest.fixture
    def normalizer(self, mock_nlp_id: Any) -> TextNormalizer:
        # mock_nlp_id digunakan untuk setup fixture
        # Parameter ini diperlukan agar fixture mock_nlp_id dijalankan terlebih dahulu
        return TextNormalizer()

    def test_init(self, mock_nlp_id):
        normalizer = TextNormalizer()

        # Check if the required classes were instantiated
        mock_nlp_id['lemmatizer'].assert_called_once()
        mock_nlp_id['stopword'].assert_called_once()

        # Check if stopwords were loaded
        mock_nlp_id['stopword_instance'].get_stopword.assert_called_once()

        # Check if the lemmatizer and stopword objects were created
        assert normalizer.lemmatizer is not None
        assert normalizer.stopword is not None

    def test_lemmatize(self, normalizer, mock_nlp_id):
        # Test lemmatization
        result = normalizer.lemmatize('running fast')
        assert result == 'run fast'

        # Verify lemmatizer was called for each token
        assert mock_nlp_id['lemmatizer_instance'].lemmatize.call_count == 2

    def test_lemmatize_empty_string(self, normalizer):
        result = normalizer.lemmatize('')
        assert result == ''

    def test_lemmatize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.lemmatize(123)

    def test_remove_stopwords(self, normalizer):
        # The stopwords are mocked as ['ini', 'adalah', 'dan', 'yang']
        text = 'ini adalah test dan yang penting'
        result = normalizer.remove_stopwords(text)
        assert result == 'test penting'

    def test_remove_stopwords_empty_string(self, normalizer):
        result = normalizer.remove_stopwords('')
        assert result == ''

    def test_remove_stopwords_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.remove_stopwords(123)

    def test_smart_inner_punct(self, normalizer):
        text = 'hello-world test.case'
        result = normalizer._smart_inner_punct(text)
        # The inner punctuation pattern replaces punctuation between words with spaces
        assert result == 'hello world test case'

    def test_smart_inner_punct_empty_string(self, normalizer):
        result = normalizer._smart_inner_punct('')
        assert result == ''

    def test_smart_inner_punct_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer._smart_inner_punct(123)

    def test_sanitize(self, normalizer):
        text = 'Hello, World! Test-Case.'
        result = normalizer.sanitize(text)
        assert 'hello' in result
        assert 'world' in result
        assert 'test' in result
        assert 'case' in result
        assert ',' not in result
        assert '!' not in result
        assert '-' not in result
        assert '.' not in result

    def test_sanitize_empty_string(self, normalizer):
        result = normalizer.sanitize('')
        assert result == ''

    def test_sanitize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.sanitize(123)

    def test_normalize(self, normalizer):
        # Mock the methods that normalize calls
        with patch.object(normalizer, 'sanitize', return_value='test dan important') as mock_sanitize, \
             patch.object(normalizer, 'lemmatize', return_value='test dan important') as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords', return_value='test important') as mock_remove_stopwords:

            result = normalizer.normalize('Test dan Important!')

            # Check if all methods were called
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_called_once()
            mock_remove_stopwords.assert_called_once()

            # Check the result
            assert result == 'test important'

    def test_normalize_empty_string(self, normalizer):
        result = normalizer.normalize('')
        assert result == ''

    def test_normalize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.normalize(123)

    def test_normalize_series(self, normalizer):
        # Create a test series
        series = pd.Series(['test dan important', 'another dan test', None])

        # Mock the normalize method
        with patch.object(normalizer, 'normalize', side_effect=['test important', 'another test', '']):
            result = normalizer.normalize_series(series)

            # Check if the result is a pandas Series
            assert isinstance(result, pd.Series)

            # Check the values
            assert result[0] == 'test important'
            assert result[1] == 'another test'
            assert result[2] == ''

    def test_normalize_series_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.normalize_series(['test', 'another'])

    def test_batch_normalize(self, normalizer):
        # Create a test list
        texts = ['test dan important', 'another dan test', '']

        # Mock the normalize method
        with patch.object(normalizer, 'normalize', side_effect=['test important', 'another test', '']):
            result = normalizer.batch_normalize(texts, batch_size=2)

            # Check if the result is a list
            assert isinstance(result, list)

            # Check the values
            assert result[0] == 'test important'
            assert result[1] == 'another test'
            assert result[2] == ''

    def test_batch_normalize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.batch_normalize('not a list')

        with pytest.raises(AssertionError):
            normalizer.batch_normalize(['test'], batch_size='not an int')

        with pytest.raises(AssertionError):
            normalizer.batch_normalize(['test'], batch_size=0)

    def test_call(self, normalizer):
        # Mock the normalize method
        with patch.object(normalizer, 'normalize', return_value='test important'):
            result = normalizer('test dan important')
            assert result == 'test important'

    def test_call_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer(123)
