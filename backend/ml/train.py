import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import FeatureUnion, Pipeline
from .data import normalize


def pipeline() -> Pipeline:
    return Pipeline([
        ('features', FeatureUnion([
            ('word', TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=35000)),
            ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True, max_features=50000)),
        ])),
        ('classifier', LogisticRegression(C=2.0, class_weight='balanced', max_iter=1500, random_state=42)),
    ])


def train(task: str, data_dir: Path, model_dir: Path, reports_dir: Path) -> dict:
    provenance = json.loads((data_dir / 'provenance.json').read_text(encoding='utf-8'))
    train_frame, test_frame = (pd.read_csv(data_dir / f'{s}.csv') for s in ['train', 'test'])
    allowed = {'billing', 'technical', 'account', 'general'} if task == 'category' else {'low', 'medium', 'high'}
    for frame in [train_frame, test_frame]:
        if frame[['text', 'label']].isna().any().any() or set(frame.label) != allowed:
            raise ValueError('All expected classes and nonempty text are required in both splits.')
    if set(train_frame.text.map(normalize)) & set(test_frame.text.map(normalize)):
        raise ValueError('Normalized text overlap detected. Run data preparation first.')
    if task == 'priority' and (not {'group_id'}.issubset(train_frame.columns) or set(train_frame.group_id) & set(test_frame.group_id)):
        raise ValueError('Priority training requires disjoint customer/thread groups.')
    started = time.perf_counter()
    model = pipeline()
    model.fit(train_frame.text, train_frame.label)
    predicted = model.predict(test_frame.text)
    classes = sorted(allowed)
    precision, recall, f1, _ = precision_recall_fscore_support(test_frame.label, predicted, average='macro', zero_division=0)
    baseline = DummyClassifier(strategy='most_frequent').fit(np.zeros((len(train_frame), 1)), train_frame.label)
    baseline_accuracy = accuracy_score(test_frame.label, baseline.predict(np.zeros((len(test_frame), 1))))
    report = {'task': task, 'status': 'trained', 'trained_at': datetime.now(timezone.utc).isoformat(),
              'model': 'TF-IDF word + char n-grams / LogisticRegression',
              'metrics': {'accuracy': float(accuracy_score(test_frame.label, predicted)),
                          'precision_macro': float(precision), 'recall_macro': float(recall), 'f1_macro': float(f1)},
              'baseline_accuracy': float(baseline_accuracy), 'classes': classes,
              'confusion_matrix': confusion_matrix(test_frame.label, predicted, labels=classes).tolist(),
              'classification_report': classification_report(test_frame.label, predicted, output_dict=True, zero_division=0),
              'train_rows': len(train_frame), 'test_rows': len(test_frame),
              'train_distribution': train_frame.label.value_counts().to_dict(),
              'test_distribution': test_frame.label.value_counts().to_dict(),
              'duration_seconds': round(time.perf_counter() - started, 3),
              'seed': 42, 'python': platform.python_version(), 'sklearn': sklearn.__version__,
              'provenance': provenance,
              'data_sha256': {s: hashlib.sha256((data_dir / f'{s}.csv').read_bytes()).hexdigest() for s in ['train', 'test']},
              'limitations': ['No support-domain validation.', 'Exact normalized deduplication only; near-duplicate leakage may remain.',
                              'Hyperparameters fixed in advance; test split not used to select them.']}
    target = model_dir / task
    target.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    temporary = target / 'model.tmp'
    joblib.dump(model, temporary)
    os.replace(temporary, target / 'model.joblib')
    (target / 'evaluation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (reports_dir / f'{task}.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    pd.DataFrame(report['confusion_matrix'], index=classes, columns=classes).to_csv(reports_dir / f'{task}-confusion.csv')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=['category', 'priority'], required=True)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--model-dir', type=Path, default=Path('models'))
    parser.add_argument('--reports-dir', type=Path, default=Path('reports'))
    args = parser.parse_args()
    result = train(args.task, args.data_dir, args.model_dir, args.reports_dir)
    print(json.dumps({k: result[k] for k in ['task', 'metrics', 'train_rows', 'test_rows', 'duration_seconds']}, indent=2))
