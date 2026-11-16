# Interview demonstration (8–10 minutes)

## Before the interview

- Run migrations and opt into fictional seed tickets (`python -m app.seed`).
- Train the category model from the pinned source revision.
- Download the pretrained sentiment weights and verify a local prediction.
- Start Ollama, pull a local instruction model, and configure `OLLAMA_MODEL` to match.
- Open the UI and API `/docs`; rehearse once with internet disconnected after setup.
- Keep priority explicitly untrained unless you have reviewed real labels.

## Walkthrough

1. **Architecture:** React calls FastAPI; PostgreSQL stores tickets/events; scikit-learn
   serves independent category/priority models; PyTorch serves sentiment; Ollama drafts replies.
2. **Overview:** explain that the visible seed tickets are fictional. Counts and chart
   distributions are computed from actual stored records, not hardcoded dashboard numbers.
3. **Ticket creation:** create a fictional duplicate-payment complaint. Leave routing
   unassigned. Search/filter for it in the inbox and open the detail drawer.
4. **Analysis:** run inference. Show category and sentiment scores. Explain why the
   priority prediction is unavailable rather than silently replacing it with a heuristic.
5. **Human review:** apply a category suggestion, manually select priority, and inspect
   the audit trail. Editing ticket text invalidates stale analysis and drafts.
6. **Reply:** ask for an Ollama draft; inspect it before copying. No message is sent.
   Resolve the ticket and show updated dashboard statistics.
7. **Evaluation:** show the actual held-out category confusion matrix and metrics.
   Discuss the majority baseline, the 77-intent mapping, domain shift, leakage checks,
   and the limitation of exact deduplication without source group IDs.
8. **Failure path:** stop Ollama or select an unavailable model, then show the actionable
   503 error. Ticket creation and non-generative features remain available.

## Engineering discussion

- Pipelines keep learned vocabulary/IDF and classifier fitting inside the training boundary.
- Train/test source fingerprints and fixed hyperparameters support reproducibility.
- Optimistic ticket versioning rejects stale writes after concurrent operations.
- Alembic manages schema changes; no implicit production table creation is performed.
- Missing components return structured statuses instead of fake classifications.
- Predictions are advisory, and generation cannot issue refunds or perform backend actions.
- A production next step is authentication/RBAC, tenant isolation, a background job queue,
  structured redacted observability, domain evaluation, calibrated thresholds, and incident-aware splits.

Do not describe this local demo as production-ready or claim that priority training,
support-domain sentiment evaluation, or unrun Docker tests have been completed.
