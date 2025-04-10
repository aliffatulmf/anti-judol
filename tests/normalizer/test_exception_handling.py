import pytest
from anti_judol.normalizer import TextNormalizer


class TestExceptionHandling:
    def test_init_import_error(self, mocker):
        mocker.patch('anti_judol.normalizer.Lemmatizer', side_effect=ImportError('Test import error'))

        with pytest.raises(ImportError) as excinfo:
            TextNormalizer()
        assert 'Failed to initialize nlp_id' in str(excinfo.value)

    def test_init_general_exception(self, mocker):
        mocker.patch('anti_judol.normalizer.Lemmatizer', side_effect=Exception('Test general error'))

        with pytest.raises(RuntimeError) as excinfo:
            TextNormalizer()
        assert 'Initialization failed' in str(excinfo.value)

    def test_remove_stopwords_empty_string(self, normalizer):
        result = normalizer.remove_stopwords('')
        assert result == ''

    def test_remove_stopwords_with_exception(self, normalizer, mocker):
        mocker.patch.object(normalizer, 'stopwords', side_effect=KeyError('Test error'))

        result = normalizer.remove_stopwords('test text')
        assert result == 'test text'

    def test_remove_stopwords_with_split_exception(self, normalizer, mocker):
        # Create a custom string class that raises an exception when split is called
        class CustomString(str):
            def split(self, *args, **kwargs):
                raise Exception('Test error')

        # Create an instance of our custom string class
        text = CustomString('test text')

        # Mock the logger.error to verify it's called
        mock_logger = mocker.patch('anti_judol.normalizer.logger.error')

        # The method should catch the exception and return the original text
        result = normalizer.remove_stopwords(text)
        assert result == text

        # Verify that logger.error was called
        mock_logger.assert_called_once()

    def test_normalize_empty_after_sanitize(self, normalizer, mocker):
        mocker.patch.object(normalizer, 'sanitize', return_value='')

        result = normalizer.normalize('test text')
        assert result == ''

    def test_normalize_empty_after_lemmatize(self, normalizer, mocker):
        mocker.patch.object(normalizer, 'sanitize', return_value='test text')
        mocker.patch.object(normalizer, 'lemmatize', return_value='')

        result = normalizer.normalize('test text')
        assert result == ''

    def test_normalize_empty_after_remove_stopwords(self, normalizer, mocker):
        mocker.patch.object(normalizer, 'sanitize', return_value='test text')
        mocker.patch.object(normalizer, 'lemmatize', return_value='test text')
        mocker.patch.object(normalizer, 'remove_stopwords', return_value='')

        result = normalizer.normalize('test text')
        assert result == ''

    def test_normalize_exception(self, normalizer, mocker):
        mocker.patch.object(normalizer, 'sanitize', side_effect=Exception('Test error'))

        result = normalizer.normalize('test text')
        assert result == ''
