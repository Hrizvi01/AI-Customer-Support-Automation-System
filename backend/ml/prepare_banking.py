"""Download a versioned real public intent dataset; preserve its official split."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import pandas as pd
from .taxonomy import category
from .data import separate

DEFAULT_REVISION = 'master'
BASE = 'https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets'


def prepare(output: Path, revision: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    frames = {}
    for split in ['train', 'test']:
        url = f'{BASE}/{revision}/banking_data/{split}.csv'
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read()
        hashes[split] = hashlib.sha256(content).hexdigest()
        frame = pd.read_csv(io.BytesIO(content))
        frame = frame.rename(columns={'category': 'intent'})
        if not {'text', 'intent'}.issubset(frame.columns):
            raise ValueError('Unexpected BANKING77 schema.')
        frame['label'] = frame.intent.map(category)
        frames[split] = frame[['text', 'label', 'intent']]
    train, test, audit = separate(frames['train'], frames['test'])
    train.to_csv(output / 'train.csv', index=False)
    test.to_csv(output / 'test.csv', index=False)
    mapping = {intent: category(intent) for intent in sorted(set(frames['train'].intent))}
    metadata = {'source': 'BANKING77 / PolyAI-LDN/task-specific-datasets',
                'url': 'https://github.com/PolyAI-LDN/task-specific-datasets',
                'license': 'CC-BY-4.0', 'revision': revision, 'download_sha256': hashes,
                'task': 'category', 'label_origin': 'Original intent labels manually grouped into four operational categories.',
                'domain': 'English online banking queries; not a general support benchmark.',
                'mapping': mapping, 'audit': audit, 'split': 'Official train/test; exact normalized overlaps removed from training.'}
    (output / 'provenance.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('data/category'))
    parser.add_argument('--revision', required=True, help='Use a source Git commit SHA for reproducibility.')
    args = parser.parse_args()
    print(json.dumps(prepare(args.output, args.revision), indent=2))
