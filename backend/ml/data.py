import re
import pandas as pd


def normalize(text: str) -> str:
    return re.sub(r'\W+', ' ', str(text).casefold()).strip()


def clean(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    frame = frame.copy()
    original = len(frame)
    frame = frame.dropna(subset=['text', 'label'])
    frame['text'] = frame['text'].astype(str).str.strip()
    frame['label'] = frame['label'].astype(str).str.strip().str.lower()
    frame['normalized'] = frame['text'].map(normalize)
    frame = frame[frame.normalized.str.len() >= 3]
    conflicts = frame.groupby('normalized')['label'].nunique()
    conflicted = set(conflicts[conflicts > 1].index)
    frame = frame[~frame.normalized.isin(conflicted)].drop_duplicates('normalized')
    return frame, {'input_rows': original, 'retained_rows': len(frame), 'conflicting_texts': len(conflicted)}


def separate(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    train, train_audit = clean(train)
    test, test_audit = clean(test)
    overlaps = train.normalized.isin(test.normalized)
    count = int(overlaps.sum())
    train = train[~overlaps].copy()
    if set(train.normalized) & set(test.normalized):
        raise ValueError('Duplicate text leaked across splits.')
    return train, test, {'train_cleaning': train_audit, 'test_cleaning': test_audit,
                         'train_duplicates_removed_against_test': count}
