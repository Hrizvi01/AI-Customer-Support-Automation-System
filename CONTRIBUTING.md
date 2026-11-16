# Development

Use Python 3.12 and Node.js 22. Follow the README for PowerShell and Docker setup.
Keep dependency changes explicit and run backend tests plus the frontend build before committing.

```powershell
# backend/
python -m pytest -q
python -m alembic check

# frontend/
npm ci
npm run build
```

`alembic check` needs a migrated database. The tests use isolated SQLite files.
For a database regression, also run migrations and API smoke checks against PostgreSQL.
Never point destructive test fixtures at a live customer database.

Update model/data documentation whenever features, label mappings, splits, or dependencies
change. Do not use held-out test scores to choose hyperparameters. Reviewers should see
what changed, what was tested, and the limitations of any reported result.

Never commit raw customer tickets, secrets, `.env`, database files, Hugging Face cache,
model weights, `node_modules`, or generated builds. Joblib artifacts are executable pickle
content: load only artifacts you created with this project's training command.

No outbound email integration is present. Keep reply generation advisory and preserve
source/provenance information when changing inference behavior.
