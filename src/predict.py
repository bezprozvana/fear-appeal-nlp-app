import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import Config

class FearClassifier:
    def __init__(self, model_dir: str, max_length: int = 192):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.model.eval()

        self.max_length = max_length

    @torch.no_grad()
    def predict_proba(self, text: str) -> dict:
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length
        ).to(self.device)

        logits = self.model(**enc).logits
        probs = torch.softmax(logits, dim=1)[0].detach().cpu().numpy()

        return {"p0": float(probs[0]), "p1": float(probs[1])}

    def predict(self, text: str, threshold: float = 0.55) -> dict:
        probs = self.predict_proba(text)
        label = 1 if probs["p1"] >= threshold else 0
        return {"label": label, **probs}

if __name__ == "__main__":
    clf = FearClassifier(str(Config.MODEL_DIR), max_length=Config.MAX_LENGTH)
    t = "Люди, можливі обстріли. Не сидіть ще 5 хв – якщо прилетить, ви не встигнете зреагувати"
    print(clf.predict(t, threshold=Config.THRESHOLD))