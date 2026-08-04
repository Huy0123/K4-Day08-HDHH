"""
Task 3 - Convert toan bo file trong data/landing/ thanh Markdown.

Su dung MarkItDown cua Microsoft:
    https://github.com/microsoft/markitdown

Cai dat:
    pip install "markitdown[pdf]"

Yeu cau:
    1. Scan toan bo file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Luu vao data/standardized/ va giu nguyen cau truc thu muc con
"""

import json
from pathlib import Path

from markitdown import MarkItDown
from pypdf import PdfReader

LANDING_DIR = Path(__file__).resolve().parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "standardized"
MARKITDOWN_EXTENSIONS = {".pdf", ".docx", ".doc"}


def build_output_path(input_path: Path) -> Path:
    """Map data/landing/... sang data/standardized/... voi duoi .md."""
    relative_path = input_path.relative_to(LANDING_DIR)
    return OUTPUT_DIR / relative_path.with_suffix(".md")


def load_legal_sources() -> dict[str, dict]:
    """Doc metadata cho cac file legal tu sources.json neu co."""
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


def convert_with_markitdown(filepath: Path, md: MarkItDown) -> str:
    """Convert cac file PDF/DOC/DOCX sang markdown."""
    result = md.convert(str(filepath))
    text = (result.text_content or "").strip()
    if text:
        return text

    if filepath.suffix.lower() == ".pdf":
        return convert_pdf_with_pypdf(filepath)

    return ""


def convert_pdf_with_pypdf(filepath: Path) -> str:
    """Fallback khi MarkItDown khong extract duoc text tu PDF."""
    reader = PdfReader(str(filepath))
    pages = []
    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()
        if page_text:
            pages.append(page_text)

    if not pages:
        return ""

    title = f"# {filepath.stem}\n\n"
    body = "\n\n".join(pages)
    return title + body


def build_legal_metadata_markdown(filepath: Path, legal_sources: dict[str, dict]) -> str:
    """Fallback tao markdown tu metadata khi PDF khong extract duoc text."""
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
            "This PDF could not be reliably converted to plain text in the current environment.",
            "The markdown file keeps source metadata so the document is still indexed and traceable.",
            "",
        ]
    )

    if metadata.get("status_note"):
        lines.append("## Status Note")
        lines.append("")
        lines.append(str(metadata["status_note"]))
        lines.append("")

    lines.extend(
        [
            "## File Information",
            "",
            f"- Original filename: `{filepath.name}`",
            f"- Relative path: `data/landing/legal/{filepath.name}`",
            "",
            "Use the original PDF when detailed article-level legal text is needed.",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def convert_json_to_markdown(filepath: Path) -> str:
    """Convert file JSON crawled article/metadata sang markdown."""
    data = json.loads(filepath.read_text(encoding="utf-8"))

    # News/article JSON: uu tien dung metadata header + noi dung markdown.
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

    # JSON khac: luu nguyen dang code block de van co file markdown hop le.
    return f"# {filepath.stem}\n\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"


def convert_file(filepath: Path, md: MarkItDown, legal_sources: dict[str, dict]) -> Path | None:
    """Convert mot file trong data/landing sang file markdown tuong ung."""
    suffix = filepath.suffix.lower()
    if suffix in MARKITDOWN_EXTENSIONS:
        content = convert_with_markitdown(filepath, md)
        if not content.strip() and filepath.suffix.lower() == ".pdf":
            content = build_legal_metadata_markdown(filepath, legal_sources)
    elif suffix == ".json":
        content = convert_json_to_markdown(filepath)
    else:
        return None

    if not content.strip():
        raise ValueError(f"Khong the trich xuat noi dung tu file: {filepath}")

    output_path = build_output_path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def convert_all() -> None:
    """Convert toan bo file hop le tu data/landing sang data/standardized."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    md = MarkItDown()
    legal_sources = load_legal_sources()
    supported_files = [
        path
        for path in sorted(LANDING_DIR.rglob("*"))
        if path.is_file() and path.suffix.lower() in MARKITDOWN_EXTENSIONS.union({".json"})
    ]

    for filepath in supported_files:
        print(f"Converting: {filepath.relative_to(LANDING_DIR)}")
        output_path = convert_file(filepath, md, legal_sources)
        if output_path is not None:
            print(f"  Saved: {output_path.relative_to(OUTPUT_DIR.parent)}")

    print(f"\nDone! Output tai: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
