# Verification record

Local verification date: **17 November 2026** (Asia/Karachi).

## Completed checks

| Check | Observed result |
|---|---|
| Backend automated suite | **19 passed** on Python 3.12.15 |
| Frontend production build | Passed with React 19, Vite 6, Recharts 3 |
| Python compilation | Application and ML modules compiled successfully |
| Alembic SQLite upgrade / check / downgrade | Passed in isolated migration test |
| Local migrated demo schema | `alembic check`: no new upgrade operations |
| PostgreSQL migration generation | Offline DDL generated, including JSON and timezone-aware columns |
| Compose / CI YAML | Parsed; expected services/jobs present |
| Browser dashboard | Desktop overview and actual model reports inspected; screenshots saved |
| Browser ticket workflow | Fictional ticket created, opened, and analyzed; category suggestion persisted without overwriting routing |
| Category training | Completed from pinned BANKING77 source revision |
| Local sentiment artifact | Downloaded pinned source weights, loaded with weights-only deserialization, saved safetensors |
| Real PyTorch sentiment inference | Passed through running FastAPI; actual class and softmax score recorded in the live smoke report |
| Ollama draft persistence | Passed with installed `qwen2.5:0.5b`: HTTP 200 and nonempty stored draft |
| Ollama availability handling | Automated success/failure tests passed |

## Category evaluation

The actual run used 9,947 training and 3,076 held-out test examples after deduplication.
Results: accuracy **94.54%**, macro precision **94.02%**, macro recall **94.45%**, macro F1
**94.23%**, majority baseline accuracy **32.44%**. The complete report, checksums,
per-class scores, and confusion counts are committed in `backend/reports/category.json`
and `backend/reports/category-confusion.csv`.

These are results for a project-defined four-class grouping of banking intents. No claim
of general customer-support accuracy or production readiness is made.

## Explicitly unverified / unavailable

- **Priority training/evaluation:** not run on real data because a verified reviewed
  labeled dataset was not supplied. The preparation/training/serving code is implemented
  and tested on isolated constructed test fixtures; those scores are not portfolio metrics.
- **PostgreSQL runtime and Docker build/start:** not executed locally because PostgreSQL
  and Docker are absent. PostgreSQL migration/API smoke checks are configured in CI but
  no successful remote CI run is claimed here.
- **Sentiment support-domain accuracy:** no labeled support-domain sentiment evaluation
  was performed. A service smoke check is not a benchmark.
- **Mobile browser interaction / accessibility audit:** responsive styles and dialog
  keyboard behavior are implemented; a full device or accessibility audit was not performed.
- **Public deployment, authentication, multi-tenant isolation, email sending:** outside
  this local portfolio demonstration.

## Reproduce live service checks

Start the backend and Ollama with a configured installed model, then use an existing
fictional ticket ID:

```powershell
# backend/
python -m scripts.verify_live --ticket-id 1
```

This saves structured service evidence in `backend/reports/live-smoke.json`. It performs
real inference and stores a suggested reply without sending it. The ticket ID in your
workspace may differ. Source/model provenance and request status are included; no private
customer text is copied into that report.
