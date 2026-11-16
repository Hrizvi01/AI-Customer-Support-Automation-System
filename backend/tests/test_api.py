from unittest.mock import Mock
import pytest
from app.services import inference, ollama

PAYLOAD = {'subject': 'Duplicate payment', 'description': 'My account was charged twice for one purchase.',
           'customer_name': 'Demo Customer', 'customer_email': 'demo@example.test'}


def test_ticket_lifecycle_filters_and_analytics(client):
    response = client.post('/api/tickets', json={**PAYLOAD, 'priority': 'high', 'category': 'billing'})
    assert response.status_code == 201
    ticket_id = response.json()['id']
    assert response.json()['analysis'] is None
    assert client.get('/api/tickets?priority=low').json()['total'] == 0
    assert client.get('/api/tickets?q=Duplicate').json()['total'] == 1
    assert client.get('/api/tickets?category=billing').json()['total'] == 1
    assert client.get('/api/analytics').json()['high_priority'] == 1
    updated = client.patch(f'/api/tickets/{ticket_id}', json={'status': 'resolved'})
    assert updated.json()['resolved_at'] is not None
    stats = client.get('/api/analytics').json()
    assert stats['resolved'] == 1 and stats['resolution_rate'] == 100 and stats['high_priority'] == 0
    assert len(stats['trend']) == 14
    assert client.patch(f'/api/tickets/{ticket_id}', json={'status': 'open'}).json()['resolved_at'] is None
    assert len(client.get(f'/api/tickets/{ticket_id}/events').json()) == 3


def test_missing_models_are_not_fake_predictions(client):
    result = client.post('/api/predict', json={'text': 'Please help with my card.'}).json()
    assert result['category']['status'] == 'untrained'
    assert result['priority']['label'] is None
    assert result['sentiment']['label'] is None
    assert client.get('/api/models').json()['priority']['metrics'] is None


def test_analysis_is_advisory_and_content_edit_invalidates(client, monkeypatch):
    monkeypatch.setattr(inference.models, 'predict', lambda task, text: {'status': 'ready', 'label': 'technical' if task == 'category' else 'low', 'confidence': .91})
    monkeypatch.setattr(inference.sentiment, 'predict', lambda text: {'status': 'ready', 'label': 'negative', 'confidence': .87})
    ticket_id = client.post('/api/tickets', json={**PAYLOAD, 'category': 'billing', 'priority': 'high'}).json()['id']
    response = client.post(f'/api/tickets/{ticket_id}/analyze').json()
    assert response['category'] == 'billing' and response['priority'] == 'high'
    assert response['analysis']['category']['label'] == 'technical'
    assert response['sentiment'] == 'negative'
    assert client.get('/api/analytics').json()['sentiments']['negative'] == 1
    response = client.patch(f'/api/tickets/{ticket_id}', json={'subject': 'Updated evidence'}).json()
    assert response['analysis'] is None and response['sentiment'] is None


def test_ollama_failure_and_success(client, monkeypatch):
    ticket_id = client.post('/api/tickets', json=PAYLOAD).json()['id']
    def fail(*args):
        raise ollama.OllamaUnavailable('Local model unavailable')
    monkeypatch.setattr(ollama, 'generate_reply', fail)
    assert client.post(f'/api/tickets/{ticket_id}/reply', json={}).status_code == 503
    assert client.get(f'/api/tickets/{ticket_id}').json()['suggested_reply'] is None
    monkeypatch.setattr(ollama, 'generate_reply', lambda *args: 'Thank you for reaching out. Could you share the transaction date?')
    response = client.post(f'/api/tickets/{ticket_id}/reply', json={}).json()
    assert response['suggested_reply'].startswith('Thank you')
    assert response['status'] == 'open'


@pytest.mark.parametrize('change', [{'customer_email': 'bad'}, {'subject': 'x'}, {'priority': 'critical'}, {'unknown': 'bad'}])
def test_create_validation(client, change):
    assert client.post('/api/tickets', json={**PAYLOAD, **change}).status_code == 422


def test_update_validation_missing_and_pagination(client):
    assert client.get('/api/tickets/999').status_code == 404
    assert client.get('/api/tickets?page=0').status_code == 422
    assert client.get('/api/tickets?priority=urgent').status_code == 422
    ticket_id = client.post('/api/tickets', json=PAYLOAD).json()['id']
    assert client.patch(f'/api/tickets/{ticket_id}', json={'status': None}).status_code == 422
    assert client.patch(f'/api/tickets/{ticket_id}', json={'customer_name': 'Not editable'}).status_code == 422
    assert client.post('/api/predict', json={'text': '   '}).status_code == 422


def test_ollama_http_error_is_actionable(monkeypatch):
    import httpx
    monkeypatch.setattr(ollama.httpx, 'post', Mock(side_effect=httpx.ConnectError('offline')))
    with pytest.raises(ollama.OllamaUnavailable):
        ollama.generate_reply('Subject', 'Customer text')
