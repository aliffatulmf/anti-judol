import os
import pickle


class LoadModel:
    LABELS = ['Bukan JUDOL', 'JUDOL']

    def __init__(self, model_path: str, normalize: bool = True):
        assert os.path.exists(model_path), f'Model not found: {model_path}'

        with open(model_path, 'rb') as f:
            binary = pickle.load(f)
            self.model = binary['model']
            self.version = binary['version']

        if normalize:
            from anti_judol.normalizer import TextNormalizer
            self.normalizer = TextNormalizer()

    def predict(self, texts: list[str]) -> list[str]:
        texts = [self.normalizer(text) for text in texts]
        return [self.LABELS[pred] for pred in self.model.predict(texts).tolist()]

    def predict_int(self, texts: list[str]) -> list[int]:
        texts = [self.normalizer(text) for text in texts]
        return self.model.predict(texts).tolist()
