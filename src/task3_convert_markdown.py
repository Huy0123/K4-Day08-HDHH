"""
Task 3 - Convert toan bo file trong data/landing/ thanh Markdown.

Thu tu convert:
1. MarkItDown
2. PyMuPDF text extraction
3. OCR bang RapidOCR + PyMuPDF render
4. Neu van that bai moi fallback sang metadata
"""

import io
import json
from pathlib import Path

import fitz  # PyMuPDF
from markitdown import MarkItDown
from PIL import Image
from pypdf import PdfReader
from rapidocr_onnxruntime import RapidOCR

LANDING_DIR = Path(__file__).resolve().parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "standardized"
MARKITDOWN_EXTENSIONS = {".pdf", ".docx", ".doc"}
MIN_TEXT_LENGTH = 500
MAX_OCR_PAGES = 10


def build_output_path(input_path: Path) -> Path:
    relative_path = input_path.relative_to(LANDING_DIR)
    return OUTPUT_DIR / relative_path.with_suffix(".md")


def load_legal_sources() -> dict[str, dict]:
    sources_path = LANDING_DIR / "legal" / "sources.json"
    if not sources_path.exists():
        return {}

    raw_sources = json.loads(sources_path.read_text(encoding="utf-8"))
    if not isinstance(raw_sources, list):
        return {}

    return {
        item["filename"]: item
        for item in raw_sources
        if isinstance(item, dict) and item.get("filename")
    }


def normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def is_good_extraction(text: str) -> bool:
    return len(normalize_text(text)) >= MIN_TEXT_LENGTH


def convert_with_markitdown(filepath: Path, md: MarkItDown) -> str:
    result = md.convert(str(filepath))
    return normalize_text(result.text_content or "")


def convert_pdf_with_pymupdf(filepath: Path) -> str:
    pages = []
    with fitz.open(filepath) as doc:
        for page in doc:
            page_text = normalize_text(page.get_text("text") or "")
            if page_text:
                pages.append(page_text)

    if not pages:
        return ""
    return f"# {filepath.stem}\n\n" + "\n\n".join(pages)


def convert_pdf_with_pypdf(filepath: Path) -> str:
    reader = PdfReader(str(filepath))
    pages = []
    for page in reader.pages:
        page_text = normalize_text(page.extract_text() or "")
        if page_text:
            pages.append(page_text)

    if not pages:
        return ""
    return f"# {filepath.stem}\n\n" + "\n\n".join(pages)


def convert_pdf_with_ocr(filepath: Path, ocr_engine: RapidOCR, max_pages: int = MAX_OCR_PAGES) -> str:
    pages = []
    with fitz.open(filepath) as doc:
        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages)
        print(f"  Running OCR on {pages_to_process}/{total_pages} pages")

        for page_index, page in enumerate(doc, start=1):
            if page_index > max_pages:
                break

            print(f"    OCR page {page_index}/{pages_to_process}")
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            result, _ = ocr_engine(image)
            lines = []
            if result:
                for item in result:
                    if len(item) >= 2 and item[1]:
                        lines.append(str(item[1]).strip())
            page_text = normalize_text("\n".join(lines))
            if page_text:
                pages.append(f"## Page {page_index}\n\n{page_text}")

    if not pages:
        return ""
    return f"# {filepath.stem}\n\n" + "\n\n".join(pages)


def build_legal_metadata_markdown(filepath: Path, legal_sources: dict[str, dict]) -> str:
    metadata = legal_sources.get(filepath.name, {})
    title = metadata.get("title", filepath.stem)
    lines = [f"# {title}", ""]

    if metadata.get("issuer"):
        lines.append(f"**Issuer:** {metadata['issuer']}")
    if metadata.get("issued_date"):
        lines.append(f"**Issued Date:** {metadata['issued_date']}")
    if metadata.get("effective_date"):
        lines.append(f"**Effective Date:** {metadata['effective_date']}")
    if metadata.get("document_page"):
        lines.append(f"**Document Page:** {metadata['document_page']}")
    if metadata.get("download_url"):
        lines.append(f"**Download URL:** {metadata['download_url']}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Extraction Note",
            "",
            "This PDF could not be converted to full text with the available local libraries.",
            "Source metadata is kept so the document remains traceable.",
            "",
        ]
    )

    if metadata.get("status_note"):
        lines.append("## Status Note")
        lines.append("")
        lines.append(str(metadata["status_note"]))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def convert_json_to_markdown(filepath: Path) -> str:
    data = json.loads(filepath.read_text(encoding="utf-8"))

    if any(key in data for key in ("title", "url", "content_markdown", "content")):
        header = f"# {data.get('title', filepath.stem)}\n\n"
        if data.get("url"):
            header += f"**Source:** {data['url']}\n"
        if data.get("category"):
            header += f"**Category:** {data['category']}\n"
        if data.get("date_crawled"):
            header += f"**Crawled:** {data['date_crawled']}\n"
        if header != f"# {data.get('title', filepath.stem)}\n\n":
            header += "\n---\n\n"

        content = data.get("content_markdown") or data.get("content")
        if content:
            return header + content
        return header + "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"

    return f"# {filepath.stem}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"


def convert_pdf(filepath: Path, md: MarkItDown, ocr_engine: RapidOCR, legal_sources: dict[str, dict]) -> str:
    text = convert_with_markitdown(filepath, md)
    if is_good_extraction(text):
        print("  Extracted with MarkItDown")
        return text

    text = convert_pdf_with_pymupdf(filepath)
    if is_good_extraction(text):
        print("  Extracted with PyMuPDF fallback")
        return text

    text = convert_pdf_with_pypdf(filepath)
    if is_good_extraction(text):
        print("  Extracted with pypdf fallback")
        return text

    text = convert_pdf_with_ocr(filepath, ocr_engine)
    if is_good_extraction(text):
        print("  Extracted with RapidOCR fallback")
        return text

    print("  Falling back to metadata because full-text extraction failed")
    return build_legal_metadata_markdown(filepath, legal_sources)


def convert_file(
    filepath: Path,
    md: MarkItDown,
    ocr_engine: RapidOCR,
    legal_sources: dict[str, dict],
) -> Path | None:
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        content = convert_pdf(filepath, md, ocr_engine, legal_sources)
    elif suffix in {".docx", ".doc"}:
        content = convert_with_markitdown(filepath, md)
    elif suffix == ".json":
        content = convert_json_to_markdown(filepath)
    else:
        return None

    content = normalize_text(content)
    if not content:
        raise ValueError(f"Khong the trich xuat noi dung tu file: {filepath}")

    output_path = build_output_path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content + "\n", encoding="utf-8")
    return output_path


def convert_all() -> None:
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    md = MarkItDown()
    ocr_engine = RapidOCR()
    legal_sources = load_legal_sources()
    supported_extensions = MARKITDOWN_EXTENSIONS.union({".json"})
    supported_files = [
        path
        for path in sorted(LANDING_DIR.rglob("*"))
        if path.is_file() and path.suffix.lower() in supported_extensions
    ]

    for filepath in supported_files:
        print(f"Converting: {filepath.relative_to(LANDING_DIR)}")
        output_path = convert_file(filepath, md, ocr_engine, legal_sources)
        if output_path is not None:
            print(f"  Saved: {output_path.relative_to(OUTPUT_DIR.parent)}")

    print(f"\nDone! Output tai: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
