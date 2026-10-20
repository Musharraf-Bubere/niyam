import pytest

from niyam.ingestion.raw_items import RawItem, blocks_from_items
from niyam.ingestion.types import BlockKind, ParsedBlock


def item(label: str, text: str, page: int | None = 1) -> RawItem:
    return RawItem(label=label, text=text, page_number=page)


def test_section_headers_become_headings() -> None:
    blocks = blocks_from_items([item("section_header", "1. Preamble", page=3)])
    assert blocks == [ParsedBlock(kind=BlockKind.HEADING, text="1. Preamble", page_number=3)]


@pytest.mark.parametrize("label", ["text", "list_item", "footnote"])
def test_body_labels_become_text(label: str) -> None:
    blocks = blocks_from_items([item(label, "Banks must verify identity.")])
    assert [b.kind for b in blocks] == [BlockKind.TEXT]


def test_tables_become_table_blocks() -> None:
    markdown = "| Category | Limit |\n| Large Cap | 80% |"
    blocks = blocks_from_items([item("table", markdown, page=7)])
    assert blocks == [ParsedBlock(kind=BlockKind.TABLE, text=markdown, page_number=7)]


@pytest.mark.parametrize("label", ["picture", "page_header", "page_footer", "document_index"])
def test_noise_labels_are_skipped(label: str) -> None:
    assert blocks_from_items([item(label, "something")]) == []


def test_blank_text_is_skipped() -> None:
    assert blocks_from_items([item("text", "   ")]) == []


def test_items_without_a_page_are_skipped() -> None:
    assert blocks_from_items([item("text", "No page.", page=None)]) == []


def test_unknown_labels_are_kept_as_text() -> None:
    blocks = blocks_from_items([item("caption", "Figure 1.")])
    assert [b.kind for b in blocks] == [BlockKind.TEXT]


def test_order_and_pages_are_preserved() -> None:
    blocks = blocks_from_items([item("text", "one", page=1), item("text", "two", page=2)])
    assert [(b.text, b.page_number) for b in blocks] == [("one", 1), ("two", 2)]
