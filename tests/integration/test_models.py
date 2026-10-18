import uuid
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from niyam.db.models import EMBEDDING_DIMENSIONS, Chunk, Document


def make_document(**overrides: Any) -> Document:
    values: dict[str, Any] = {
        "regulator": "RBI",
        "circular_number": "RBI/2024-25/12",
        "title": "Master Direction on KYC",
        "content_hash": uuid.uuid4().hex,
    }
    values.update(overrides)
    return Document(**values)


def unit_vector(position: int) -> list[float]:
    """A vector with a single 1.0 at `position` and zeros elsewhere."""
    vector = [0.0] * EMBEDDING_DIMENSIONS
    vector[position] = 1.0
    return vector


def test_document_defaults_are_filled_in(session: Session) -> None:
    document = make_document()
    session.add(document)
    session.flush()
    session.refresh(document)

    assert document.status == "active"
    assert document.created_at is not None


@pytest.mark.parametrize(
    ("field", "value"),
    [("regulator", "IRDAI"), ("status", "deleted")],
)
def test_check_constraints_reject_invalid_values(session: Session, field: str, value: str) -> None:
    session.add(make_document(**{field: value}))

    with pytest.raises(IntegrityError):
        session.flush()


def test_duplicate_content_hash_is_rejected(session: Session) -> None:
    session.add_all([make_document(content_hash="same"), make_document(content_hash="same")])

    with pytest.raises(IntegrityError):
        session.flush()


def test_chunk_position_is_unique_within_a_document(session: Session) -> None:
    document = make_document()
    document.chunks = [Chunk(chunk_index=0, text="a"), Chunk(chunk_index=0, text="b")]
    session.add(document)

    with pytest.raises(IntegrityError):
        session.flush()


def test_database_cascades_document_delete_to_chunks(session: Session) -> None:
    document = make_document()
    document.chunks = [Chunk(chunk_index=0, text="first"), Chunk(chunk_index=1, text="second")]
    session.add(document)
    session.flush()

    session.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document.id})

    assert session.scalar(text("SELECT count(*) FROM chunks")) == 0


def test_search_text_is_generated_and_matches_word_forms(session: Session) -> None:
    document = make_document()
    document.chunks = [
        Chunk(chunk_index=0, text="Banks must complete customer due diligence"),
        Chunk(chunk_index=1, text="Interest rates on deposits are reviewed quarterly"),
    ]
    session.add(document)
    session.flush()

    matches = session.scalars(
        select(Chunk.text).where(
            Chunk.search_text.match("customers", postgresql_regconfig="english")
        )
    ).all()

    assert matches == ["Banks must complete customer due diligence"]


def test_vector_search_returns_nearest_chunk_first(session: Session) -> None:
    document = make_document()
    document.chunks = [
        Chunk(chunk_index=0, text="north", embedding=unit_vector(0)),
        Chunk(chunk_index=1, text="east", embedding=unit_vector(1)),
        Chunk(chunk_index=2, text="up", embedding=unit_vector(2)),
    ]
    session.add(document)
    session.flush()

    query = unit_vector(1)
    query[0] = 0.2

    nearest = session.scalars(
        select(Chunk.text).order_by(Chunk.embedding.cosine_distance(query)).limit(2)
    ).all()

    assert nearest == ["east", "north"]
