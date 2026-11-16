import json
import hashlib
from pathlib import Path
import urllib.request
from app.config import settings


def download_file(url: str, target: Path, size: int, sha256: str | None) -> None:
    def valid() -> bool:
        if not target.exists() or target.stat().st_size != size:
            return False
        if sha256:
            with target.open('rb') as stream:
                return hashlib.file_digest(stream, 'sha256').hexdigest() == sha256
        return True
    if valid():
        return
    temporary = target.with_suffix(target.suffix + '.partial')
    print(f'Downloading {target.name}: {size / 1024 / 1024:.1f} MiB', flush=True)
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as stream:
        written, mark = 0, 0
        while block := response.read(1024 * 1024):
            stream.write(block)
            written += len(block)
            if written // (64 * 1024 * 1024) > mark:
                mark = written // (64 * 1024 * 1024)
                print(f'  {written / max(1, size):.0%}', flush=True)
    temporary.replace(target)
    if not valid():
        raise ValueError(f'Integrity check failed for {target.name}. Retry the download.')


def main() -> None:
    source = settings.sentiment_dir / '_download'
    source.mkdir(parents=True, exist_ok=True)
    base = f'https://huggingface.co/{settings.sentiment_model}'
    with urllib.request.urlopen(f'https://huggingface.co/api/models/{settings.sentiment_model}/tree/{settings.sentiment_revision}', timeout=30) as response:
        files = {f['path']: f for f in json.load(response) if f['type'] == 'file'}
    weights = 'model.safetensors' if 'model.safetensors' in files else 'pytorch_model.bin'
    if weights not in files:
        raise ValueError('Choose a lightweight model with a single model.safetensors or pytorch_model.bin file.')
    selected = {'config.json', 'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json',
                'vocab.json', 'vocab.txt', 'merges.txt', weights}
    for name in sorted(selected & files.keys()):
        entry = files[name]
        download_file(f'{base}/resolve/{settings.sentiment_revision}/{name}?download=true',
                      source / name, entry['size'], entry.get('lfs', {}).get('oid'))
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(source, local_files_only=True)
    # torch>=2.6 weights-only loading; never trust or execute remote model code.
    model = AutoModelForSequenceClassification.from_pretrained(source, local_files_only=True,
        use_safetensors=weights.endswith('.safetensors'), weights_only=True, trust_remote_code=False)
    tokenizer.save_pretrained(settings.sentiment_dir)
    model.save_pretrained(settings.sentiment_dir, safe_serialization=True)
    (settings.sentiment_dir / 'provenance.json').write_text(json.dumps({
        'source': settings.sentiment_model, 'revision': settings.sentiment_revision,
        'source_format': weights, 'source_sha256': files[weights].get('lfs', {}).get('oid'),
        'local_format': 'safetensors',
        'license': 'CC-BY-4.0' if settings.sentiment_model == 'cardiffnlp/twitter-roberta-base-sentiment-latest' else 'Review upstream model card',
        'fine_tuned_here': False}, indent=2), encoding='utf-8')
    # Remove only our verified source-weight copy after safetensors conversion succeeds.
    (source / weights).unlink()
    print(f'Downloaded {settings.sentiment_model} to {settings.sentiment_dir}. No fine-tuning performed.')


if __name__ == '__main__':
    main()
