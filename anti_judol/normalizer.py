import re
import logging
from typing import List, Set
from functools import lru_cache

import pandas as pd
from unidecode import unidecode
from nlp_id.lemmatizer import Lemmatizer
from nlp_id.stopword import StopWord


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def merge_words(text: str) -> str:
    assert isinstance(text, str), 'Input must be string'

    tokens = text.split()
    buffer = []
    result = []
    for token in tokens:
        if len(token) == 1:
            buffer.append(token)
        else:
            if buffer:
                result.append(''.join(buffer))
                buffer = []
            result.append(token)
    if buffer:
        result.append(''.join(buffer))
    return ' '.join(result)

class TextNormalizer:
    CHARS_TO_REMOVE: str = 'ᆢ【】'

    PUNCT_PATTERN: str = r'[^\w\s]'
    SPACE_PATTERN: str = r'\s+'
    INNER_PUNCT_PATTERN: str = r'(?<=\w)([^\w\s]+)(?=\w)'

    def __init__(self) -> None:
        self.translation_table: dict = str.maketrans('', '', self.CHARS_TO_REMOVE)
        self._lemma_cache: dict = {}

        try:
            self.lemmatizer = Lemmatizer()
            self.stopword = StopWord()
            self.stopwords: Set[str] = set(self.stopword.get_stopword())
        except ImportError as e:
            logger.error(f'Missing dependency: {e}')
            raise ImportError('Failed to initialize nlp_id')
        except Exception as e:
            logger.error(f'Failed to initialize TextNormalizer: {e}')
            raise RuntimeError(f'Initialization failed: {e}')

    @lru_cache(maxsize=10000)
    def lemmatize(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            if not text:
                return ''

            tokens: List[str] = text.split()
            lemmatized_tokens: List[str] = []

            for token in tokens:
                lemma = self.lemmatizer.lemmatize(token)
                lemmatized_tokens.append(lemma)

            return ' '.join(lemmatized_tokens)

        except Exception as e:
            logger.error(f'Error in lemmatization: {e}')
            return text

    def remove_stopwords(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            if not text:
                return ''

            tokens: List[str] = text.split()
            filtered: List[str] = [
                word for word in tokens
                if word.lower() not in self.stopwords
            ]
            return ' '.join(filtered)

        except Exception as e:
            logger.error(f'Error removing stopwords: {e}')
            return text

    def _smart_inner_punct(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            return re.sub(self.INNER_PUNCT_PATTERN, ' ', text)
        except Exception as e:
            logger.error(f'Error in smart punctuation: {e}')
            return text

    def sanitize(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'

        try:
            text = text.lower()
            text = unidecode(text)
            text = self._smart_inner_punct(text)
            text = re.sub(self.PUNCT_PATTERN, ' ', text)
            text = re.sub(self.SPACE_PATTERN, ' ', text)

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
            text = text.translate(self.translation_table)
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

            text = merge_words(text)

            return text.strip()
        except Exception as e:
            logger.error(f'Error in normalization: {e}')
            return ''

    def normalize_series(self, texts: pd.Series) -> pd.Series:
        assert isinstance(texts, pd.Series), 'Input must be pandas Series'

        try:
            texts = texts.fillna('')
            return texts.apply(lambda x: self.normalize(x) if x else '')
        except Exception as e:
            logger.error(f'Error in series normalization: {e}')
            return pd.Series([''] * len(texts))

    def batch_normalize(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[str]:
        assert isinstance(texts, list), 'Input must be list'
        assert isinstance(batch_size, int) and batch_size > 0, 'Batch size must be a positive integer'

        try:
            results: List[str] = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                normalized = [self.normalize(text) for text in batch]
                results.extend(normalized)
            return results

        except Exception as e:
            logger.error(f'Error in batch normalization: {e}')
            return [''] * len(texts)

    def __call__(self, text: str) -> str:
        assert isinstance(text, str), 'Input must be string'
        return self.normalize(text)
