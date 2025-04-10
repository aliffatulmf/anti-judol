import re
import logging
import string
from functools import lru_cache

from unidecode import unidecode
from nlp_id.lemmatizer import Lemmatizer
from nlp_id.stopword import StopWord
from nlp_id.tokenizer import Tokenizer


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_words(text: str) -> str:
    assert isinstance(text, str), 'Input must be string'

    tokens = text.split()
    result = []
    buffer = []

    for token in tokens:
        if len(token) == 1:
            buffer.append(token)
        else:
            if buffer:
                result.append(''.join(buffer))
                buffer.clear()
            result.append(token)

    if buffer:
        result.append(''.join(buffer))

    return ' '.join(result)

class TextNormalizer:
    CHARS_TO_REMOVE = 'ᆢ【】'

    def __init__(self) -> None:
        self.sym_table = str.maketrans({char: ' ' for char in self.CHARS_TO_REMOVE})
        self.punct_table = str.maketrans({char: ' ' for char in string.punctuation})

        try:
            self.lemmatizer = Lemmatizer()
            self.stopwords = set(StopWord().get_stopword())
            self.tokenizer = Tokenizer()
        except ImportError as e:
            logger.error(f'Missing dependency: {e}')
            raise ImportError('Failed to initialize nlp_id')
        except Exception as e:
            logger.error(f'Failed to initialize TextNormalizer: {e}')
            raise RuntimeError(f'Initialization failed: {e}')

    @lru_cache(maxsize=128)
    def lemmatize(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            if not text:
                return ''

            tokens = self.tokenizer.tokenize(text)
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

            return ' '.join(tokens)

        except Exception as e:
            logger.error(f'Error in lemmatization: {e}')
            return text

    def remove_stopwords(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            if not text:
                return ''

            tokens = text.split()
            tokens = [
                word for word in tokens
                if word.lower() not in self.stopwords
            ]
            return ' '.join(tokens)

        except Exception as e:
            logger.error(f'Error removing stopwords: {e}')
            return text

    def sanitize(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            if not text.strip():
                return ''

            text = text.translate(self.sym_table)
            text = unidecode(text).lower()
            text = text.translate(self.punct_table)
            text = re.sub(r'\s+', ' ', text)
            text = merge_words(text)

            return text.strip()
        except Exception as e:
            logger.error(f'Error in text cleaning: {e}')
            return ''

    def normalize(self, text: str, lemmatize: bool = True) -> str:
        assert isinstance(text, str), 'Input must be string'
        assert isinstance(lemmatize, bool), 'Lemmatize parameter must be boolean'

        if len(text.strip()) == 0:
            return ''

        try:
            text = self.sanitize(text)

            if not text:
                return ''

            if lemmatize:
                text = self.lemmatize(text)

            if not text:
                return ''

            text = self.remove_stopwords(text)

            if not text:
                return ''

            return text.strip()
        except Exception as e:
            logger.error(f'Error in normalization: {e}')
            return ''

    def __call__(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'
        return self.normalize(text)
