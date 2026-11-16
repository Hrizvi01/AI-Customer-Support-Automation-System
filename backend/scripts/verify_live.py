"""Smoke-check running local services with an existing FICTIONAL demo ticket.

This creates stored AI analysis and a reply draft; it does not send customer messages.
"""
import argparse
import json
from pathlib import Path
import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8001')
    parser.add_argument('--ticket-id', type=int, required=True, help='Use a fictional demo ticket only.')
    parser.add_argument('--output', type=Path, default=Path('reports/live-smoke.json'))
    args = parser.parse_args()
    with httpx.Client(base_url=args.url, timeout=180) as client:
        health = client.get('/api/health')
        health.raise_for_status()
        state = health.json()
        analysis = client.post(f'/api/tickets/{args.ticket_id}/analyze')
        analysis.raise_for_status()
        analyzed = analysis.json()['analysis']
        draft = client.post(f'/api/tickets/{args.ticket_id}/reply', json={
            'instructions': 'Ask for the transaction date if relevant. Never promise a refund.'})
        result = {'database': state['database_type'], 'health': state,
                  'inference': {k: analyzed[k] for k in ['category', 'priority', 'sentiment']},
                  'reply_http_status': draft.status_code,
                  'reply_model': draft.json().get('reply_model') if draft.is_success else None,
                  'reply_nonempty': bool(draft.json().get('suggested_reply')) if draft.is_success else False,
                  'note': 'Service smoke check on fictional content; not an accuracy evaluation.'}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
