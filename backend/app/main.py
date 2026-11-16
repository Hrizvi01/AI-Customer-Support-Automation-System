import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from .config import settings
from .database import get_db
from .models import Ticket, TicketEvent, utcnow
from .schemas import Category, Priority, Status, TicketCreate, TicketOut, TicketUpdate, TextRequest, ReplyRequest
from .services import inference, ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
app = FastAPI(title='SupportPilot API', version='1.0.0', description='Local AI support triage with human review.')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=['GET', 'POST', 'PATCH'], allow_headers=['Content-Type'])
DB = Annotated[Session, Depends(get_db)]


@app.exception_handler(StaleDataError)
async def stale_error(request: Request, exc: StaleDataError) -> JSONResponse:
    return JSONResponse(status_code=409, content={'detail': 'Ticket changed during this operation. Refresh and retry.'})


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error('Database operation failed: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable. Check PostgreSQL and run migrations.'})


def require_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(404, 'Ticket not found.')
    return ticket


def event(db: Session, ticket: Ticket, action: str, detail: str) -> None:
    db.add(TicketEvent(ticket_id=ticket.id, action=action, detail=detail))


@app.get('/api/health')
def health(db: DB) -> dict:
    try:
        db.execute(select(Ticket.id).limit(1))
        db_status = 'ready'
    except SQLAlchemyError:
        db.rollback()
        db_status = 'unavailable'
    return {'database': db_status, 'database_type': 'sqlite_demo' if settings.database_url.startswith('sqlite') else 'postgresql',
            'ollama': ollama.status(),
            'category_model': inference.models.report('category')['status'],
            'priority_model': inference.models.report('priority')['status'],
            'sentiment': 'downloaded' if (settings.sentiment_dir / 'config.json').exists() else 'not_downloaded'}


@app.get('/api/tickets')
def list_tickets(db: DB, q: str = Query('', max_length=200), status: Status | None = None,
                 category: Category | None = None, priority: Priority | None = None,
                 page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)) -> dict:
    statement = select(Ticket)
    if q:
        statement = statement.where(or_(Ticket.subject.ilike(f'%{q}%'), Ticket.description.ilike(f'%{q}%'),
                                        Ticket.customer_name.ilike(f'%{q}%')))
    for column, value in [(Ticket.status, status), (Ticket.category, category), (Ticket.priority, priority)]:
        if value:
            statement = statement.where(column == value)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    tickets = db.scalars(statement.order_by(Ticket.created_at.desc(), Ticket.id.desc())
                         .offset((page - 1) * page_size).limit(page_size)).all()
    return {'items': [TicketOut.model_validate(t) for t in tickets], 'total': total, 'page': page, 'page_size': page_size}


@app.post('/api/tickets', response_model=TicketOut, status_code=201)
def create_ticket(body: TicketCreate, db: DB) -> Ticket:
    ticket = Ticket(**body.model_dump())
    db.add(ticket)
    db.flush()
    event(db, ticket, 'created', 'Ticket created. Fields set by the agent; no AI inference claimed.')
    db.commit()
    logger.info('Ticket %s created', ticket.id)
    return ticket


@app.get('/api/tickets/{ticket_id}', response_model=TicketOut)
def get_ticket(ticket_id: int, db: DB) -> Ticket:
    return require_ticket(db, ticket_id)


@app.patch('/api/tickets/{ticket_id}', response_model=TicketOut)
def update_ticket(ticket_id: int, body: TicketUpdate, db: DB) -> Ticket:
    ticket = require_ticket(db, ticket_id)
    changes = body.model_dump(exclude_unset=True)
    if not changes:
        return ticket
    content_changed = any(k in changes and getattr(ticket, k) != changes[k] for k in ['subject', 'description'])
    for key, value in changes.items():
        setattr(ticket, key, value)
    if content_changed:
        ticket.analysis = None
        ticket.sentiment = None
        ticket.suggested_reply = None
        ticket.reply_model = None
    if 'status' in changes:
        ticket.resolved_at = utcnow() if changes['status'] == 'resolved' else None
    event(db, ticket, 'updated', 'Agent updated: ' + ', '.join(changes.keys()))
    db.commit()
    return ticket


@app.get('/api/tickets/{ticket_id}/events')
def events(ticket_id: int, db: DB) -> list[dict]:
    require_ticket(db, ticket_id)
    rows = db.scalars(select(TicketEvent).where(TicketEvent.ticket_id == ticket_id)
                      .order_by(TicketEvent.created_at.desc(), TicketEvent.id.desc())).all()
    return [{'id': r.id, 'action': r.action, 'detail': r.detail, 'created_at': r.created_at} for r in rows]


@app.post('/api/predict')
def predict(body: TextRequest) -> dict:
    return {'category': inference.models.predict('category', body.text),
            'priority': inference.models.predict('priority', body.text),
            'sentiment': inference.sentiment.predict(body.text)}


@app.post('/api/tickets/{ticket_id}/analyze', response_model=TicketOut)
def analyze(ticket_id: int, db: DB) -> Ticket:
    ticket = require_ticket(db, ticket_id)
    content = ticket.subject + '\n' + ticket.description
    results = predict(TextRequest(text=content[:10000]))
    ticket.analysis = {**results, 'analyzed_at': utcnow().isoformat()}
    ticket.sentiment = results['sentiment'].get('label')
    # Suggestions are never silently applied to agent-owned routing fields.
    ticket.updated_at = utcnow()
    event(db, ticket, 'analyzed', 'AI analysis completed; unavailable components are reported individually.')
    db.commit()
    return ticket


@app.post('/api/tickets/{ticket_id}/reply', response_model=TicketOut)
def suggest_reply(ticket_id: int, body: ReplyRequest, db: DB) -> Ticket:
    ticket = require_ticket(db, ticket_id)
    try:
        reply = ollama.generate_reply(ticket.subject, ticket.description, body.instructions)
    except ollama.OllamaUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    ticket.suggested_reply = reply
    ticket.reply_model = settings.ollama_model
    event(db, ticket, 'reply_suggested', f'Draft generated by {settings.ollama_model}; not sent to customer.')
    db.commit()
    return ticket


@app.get('/api/models')
def model_reports() -> dict:
    return {'category': inference.models.report('category'), 'priority': inference.models.report('priority'),
            'sentiment': {'model': settings.sentiment_model,
                          'status': 'downloaded' if (settings.sentiment_dir / 'config.json').exists() else 'not_downloaded',
                          'evaluation': None, 'note': 'Pretrained on social-media sentiment; not evaluated on support tickets.'}}


@app.get('/api/analytics')
def analytics(db: DB) -> dict:
    def counts(column) -> dict:
        return {str(key or 'unassigned'): value for key, value in db.execute(select(column, func.count()).group_by(column))}
    statuses, categories, priorities, sentiments = (counts(c) for c in [Ticket.status, Ticket.category, Ticket.priority, Ticket.sentiment])
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=13)
    grouped = {str(day): count for day, count in db.execute(
        select(func.date(Ticket.created_at), func.count()).where(Ticket.created_at >= first_day)
        .group_by(func.date(Ticket.created_at)))}
    sentiment_rows = db.execute(select(func.date(Ticket.created_at), Ticket.sentiment, func.count())
                                .where(Ticket.created_at >= first_day, Ticket.sentiment.is_not(None))
                                .group_by(func.date(Ticket.created_at), Ticket.sentiment)).all()
    by_day: dict[str, dict] = {}
    for day, label, count in sentiment_rows:
        by_day.setdefault(str(day), {})[label] = count
    trend = [{'date': str(first_day + timedelta(days=i)), 'tickets': grouped.get(str(first_day + timedelta(days=i)), 0),
              **{label: by_day.get(str(first_day + timedelta(days=i)), {}).get(label, 0)
                 for label in ['positive', 'negative', 'neutral']}} for i in range(14)]
    total = sum(statuses.values())
    return {'total': total, 'open': statuses.get('open', 0), 'in_progress': statuses.get('in_progress', 0),
            'resolved': statuses.get('resolved', 0),
            'resolution_rate': round(statuses.get('resolved', 0) / total * 100, 1) if total else 0,
            'high_priority': db.scalar(select(func.count()).select_from(Ticket).where(Ticket.priority == 'high', Ticket.status != 'resolved')),
            'categories': categories, 'priorities': priorities, 'sentiments': sentiments, 'trend': trend}
