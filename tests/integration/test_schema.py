from sqlalchemy import text
from sqlalchemy.orm import Session


def test_migration_created_both_tables(session: Session) -> None:
    rows = session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    ).scalars()

    assert {"documents", "chunks"} <= set(rows)
