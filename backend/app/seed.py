"""Opt-in fictional interview demo records, never training data or predictions."""
from datetime import timedelta
from sqlalchemy import func, select
from .database import SessionLocal
from .models import Ticket, TicketEvent, utcnow

EXAMPLES = [
    ('Charged twice for one purchase', 'My card statement shows two charges for the same purchase. Could you help me investigate?', 'Maya Chen', 'billing', 'high', 'open'),
    ('Unable to sign in to my account', 'I forgot my passcode and cannot access my account. How can I securely restore access?', 'James Wilson', 'account', 'high', 'open'),
    ('Card payment keeps failing', 'My card payment is declined even though my account has enough funds. I tried again this morning.', 'Sofia Martinez', 'technical', 'medium', 'in_progress'),
    ('Refund has not arrived', 'The merchant approved my refund, but I cannot see it on my statement. What information do you need?', 'Oliver Reed', 'billing', 'medium', 'open'),
    ('How do I update my address?', 'I recently moved and would like to update the address associated with my account.', 'Amara Okafor', 'account', 'low', 'resolved'),
    ('International card availability', 'Can I use my card while traveling abroad? I would like information about supported countries.', 'Ethan Brooks', 'general', 'low', 'open'),
    ('Contactless payment not working', 'My physical card works with a PIN, but the contactless feature stopped working yesterday.', 'Priya Sharma', 'technical', 'medium', 'in_progress'),
    ('Unexpected transfer charge', 'I noticed an extra fee after a bank transfer. Could someone explain what this charge relates to?', 'Leo Anderson', 'billing', 'medium', 'open'),
    ('Account verification assistance', 'My identity verification was rejected, and I would like to understand the next steps.', 'Isabella Rossi', 'account', 'high', 'in_progress'),
    ('Physical card delivery question', 'I ordered a physical card last week. Where can I find the delivery information?', 'Noah Williams', 'general', 'low', 'resolved'),
    ('Virtual card stopped working', 'My virtual card fails on several websites. The error appears before the payment is completed.', 'Zara Ahmed', 'technical', 'high', 'open'),
    ('Question about exchange fees', 'I plan to exchange currency for a trip. Where can I review the applicable fees before making a transfer?', 'Lucas Bennett', 'billing', 'low', 'resolved'),
]


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Ticket)):
            print('Workspace is not empty. Skipping demo seed to avoid mixing or duplicating records.')
            return
        now = utcnow()
        for i, (subject, description, name, category, priority, status) in enumerate(EXAMPLES):
            created = now - timedelta(days=i % 12, hours=i % 4)
            ticket = Ticket(subject=subject, description=description, customer_name=name,
                            customer_email=name.lower().replace(' ', '.') + '@example.test',
                            category=category, priority=priority, status=status,
                            created_at=created, updated_at=created,
                            resolved_at=created + timedelta(hours=2) if status == 'resolved' else None)
            db.add(ticket)
            db.flush()
            db.add(TicketEvent(ticket_id=ticket.id, action='demo_created',
                               detail='Fictional demo record. Routing labels are manually assigned; no model inference claimed.',
                               created_at=created))
        db.commit()
    print('Created 12 FICTIONAL demo tickets. No training labels or model predictions were generated.')


if __name__ == '__main__':
    main()
