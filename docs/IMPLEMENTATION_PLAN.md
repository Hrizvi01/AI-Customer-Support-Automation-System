# Implementation plan and verification boundaries

1. Inspect the existing workspace and keep Folio untouched. Build SupportPilot separately.
2. Verify public dataset provenance. Preserve original classification train/test splits,
   document the four-category mapping, and reject fabricated priority labels.
3. Implement typed FastAPI contracts, SQLAlchemy entities, audit events, concurrency
   protection, pagination/filtering, and Alembic migrations.
4. Implement reproducible TF-IDF classification/priority training, local PyTorch
   sentiment inference, explicit unavailable states, and reviewed Ollama drafts.
5. Build responsive overview, inbox, ticket detail, analytics, and model evaluation views.
6. Verify API behavior, migrations, training, inference, production builds, and browser flows.
7. Package Docker/Windows workflows, actual evaluation reports, screenshots, and demo guidance.

## Deliberate boundaries

- BANKING77 is a real public intent dataset, used with a project-defined four-class mapping.
- Priority is trainable but remains untrained without reviewed human-labeled data.
- Sentiment is pretrained, not fine-tuned or benchmarked on this support domain.
- Fictional seed tickets are UI demo content, never training or evaluation data.
- A missing model never produces an invented prediction or metric.
- SQLite supports the local demo and fast tests; PostgreSQL is the Docker database.
- No customer messages are sent. AI routing fields are advisory until explicitly applied.
