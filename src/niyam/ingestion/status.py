"""Cross-check a circular's manifest status against the Withdrawn watermark."""

from niyam.ingestion.manifest import DocumentStatus


class StatusConflictError(Exception):
    """The manifest and the document disagree in a way that is unsafe to ignore."""


def check_status(status: DocumentStatus, watermark_pages: list[int]) -> list[str]:
    """Return warnings for harmless disagreements; raise for the dangerous one."""
    watermarked = bool(watermark_pages)
    if status is DocumentStatus.ACTIVE and watermarked:
        raise StatusConflictError(
            f"manifest says active but the document shows a Withdrawn watermark "
            f"on pages {watermark_pages}; fix the manifest or the file before ingesting"
        )
    if status is DocumentStatus.WITHDRAWN and not watermarked:
        return ["manifest says withdrawn but no Withdrawn watermark was found in the document"]
    return []
