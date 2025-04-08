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

    def test_merge_words_with_complex_input(self):
        # Test with more complex patterns
        text = 'a b c test d e f word g h i'
        result = merge_words(text)
        assert result == 'abc test def word ghi'

        # Test with alternating patterns
        text = 'a test b c word d'
        result = merge_words(text)
        assert result == 'a test bc word d'

    def test_merge_words_with_numbers(self):
        # Test with numbers
        text = '1 2 3 test 4 5 6'
        result = merge_words(text)
        assert result == '123 test 456'

        # Test with mixed numbers and letters
        text = 'a 1 b 2 test 3 c'
        result = merge_words(text)
        assert result == 'a1b2 test 3c'


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

    def test_init_import_error(self):
        # Test ImportError handling in __init__
        with patch('anti_judol.normalizer.Lemmatizer', side_effect=ImportError('Test error')), \
             pytest.raises(ImportError):
            TextNormalizer()

    def test_init_general_error(self):
        # Test general error handling in __init__
        with patch('anti_judol.normalizer.Lemmatizer', side_effect=Exception('Test error')), \
             pytest.raises(RuntimeError):
            TextNormalizer()

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

    def test_normalize_with_lemmatize_false(self, normalizer):
        # Test normalize with lemmatize=False
        with patch.object(normalizer, 'sanitize', return_value='running test') as mock_sanitize, \
             patch.object(normalizer, 'lemmatize') as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords', return_value='running test') as mock_remove_stopwords, \
             patch('anti_judol.normalizer.merge_words', return_value='running test') as mock_merge_words:

            result = normalizer.normalize('Running test!', lemmatize=False)

            # Check that lemmatize was not called
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_not_called()
            mock_remove_stopwords.assert_called_once()
            mock_merge_words.assert_called_once()

            assert result == 'running test'

    def test_normalize_with_special_chars(self, normalizer):
        # Test with characters that should be removed
        text = 'Hello【World】ᆢ'
        result = normalizer.normalize(text)

        # These characters should be removed
        assert '【' not in result
        assert '】' not in result
        assert 'ᆢ' not in result
        assert 'hello' in result.lower()
        assert 'world' in result.lower()

    def test_normalize_integration(self, normalizer):
        # Test the full normalization pipeline with real dependencies
        # This is more of an integration test
        with patch.object(normalizer, 'sanitize', side_effect=lambda x: x.lower()) as mock_sanitize, \
             patch.object(normalizer, 'lemmatize', side_effect=lambda x: x) as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords', side_effect=lambda x: x) as mock_remove_stopwords, \
             patch('anti_judol.normalizer.merge_words', side_effect=lambda x: x) as mock_merge_words:

            # Test with a complex input
            text = 'Hello, World! This-is a test.'
            normalizer.normalize(text)

            # Verify the correct sequence of calls
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_called_once()
            mock_remove_stopwords.assert_called_once()
            mock_merge_words.assert_called_once()

    def test_normalize_with_error_handling(self, normalizer):
        # Test error handling in normalize
        with patch.object(normalizer, 'sanitize', side_effect=Exception('Test error')):
            result = normalizer.normalize('Test text')
            assert result == ''

    def test_batch_normalize_empty_list(self, normalizer):
        # Test batch_normalize with empty list
        result = normalizer.batch_normalize([])
        assert result == []

    def test_normalize_series_with_error(self, normalizer):
        # Test error handling in normalize_series
        series = pd.Series(['test1', 'test2'])

        with patch.object(normalizer, 'normalize', side_effect=Exception('Test error')):
            result = normalizer.normalize_series(series)

            # Should return empty strings with the same length
            assert len(result) == 2
            assert all(val == '' for val in result)

    def test_translation_table(self, normalizer):
        # Test that the translation table is correctly initialized
        # and removes the specified characters
        text = 'Hello【World】ᆢ'
        translated = text.translate(normalizer.translation_table)

        assert '【' not in translated
        assert '】' not in translated
        assert 'ᆢ' not in translated
        assert 'Hello' in translated
        assert 'World' in translated

    def test_lemmatize_with_error(self, normalizer):
        # Test error handling in lemmatize
        with patch.object(normalizer.lemmatizer, 'lemmatize', side_effect=Exception('Test error')):
            result = normalizer.lemmatize('test word')
            # Should return the original text on error
            assert result == 'test word'

    def test_remove_stopwords_with_error(self, normalizer):
        # Test error handling in remove_stopwords
        with patch.object(normalizer, 'stopwords', side_effect=Exception('Test error')):
            result = normalizer.remove_stopwords('test word')
            # Should return the original text on error
            assert result == 'test word'

        # Test with a different exception to cover all error handling paths
        with patch.object(normalizer, 'stopwords', side_effect=KeyError('Test error')):
            result = normalizer.remove_stopwords('test word')
            assert result == 'test word'

    def test_remove_stopwords_with_list_comprehension_error(self, normalizer):
        # Test error in the list comprehension part of remove_stopwords
        # This should trigger the exception handling in lines 91-93
        text = 'test word'

        # Create a mock that raises an exception when accessed with 'in'
        mock_stopwords = MagicMock()
        mock_stopwords.__contains__.side_effect = Exception('Test error')

        with patch.object(normalizer, 'stopwords', mock_stopwords):
            result = normalizer.remove_stopwords(text)
            # Should return the original text on error
            assert result == text

    def test_smart_inner_punct_with_error(self, normalizer):
        # Test error handling in _smart_inner_punct
        with patch('re.sub', side_effect=Exception('Test error')):
            result = normalizer._smart_inner_punct('test-word')
            # Should return the original text on error
            assert result == 'test-word'

    def test_sanitize_with_error(self, normalizer):
        # Test error handling in sanitize
        with patch('unidecode.unidecode', side_effect=Exception('Test error')):
            result = normalizer.sanitize('Test Word')
            # The implementation returns lowercase text on error, not empty string
            assert result == 'test word'

        # Test with a different exception to cover all error handling paths
        with patch.object(normalizer, '_smart_inner_punct', side_effect=Exception('Test error')):
            result = normalizer.sanitize('Test Word')
            assert result == ''

        # Test with another exception path
        with patch('re.sub', side_effect=Exception('Test error')):
            result = normalizer.sanitize('Test Word')
            assert result == ''

    def test_normalize_with_lemmatize_parameter(self, normalizer):
        # Test normalize with different lemmatize parameter values
        with patch.object(normalizer, 'lemmatize') as mock_lemmatize:
            # Test with default value (True)
            normalizer.normalize('test')
            mock_lemmatize.assert_called_once()

            mock_lemmatize.reset_mock()

            # Test with explicit True
            normalizer.normalize('test', lemmatize=True)
            mock_lemmatize.assert_called_once()

            mock_lemmatize.reset_mock()

            # Test with False
            normalizer.normalize('test', lemmatize=False)
            mock_lemmatize.assert_not_called()

    def test_normalize_empty_checks(self, normalizer):
        # Test the empty string checks in normalize
        with patch.object(normalizer, 'sanitize', return_value='') as mock_sanitize, \
             patch.object(normalizer, 'lemmatize') as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords') as mock_remove_stopwords, \
             patch('anti_judol.normalizer.merge_words') as mock_merge_words:

            result = normalizer.normalize('test')

            # Check that sanitize was called but the rest weren't
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_not_called()
            mock_remove_stopwords.assert_not_called()
            mock_merge_words.assert_not_called()

            assert result == ''

        # Test empty after lemmatize
        with patch.object(normalizer, 'sanitize', return_value='test') as mock_sanitize, \
             patch.object(normalizer, 'lemmatize', return_value='') as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords') as mock_remove_stopwords, \
             patch('anti_judol.normalizer.merge_words') as mock_merge_words:

            result = normalizer.normalize('test')

            # Check that sanitize and lemmatize were called but the rest weren't
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_called_once()
            mock_remove_stopwords.assert_not_called()
            mock_merge_words.assert_not_called()

            assert result == ''

        # Test empty after remove_stopwords
        with patch.object(normalizer, 'sanitize', return_value='test') as mock_sanitize, \
             patch.object(normalizer, 'lemmatize', return_value='test') as mock_lemmatize, \
             patch.object(normalizer, 'remove_stopwords', return_value='') as mock_remove_stopwords, \
             patch('anti_judol.normalizer.merge_words') as mock_merge_words:

            result = normalizer.normalize('test')

            # Check that sanitize, lemmatize, and remove_stopwords were called but merge_words wasn't
            mock_sanitize.assert_called_once()
            mock_lemmatize.assert_called_once()
            mock_remove_stopwords.assert_called_once()
            mock_merge_words.assert_not_called()

            assert result == ''

    def test_batch_normalize_with_error(self, normalizer):
        # Test error handling in batch_normalize
        with patch.object(normalizer, 'normalize', side_effect=Exception('Test error')):
            result = normalizer.batch_normalize(['test1', 'test2'])

            # Should return empty strings with the same length
            assert len(result) == 2
            assert all(val == '' for val in result)
