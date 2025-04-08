import os
import pickle


class LoadModel:
    LABELS = ['Bukan JUDOL', 'JUDOL']

    def __init__(self, model_path: str):
        assert os.path.exists(model_path), f'Model not found: {model_path}'

        with open(model_path, 'rb') as f:
            binary = pickle.load(f)
            self.model = binary['model']
            self.version = binary['version']

    def predict(self, texts: list[str]) -> list[str]:
        return [self.LABELS[pred] for pred in self.model.predict(texts).tolist()]

    def predict_int(self, texts: list[str]) -> list[int]:
        return self.model.predict(texts).tolist()
