import pytest

from niyam.ingestion.types import BlockKind, ParsedBlock


def test_valid_block_keeps_its_values() -> None:
    block = ParsedBlock(kind=BlockKind.TEXT, text="Banks must verify identity.", page_number=3)
    assert block.page_number == 3
    assert block.kind is BlockKind.TEXT


@pytest.mark.parametrize("page_number", [0, -1])
def test_page_number_must_be_at_least_one(page_number: int) -> None:
    with pytest.raises(ValueError, match="page_number"):
        ParsedBlock(kind=BlockKind.TEXT, text="x", page_number=page_number)


@pytest.mark.parametrize("text", ["", "   ", "\n"])
def test_blank_text_is_rejected(text: str) -> None:
    with pytest.raises(ValueError, match="text"):
        ParsedBlock(kind=BlockKind.TEXT, text=text, page_number=1)
