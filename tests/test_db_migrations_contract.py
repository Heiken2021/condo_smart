from pathlib import Path

DB = Path('core/db.py').read_text(encoding='utf-8')


def test_database_initialization_uses_advisory_lock():
    assert 'pg_advisory_lock' in DB
    assert 'pg_advisory_unlock' in DB


def test_migrations_run_once():
    assert 'schema_migrations' in DB
    assert '_apply_file_once' in DB


def test_migration_checksum_guard():
    assert 'checksum' in DB
    assert 'cambió después de haber sido aplicada' in DB


def test_old_run_every_startup_loop_removed():
    assert 'run_script(f)' not in DB
