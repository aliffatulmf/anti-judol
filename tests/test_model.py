import os
import pickle
import pytest
import numpy as np

from anti_judol.model import LoadModel


class MockModel:
    def __init__(self, predictions=None):
        self.predictions = predictions if predictions is not None else [1, 0, 1]

    def predict(self, texts):
        return np.array(self.predictions[:len(texts)] if texts else [])


class TestLoadModel:
    @pytest.fixture
    def mock_model_file(self, mocker):
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}
        mocker.patch('pickle.load', return_value=mock_data)
        return mock_data

    @pytest.fixture
    def temp_model_path(self, tmp_path):
        model_path = tmp_path / 'test_model.pkl'
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}

        with open(model_path, 'wb') as f:
            pickle.dump(mock_data, f)

        yield model_path

        if model_path.exists():
            os.unlink(model_path)

    def test_init_with_valid_path(self, temp_model_path):
        model_loader = LoadModel(str(temp_model_path), normalize=False)
        assert model_loader.model is not None
        assert model_loader.version == '1.0.0'

    def test_init_with_invalid_path(self):
        with pytest.raises(AssertionError, match='Model not found'):
            LoadModel('non_existent_model.pkl')

    @pytest.fixture
    def mock_nlp_id(self, mocker):
        mock_lemmatizer = mocker.patch('anti_judol.normalizer.Lemmatizer')
        mock_lemmatizer_instance = mocker.MagicMock()
        mock_lemmatizer.return_value = mock_lemmatizer_instance
        mock_lemmatizer_instance.lemmatize.side_effect = lambda word: word

        mock_stopword = mocker.patch('anti_judol.normalizer.StopWord')
        mock_stopword_instance = mocker.MagicMock()
        mock_stopword.return_value = mock_stopword_instance
        mock_stopword_instance.get_stopword.return_value = ['ini', 'adalah', 'dan', 'yang']

        return {}

    @pytest.fixture
    def mock_text_normalizer(self, mocker):
        mock_normalizer = mocker.MagicMock()
        mock_normalizer.__call__ = lambda _, text: text
        return mock_normalizer

    def test_predict(self, mocker):
        mock_model = MockModel()
        mock_model.predict = mocker.MagicMock(side_effect=mock_model.predict)
        mock_data = {'model': mock_model, 'version': '1.0.0'}
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('anti_judol.normalizer.TextNormalizer', return_value=mocker.MagicMock())
        mock_open = mocker.patch('builtins.open', mocker.mock_open())
        mocker.patch('pickle.load', return_value=mock_data)

        model_loader = LoadModel('fake_model.pkl')
        texts = ['sample text 1', 'sample text 2', 'sample text 3']
        predictions = model_loader.predict(texts)

        assert predictions == ['JUDOL', 'Bukan JUDOL', 'JUDOL']
        assert isinstance(predictions, list)
        assert all(isinstance(pred, str) for pred in predictions)
        mock_model.predict.assert_called_once()

    def test_predict_empty_list(self, mocker):
        mock_model = MockModel()
        mock_model.predict = mocker.MagicMock(side_effect=mock_model.predict)
        mock_data = {'model': mock_model, 'version': '1.0.0'}
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('anti_judol.normalizer.TextNormalizer', return_value=mocker.MagicMock())
        mock_open = mocker.patch('builtins.open', mocker.mock_open())
        mocker.patch('pickle.load', return_value=mock_data)

        model_loader = LoadModel('fake_model.pkl')
        predictions = model_loader.predict([])

        assert predictions == []
        assert isinstance(predictions, list)
        mock_model.predict.assert_called_once_with([])
