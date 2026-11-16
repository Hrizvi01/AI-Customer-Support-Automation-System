"""Prepare HUMAN-labeled priority data; never manufacture labels from keywords."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from .data import clean, separate


def prepare(input_path: Path, output: Path, source: str, license_name: str) -> dict:
    frame = pd.read_csv(input_path, dtype=str)
    required = {'text', 'priority', 'group_id'}
    if not required.issubset(frame.columns):
        raise ValueError('CSV must contain text, priority, group_id. See docs/DATASETS.md.')
    if frame[list(required)].isna().any().any():
        raise ValueError('Every row needs reviewed priority labels and nonempty group IDs. No automatic labels are assigned.')
    frame = frame.rename(columns={'priority': 'label'})
    frame['group_id'] = frame['group_id'].str.strip()
    frame, cleaning = clean(frame)
    if set(frame.label) != {'low', 'medium', 'high'}:
        raise ValueError('Reviewed labels must cover exactly low, medium, high.')
    if frame.group_id.str.strip().eq('').any():
        raise ValueError('group_id cannot be blank.')
    # Stable group-hash partition: all tickets from one customer/thread stay together.
    frame['split'] = frame.group_id.map(lambda value: 'test' if int(hashlib.sha256(value.encode()).hexdigest()[:8], 16) % 5 == 0 else 'train')
    train, test, audit = separate(frame[frame.split == 'train'], frame[frame.split == 'test'])
    for label in ['low', 'medium', 'high']:
        if sum(train.label == label) < 5 or sum(test.label == label) < 2:
            raise ValueError('Need at least 5 training and 2 held-out test examples per class after group splitting. Collect more reviewed labels.')
    output.mkdir(parents=True, exist_ok=True)
    train.to_csv(output / 'train.csv', index=False)
    test.to_csv(output / 'test.csv', index=False)
    metadata = {'source': source, 'license': license_name, 'task': 'priority',
                'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
                'label_origin': 'Human-reviewed input labels; supplied by dataset owner.',
                'split': 'Stable SHA256 group partition (~80/20); no group overlap.',
                'cleaning': cleaning, 'audit': audit}
    (output / 'provenance.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('data/priority'))
    parser.add_argument('--source', required=True)
    parser.add_argument('--license', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.input, args.output, args.source, args.license), indent=2))
