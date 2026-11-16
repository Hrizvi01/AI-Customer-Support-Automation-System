import json
import pandas as pd
import pytest
from ml.data import clean, separate
from ml.prepare_priority import prepare
from ml.train import train
from app.services.inference import ModelService
from app.config import settings


def test_normalized_duplicates_and_conflicts():
    train = pd.DataFrame({'text': ['Same text!', 'same text', 'Conflict', 'Conflict', 'Unique train'],
                          'label': ['a', 'a', 'a', 'b', 'b']})
    test = pd.DataFrame({'text': ['SAME TEXT', 'Unique test'], 'label': ['a', 'b']})
    training, testing, audit = separate(train, test)
    assert len(training) == 1 and len(testing) == 2
    assert audit['train_cleaning']['conflicting_texts'] == 1
    assert audit['train_duplicates_removed_against_test'] == 1


def test_unlabeled_priority_rejected(tmp_path):
    source = tmp_path / 'unlabeled.csv'
    pd.DataFrame({'text': ['Needs help'], 'priority': [None], 'group_id': ['a']}).to_csv(source, index=False)
    with pytest.raises(ValueError, match='reviewed'):
        prepare(source, tmp_path / 'prepared', 'test fixture', 'test only')


def test_priority_groups_never_overlap(tmp_path):
    source = tmp_path / 'reviewed.csv'
    # Deliberately constructed test fixture; never used for portfolio metrics.
    records = [{'text': f'{label} fixture ticket {i}', 'priority': label, 'group_id': f'customer-{i}'}
               for label in ['low', 'medium', 'high'] for i in range(100)]
    pd.DataFrame(records).to_csv(source, index=False)
    prepare(source, tmp_path / 'prepared', 'synthetic unit test fixture', 'test only')
    a = pd.read_csv(tmp_path / 'prepared/train.csv')
    b = pd.read_csv(tmp_path / 'prepared/test.csv')
    assert not set(a.group_id) & set(b.group_id)


def test_train_serve_and_report_real_computation(tmp_path, monkeypatch):
    data = tmp_path / 'data'
    data.mkdir()
    labels = ['billing', 'account', 'technical', 'general']
    for split in ['train', 'test']:
        frame = pd.DataFrame([{'text': f'{label} {split} request number {i}', 'label': label}
                              for label in labels for i in range(5)])
        frame.to_csv(data / f'{split}.csv', index=False)
    (data / 'provenance.json').write_text(json.dumps({'source': 'synthetic unit-test fixture only'}))
    report = train('category', data, tmp_path / 'models', tmp_path / 'reports')
    assert report['train_rows'] == 20 and report['test_rows'] == 20
    assert sum(sum(row) for row in report['confusion_matrix']) == 20
    monkeypatch.setattr(settings, 'model_dir', tmp_path / 'models')
    result = ModelService().predict('category', 'billing request question')
    assert result['status'] == 'ready' and 0 <= result['confidence'] <= 1


def test_trainer_refuses_leakage(tmp_path):
    (tmp_path / 'provenance.json').write_text('{}')
    frame = pd.DataFrame({'text': ['a billing', 'b technical', 'c account', 'd general'],
                          'label': ['billing', 'technical', 'account', 'general']})
    for split in ['train', 'test']:
        frame.to_csv(tmp_path / f'{split}.csv', index=False)
    with pytest.raises(ValueError, match='overlap'):
        train('category', tmp_path, tmp_path / 'models', tmp_path / 'reports')
