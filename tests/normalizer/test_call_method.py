import pytest
from anti_judol.normalizer import TextNormalizer


class TestCallMethod:
    def test_call_method(self, normalizer):
        result = normalizer('test text')
        assert isinstance(result, str)

        direct_result = normalizer.normalize('test text')
        assert result == direct_result

    def test_call_method_invalid_type(self, normalizer):
        with pytest.raises(AssertionError):
            normalizer(123)

    def test_call_method_empty_string(self, normalizer):
        result = normalizer('')
        assert result == ''
