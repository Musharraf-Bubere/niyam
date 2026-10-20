"""Remove known noise from parsed blocks without rewriting the regulation text."""

import re
from dataclasses import dataclass, replace

from niyam.ingestion.types import ParsedBlock

_IMAGE_MARKER = "<!-- image -->"
_WATERMARK = "withdrawn"
_EXTRA_SPACES = re.compile(r"[ \t]{2,}")


@dataclass(frozen=True)
class CleanResult:
    """Blocks with noise removed, plus the pages where the Withdrawn watermark was seen."""

    blocks: list[ParsedBlock]
    watermark_pages: list[int]


def clean_blocks(blocks: list[ParsedBlock]) -> CleanResult:
    kept: list[ParsedBlock] = []
    watermark_pages: set[int] = set()
    for block in blocks:
        if block.text.strip().lower() == _WATERMARK:
            watermark_pages.add(block.page_number)
            continue
        text = _remove_image_markers(block.text)
        if not text:
            continue
        kept.append(block if text == block.text else replace(block, text=text))
    return CleanResult(blocks=kept, watermark_pages=sorted(watermark_pages))


def _remove_image_markers(text: str) -> str:
    if _IMAGE_MARKER not in text:
        return text
    return _EXTRA_SPACES.sub(" ", text.replace(_IMAGE_MARKER, " ")).strip()
