import pytest
from anti_judol.normalizer import TextNormalizer


@pytest.fixture
def normalizer():
    return TextNormalizer()

class TestNormalize:
    def test_normalize_basic(self, normalizer):
        result = normalizer.normalize('test text')
        assert isinstance(result, str)
        assert result != ''
        assert result.islower()

    def test_normalize_empty_string(self, normalizer):
        result = normalizer.normalize('')
        assert result == ''

    def test_normalize_whitespace_only(self, normalizer):
        result = normalizer.normalize('   ')
        assert result == ''

    def test_normalize_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer.normalize(123)

    def test_normalize_with_lemmatize_false(self, normalizer):
        text = 'berjalan berlari'
        result_with_lemma = normalizer.normalize(text)
        result_without_lemma = normalizer.normalize(text, lemmatize=False)
        assert result_with_lemma != result_without_lemma

    def test_normalize_punctuation_removal(self, normalizer):
        text = 'Halo, dunia! Ini@adalah#test.'
        result = normalizer.normalize(text)
        assert ',' not in result
        assert '!' not in result
        assert '@' not in result
        assert '#' not in result
        assert '.' not in result

    def test_normalize_stopwords_removal(self, normalizer):
        text = 'ini adalah sebuah kalimat dengan banyak stopwords yang harus dihapus'
        result = normalizer.normalize(text)

        assert 'adalah' not in result
        assert 'sebuah' not in result
        assert 'dengan' not in result
        assert 'yang' not in result
        assert 'harus' not in result

        assert 'kalimat' in result
        assert 'stopwords' in result
        assert 'hapus' in result

    def test_normalize_case_conversion(self, normalizer):
        text = 'TeKs DengAn HURUF CamPuRan'
        result = normalizer.normalize(text)
        assert result == result.lower()
        assert 'teks' in result
        assert 'HURUF' not in result

    def test_normalize_special_characters(self, normalizer):
        text = 'teks dengan karakter ᆢ【】khusus'
        result = normalizer.normalize(text)

        assert 'ᆢ' not in result
        assert '【' not in result
        assert '】' not in result

        assert 'teks' in result
        assert 'karakter' in result
        assert 'khusus' in result
