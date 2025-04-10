import pytest
from anti_judol.normalizer import TextNormalizer

@pytest.fixture
def normalizer():
    return TextNormalizer()
