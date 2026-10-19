from niyam.ingestion.chunking import chunk_blocks
from niyam.ingestion.types import BlockKind, ParsedBlock


def heading(text: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(kind=BlockKind.HEADING, text=text, page_number=page)


def para(text: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(kind=BlockKind.TEXT, text=text, page_number=page)


def table(text: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(kind=BlockKind.TABLE, text=text, page_number=page)


def test_no_blocks_gives_no_chunks() -> None:
    assert chunk_blocks([]) == []


def test_text_under_a_heading_becomes_one_chunk_with_that_section() -> None:
    chunks = chunk_blocks([heading("KYC norms"), para("Verify identity.", page=4)])
    assert len(chunks) == 1
    assert chunks[0].section == "KYC norms"
    assert chunks[0].page_number == 4
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "Verify identity."


def test_text_before_any_heading_has_no_section() -> None:
    chunks = chunk_blocks([para("Preamble.")])
    assert chunks[0].section is None


def test_a_new_heading_starts_a_new_chunk() -> None:
    chunks = chunk_blocks([heading("A"), para("one"), heading("B"), para("two")])
    assert [c.section for c in chunks] == ["A", "B"]
    assert [c.chunk_index for c in chunks] == [0, 1]


def test_long_sections_split_between_blocks() -> None:
    blocks = [heading("A"), para("x" * 50), para("y" * 50), para("z" * 50)]
    chunks = chunk_blocks(blocks, max_chars=120)
    assert [c.text for c in chunks] == ["x" * 50 + "\n\n" + "y" * 50, "z" * 50]
    assert all(c.section == "A" for c in chunks)


def test_a_table_is_never_merged_or_split() -> None:
    rows = "| Catgory | Limit |\n| Large Cap | 80% |"
    chunks = chunk_blocks([heading("A"), para("before"), table(rows), para("after")])
    assert [c.text for c in chunks] == ["before", rows, "after"]
