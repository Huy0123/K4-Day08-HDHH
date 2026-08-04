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

LANDING_DIR = Path(__file__).resolve().parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "standardized"
MARKITDOWN_EXTENSIONS = {".pdf", ".docx", ".doc"}


def build_output_path(input_path: Path) -> Path:
    """Map data/landing/... sang data/standardized/... voi duoi .md."""
    relative_path = input_path.relative_to(LANDING_DIR)
    return OUTPUT_DIR / relative_path.with_suffix(".md")


def convert_with_markitdown(filepath: Path, md: MarkItDown) -> str:
    """Convert cac file PDF/DOC/DOCX sang markdown."""
    result = md.convert(str(filepath))
    return result.text_content


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


def convert_file(filepath: Path, md: MarkItDown) -> Path | None:
    """Convert mot file trong data/landing sang file markdown tuong ung."""
    suffix = filepath.suffix.lower()
    if suffix in MARKITDOWN_EXTENSIONS:
        content = convert_with_markitdown(filepath, md)
    elif suffix == ".json":
        content = convert_json_to_markdown(filepath)
    else:
        return None

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
    supported_files = [
        path
        for path in sorted(LANDING_DIR.rglob("*"))
        if path.is_file() and path.suffix.lower() in MARKITDOWN_EXTENSIONS.union({".json"})
    ]

    for filepath in supported_files:
        print(f"Converting: {filepath.relative_to(LANDING_DIR)}")
        output_path = convert_file(filepath, md)
        if output_path is not None:
            print(f"  Saved: {output_path.relative_to(OUTPUT_DIR.parent)}")

    print(f"\nDone! Output tai: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
