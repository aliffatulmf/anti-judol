import pytest
from anti_judol.normalizer import merge_words

class TestMergeWords:
    def test_merge_words_with_valid_input(self):
        text = 'a b c test word'
        result = merge_words(text)
        assert result == 'abc test word'

        text = 'a b c'
        result = merge_words(text)
        assert result == 'abc'

        text = 'a b test c d word'
        result = merge_words(text)
        assert result == 'ab test cd word'

    def test_merge_words_with_empty_string(self):
        result = merge_words('')
        assert result == ''

    def test_merge_words_with_invalid_type(self):
        with pytest.raises(AssertionError):
            merge_words(123)  # type: ignore

    def test_merge_words_with_complex_input(self):
        text = 'a b c test d e f word g h i'
        result = merge_words(text)
        assert result == 'abc test def word ghi'

        text = 'a test b c word d'
        result = merge_words(text)
        assert result == 'a test bc word d'

    def test_merge_words_with_numbers(self):
        text = '1 2 3 test 4 5 6'
        result = merge_words(text)
        assert result == '123 test 456'

        text = 'a 1 b 2 test 3 c'
        result = merge_words(text)
        assert result == 'a1b2 test 3c'
