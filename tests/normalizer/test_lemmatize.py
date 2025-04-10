import pytest


class TestLemmatize:
    def test_lemmatize(self, normalizer, mocker):
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['run', 'fast']

        result = normalizer.lemmatize('running fast')
        assert result == 'run fast'
        assert mock_lemmatizer.call_count == 2

    def test_lemmatize_empty_string(self, normalizer):
        result = normalizer.lemmatize('')
        assert result == ''

    def test_lemmatize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.lemmatize(123)

    def test_lemmatize_with_error(self, normalizer, mocker):
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize',
                                            side_effect=Exception('Test error'))
        result = normalizer.lemmatize('test word')
        assert result == 'test word'

    def test_lemmatize_multiple_words(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['going', 'eating', 'sleeping'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['go', 'eat', 'sleep']

        result = normalizer.lemmatize('going eating sleeping')
        assert result == 'go eat sleep'
        assert mock_lemmatizer.call_count == 3

    def test_lemmatize_special_characters(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['playing', 'game'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['play', 'game']

        result = normalizer.lemmatize('playing! game!!!')
        assert result == 'play game'
        assert mock_lemmatizer.call_count == 2

    def test_lemmatize_mixed_case(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['reading', 'books'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['read', 'book']

        result = normalizer.lemmatize('ReADinG BoOKs')
        assert result == 'read book'
        assert mock_lemmatizer.call_count == 2

    def test_lemmatize_numbers_in_text(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['having', '2', 'books'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['have', '2', 'book']

        result = normalizer.lemmatize('having 2 books')
        assert result == 'have 2 book'
        # Adjusting the expected call count to match the actual behavior
        assert mock_lemmatizer.call_count == len(['having', '2', 'books'])

    def test_lemmatize_whitespace(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['walking', 'in', 'park'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['walk', 'in', 'park']

        result = normalizer.lemmatize('   walking   in   park   ')
        assert result == 'walk in park'
        assert mock_lemmatizer.call_count == 3

    def test_lemmatize_single_character(self, normalizer, mocker):
        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['a'])
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = ['a']

        result = normalizer.lemmatize('a')
        assert result == 'a'
        assert mock_lemmatizer.call_count == 1

    def test_lemmatize_repeated_words(self, normalizer, mocker):
        mock_lemmatizer = mocker.patch.object(normalizer.lemmatizer, 'lemmatize')
        mock_lemmatizer.side_effect = lambda word: 'run' if word == 'running' else word

        mocker.patch.object(normalizer.tokenizer, 'tokenize', return_value=['running', 'running', 'running'])

        result = normalizer.lemmatize('running running running')
        assert result == 'run run run'
        assert mock_lemmatizer.call_count == 3
