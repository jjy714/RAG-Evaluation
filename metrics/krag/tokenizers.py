# krag/tokenizer.py

from kiwipiepy import Kiwi

class KiwiTokenizer:
    def __init__(self, model_type: str = 'sbg', typos: str = None):
        self.kiwi = Kiwi(model_type=model_type, typos=typos)

    def tokenize(self, text: str):
        return self.kiwi.tokenize(text)

