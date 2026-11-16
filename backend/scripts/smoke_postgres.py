"""Run only against a dedicated local/CI PostgreSQL demonstration database."""
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

if not settings.database_url.startswith('postgresql'):
    raise SystemExit('This smoke check requires an explicit PostgreSQL DATABASE_URL.')

with TestClient(app) as client:
    assert client.get('/api/health').json()['database'] == 'ready'
    response = client.post('/api/tickets', json={
        'subject': 'PostgreSQL integration smoke test',
        'description': 'Fictional test ticket created to verify PostgreSQL persistence and API behavior.',
        'customer_name': 'CI Test', 'customer_email': 'ci@example.test', 'priority': 'low'})
    assert response.status_code == 201, response.text
    ticket_id = response.json()['id']
    assert client.get(f'/api/tickets/{ticket_id}').status_code == 200
    resolved = client.patch(f'/api/tickets/{ticket_id}', json={'status': 'resolved'})
    assert resolved.status_code == 200 and resolved.json()['resolved_at']
    assert len(client.get(f'/api/tickets/{ticket_id}/events').json()) == 2
    assert client.get('/api/analytics').status_code == 200
    print(f'PostgreSQL smoke check passed; fictional resolved test ticket #{ticket_id} retained.')
