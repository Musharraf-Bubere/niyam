from niyam.ingestion.cleaning import clean_blocks
from niyam.ingestion.types import BlockKind, ParsedBlock


def block(text: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(kind=BlockKind.TEXT, text=text, page_number=page)


def test_ordinary_blocks_pass_through_unchanged() -> None:
    blocks = [block("Banks must verify identity.")]
    result = clean_blocks(blocks)
    assert result.blocks == blocks
    assert result.watermark_pages == []


def test_image_marker_blocks_are_dropped() -> None:
    result = clean_blocks([block("<!-- image -->"), block("Real text.")])
    assert [b.text for b in result.blocks] == ["Real text."]


def test_image_marker_inside_text_is_removed() -> None:
    result = clean_blocks([block("Before <!-- image --> after.")])
    assert result.blocks[0].text == "Before after."


def test_a_standalone_withdrawn_block_is_a_watermark() -> None:
    blocks = [block("Withdrawn", page=1), block("Text.", page=1), block("Withdrawn", page=2)]
    result = clean_blocks(blocks)
    assert [b.text for b in result.blocks] == ["Text."]
    assert result.watermark_pages == [1, 2]


def test_withdrawn_inside_a_sentence_is_kept() -> None:
    blocks = [block("The licence may be withdrawn by the Bank.")]
    result = clean_blocks(blocks)
    assert result.blocks == blocks
    assert result.watermark_pages == []


def test_watermark_match_ignores_case_and_spacing() -> None:
    result = clean_blocks([block("  WITHDRAWN \n")])
    assert result.blocks == []
    assert result.watermark_pages == [1]
