import json
import logging
import threading
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any
import joblib
from ..config import settings

logger = logging.getLogger(__name__)


class ModelService:
    """Load only trusted local artifacts created by this project's training CLI."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._models: dict[str, tuple[float, Any]] = {}

    def predict(self, task: str, text: str) -> dict:
        path = settings.model_dir / task / 'model.joblib'
        if not path.exists():
            return {'status': 'untrained', 'label': None, 'confidence': None,
                    'message': f'No trained {task} model. Follow the training guide.'}
        try:
            with self._lock:
                stamp = path.stat().st_mtime
                if task not in self._models or self._models[task][0] != stamp:
                    self._models[task] = (stamp, joblib.load(path))
                model = self._models[task][1]
                probabilities = model.predict_proba([text])[0]
                idx = int(probabilities.argmax())
                confidence = float(probabilities[idx])
                label = str(model.classes_[idx])
            return {'status': 'ready', 'label': label, 'confidence': confidence,
                    'needs_review': confidence < settings.inference_threshold,
                    'model_version': datetime.fromtimestamp(stamp, timezone.utc).isoformat()}
        except Exception:
            logger.exception('Model inference failed for %s', task)
            return {'status': 'error', 'label': None, 'confidence': None,
                    'message': 'Model artifact could not be loaded. Check version compatibility and retrain.'}

    def report(self, task: str) -> dict:
        path = settings.model_dir / task / 'evaluation.json'
        if not path.exists():
            return {'task': task, 'status': 'untrained', 'metrics': None}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            return {'task': task, 'status': 'error', 'metrics': None}


models = ModelService()


class SentimentService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tokenizer = None
        self._model = None

    def predict(self, text: str) -> dict:
        if not settings.sentiment_enabled:
            return {'status': 'disabled', 'label': None, 'confidence': None}
        if not (settings.sentiment_dir / 'config.json').exists():
            return {'status': 'not_downloaded', 'label': None, 'confidence': None,
                    'message': 'Run python -m ml.download_sentiment to enable local sentiment analysis.'}
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            with self._lock:
                if self._model is None:
                    self._tokenizer = AutoTokenizer.from_pretrained(settings.sentiment_dir, local_files_only=True)
                    self._model = AutoModelForSequenceClassification.from_pretrained(settings.sentiment_dir, local_files_only=True)
                    self._model.eval()
                    torch.set_num_threads(min(4, torch.get_num_threads()))
                cleaned = ' '.join('@user' if t.startswith('@') else 'http' if t.startswith('http') else t for t in text.split())
                tokens = self._tokenizer(cleaned, return_tensors='pt', truncation=True, max_length=512)
                with torch.inference_mode():
                    scores = torch.softmax(self._model(**tokens).logits[0], dim=-1)
                idx = int(scores.argmax())
                label = self._model.config.id2label[idx].lower()
                return {'status': 'ready', 'label': label, 'confidence': float(scores[idx]),
                        'model': settings.sentiment_model, 'truncated': len(self._tokenizer.encode(cleaned)) > 512}
        except Exception:
            logger.exception('Sentiment inference failed')
            return {'status': 'unavailable', 'label': None, 'confidence': None,
                    'message': 'Install sentiment dependencies and verify the local model download.'}


sentiment = SentimentService()
