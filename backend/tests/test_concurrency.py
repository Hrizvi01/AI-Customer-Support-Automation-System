import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from app.database import Base
from app.models import Ticket


def test_versioning_rejects_stale_write(tmp_path):
    engine = create_engine(f'sqlite:///{tmp_path / "concurrency.db"}')
    Base.metadata.create_all(engine)
    with Session(engine) as setup:
        ticket = Ticket(subject='Concurrency test', description='A fictional isolated versioning test.',
                        customer_name='Test', customer_email='test@example.test')
        setup.add(ticket)
        setup.commit()
        ticket_id = ticket.id
    with Session(engine) as first, Session(engine) as second:
        a, b = first.get(Ticket, ticket_id), second.get(Ticket, ticket_id)
        a.status = 'resolved'
        first.commit()
        b.status = 'in_progress'
        with pytest.raises(StaleDataError):
            second.commit()
    engine.dispose()
