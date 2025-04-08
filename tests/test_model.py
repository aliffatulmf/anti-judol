import os
import pickle
import pytest
import numpy as np
from unittest.mock import patch, mock_open

from anti_judol.model import LoadModel


class MockModel:
    def __init__(self, predictions=None):
        self.predictions = predictions if predictions is not None else [1, 0, 1]

    def predict(self, texts):
        # Return numpy array to simulate scikit-learn model behavior
        return np.array(self.predictions[:len(texts)] if texts else [])


class TestLoadModel:
    @pytest.fixture
    def mock_model_file(self):
        # Create a mock model that returns numpy arrays
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}

        # Create a mock pickle.load that returns our mock model
        with patch('pickle.load', return_value=mock_data):
            yield mock_data

    @pytest.fixture
    def temp_model_path(self, tmp_path):
        # Create a temporary model file
        model_path = tmp_path / 'test_model.pkl'

        # Create a mock model that can be pickled
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}

        # Save the mock model to the file
        with open(model_path, 'wb') as f:
            pickle.dump(mock_data, f)

        yield model_path

        # Clean up
        if model_path.exists():
            os.unlink(model_path)

    def test_init_with_valid_path(self, temp_model_path):
        # Test initialization with a valid model path
        model_loader = LoadModel(str(temp_model_path))

        # Verify that the model was loaded
        assert model_loader.model is not None
        assert model_loader.version == '1.0.0'

    def test_init_with_invalid_path(self):
        # Test initialization with an invalid model path
        with pytest.raises(AssertionError, match='Model not found'):
            LoadModel('non_existent_model.pkl')

    def test_predict(self):
        # Mock os.path.exists to return True
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()), \
             patch('pickle.load', return_value=mock_data):

            # Initialize the model loader
            model_loader = LoadModel('fake_model.pkl')

            # Test the predict method
            texts = ['sample text 1', 'sample text 2', 'sample text 3']
            predictions = model_loader.predict(texts)

            # Verify the predictions
            assert predictions == ['JUDOL', 'Bukan JUDOL', 'JUDOL']
            assert isinstance(predictions, list)
            assert all(isinstance(pred, str) for pred in predictions)

    def test_predict_empty_list(self):
        # Mock os.path.exists to return True
        mock_model = MockModel()
        mock_data = {'model': mock_model, 'version': '1.0.0'}
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()), \
             patch('pickle.load', return_value=mock_data):

            # Initialize the model loader
            model_loader = LoadModel('fake_model.pkl')

            # Test the predict method with an empty list
            predictions = model_loader.predict([])

            # Verify the predictions
            assert predictions == []
            assert isinstance(predictions, list)
