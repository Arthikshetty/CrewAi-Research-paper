import logging
import tempfile
from typing import Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from src.utils.text_processing import clean_text

logger = logging.getLogger(__name__)


class PDFExtractInput(BaseModel):
    pdf_url: str = Field(..., description="URL of the PDF to download and extract text from")


class PDFExtractionTool(BaseTool):
    name: str = "pdf_extraction"
    description: str = (
        "Download a research paper PDF and extract its full text. "
        "Use this when you need the complete paper text for detailed summarization."
    )
    args_schema: Type[BaseModel] = PDFExtractInput

    def _run(self, pdf_url: str) -> str:
        try:
            return self._extract_text(pdf_url)
        except Exception as e:
            logger.error(f"PDF extraction error for {pdf_url}: {e}")
            return f"Error extracting PDF: {e}"

    def _extract_text(self, pdf_url: str) -> str:
        try:
            import fitz  # pymupdf
        except ImportError:
            return "Error: pymupdf not installed. Install with: pip install pymupdf"

        resp = requests.get(pdf_url, timeout=60, stream=True)
        resp.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        try:
            for chunk in resp.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp.flush()
            tmp.close()

            doc = fitz.open(tmp.name)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        finally:
            import os
            os.unlink(tmp.name)

        full_text = "\n".join(text_parts)
        full_text = clean_text(full_text)

        if len(full_text) > 15000:
            full_text = full_text[:15000] + "\n\n[... text truncated for processing ...]"

        return full_text
