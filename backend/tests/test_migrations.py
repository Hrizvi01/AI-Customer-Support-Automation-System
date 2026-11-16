import os
from pathlib import Path
import subprocess
import sys
from sqlalchemy import create_engine, inspect


def test_migration_upgrade_downgrade(tmp_path):
    url = f'sqlite:///{tmp_path / "migration.db"}'
    env = {**os.environ, 'DATABASE_URL': url}
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], cwd=root, env=env, check=True)
    engine = create_engine(url)
    assert {'tickets', 'ticket_events'}.issubset(inspect(engine).get_table_names())
    engine.dispose()
    subprocess.run([sys.executable, '-m', 'alembic', 'check'], cwd=root, env=env, check=True)
    subprocess.run([sys.executable, '-m', 'alembic', 'downgrade', 'base'], cwd=root, env=env, check=True)
    engine = create_engine(url)
    assert 'tickets' not in inspect(engine).get_table_names()
    engine.dispose()
