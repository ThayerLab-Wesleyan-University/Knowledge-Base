"""Conservative text-only PDF extraction. No OCR or layout-fidelity claims."""
import io

import pypdf

from utility_scripts.contracts import KBError, safe_text


def convert_pdf(data: bytes, config: dict) -> tuple[str, dict]:
    try:
        reader = pypdf.PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted:
            raise KBError("Encrypted PDF: submit a permitted, unencrypted copy.")
        if not reader.pages or len(reader.pages) > config["max_pdf_pages"]:
            raise KBError("PDF is empty or exceeds max_pdf_pages.")
        pages = []
        for number, page in enumerate(reader.pages, 1):
            stream = page.get_contents()
            if stream and len(stream.get_data()) > config["max_pdf_page_stream_bytes"]:
                raise KBError(f"PDF page {number} exceeds the decompressed stream limit.")
            text = page.extract_text(extraction_mode="layout").strip()
            # Image-only and otherwise textless pages fail closed, including mixed scans.
            if not text:
                raise KBError(f"PDF page {number} has no extractable text; OCR or manual cleanup is required.")
            safe_text(text, "PDF text")
            pages.append(f"## Page {number}\n\n{text}\n")
        return "\n".join(pages), {"tool": "pypdf-layout", "version": pypdf.__version__}
    except KBError:
        raise
    except Exception as exc:
        raise KBError("PDF extraction failed: submit a readable, unencrypted text PDF.") from exc
