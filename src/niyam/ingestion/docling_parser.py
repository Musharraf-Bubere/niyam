"""Docling-backed DocumentParser. Needs the optional 'ingest' dependency group."""

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DocItem, TableItem

from niyam.ingestion.raw_items import RawItem, blocks_from_items
from niyam.ingestion.types import ParsedBlock


class DoclingParser:
    """Parses a PDF with Docling. All three circulars have a text layer, so OCR is off."""

    def __init__(self) -> None:
        options = PdfPipelineOptions(do_ocr=False)
        self._converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )

    def parse(self, path: Path) -> list[ParsedBlock]:
        document = self._converter.convert(path).document
        items: list[RawItem] = []
        for item, _level in document.iterate_items():
            if not isinstance(item, DocItem):
                continue
            if isinstance(item, TableItem):
                text = item.export_to_markdown(doc=document)
            else:
                text = getattr(item, "text", "") or ""
            page = item.prov[0].page_no if item.prov else None
            items.append(RawItem(label=str(item.label), text=text, page_number=page))
        return blocks_from_items(items)
