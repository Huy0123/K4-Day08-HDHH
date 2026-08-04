"""Task 1 - Tải văn bản pháp luật lao động từ nguồn chính thức.

Nguồn được giới hạn ở Cổng Thông tin điện tử Chính phủ. Các URL bên dưới
trỏ trực tiếp tới tệp đính kèm của trang văn bản, không phải PDF tự tạo.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
MANIFEST_PATH = DATA_DIR / "sources.json"

DOCUMENTS = (
    {
        "filename": "bo-luat-lao-dong-45-2019-qh14.pdf",
        "title": "Bộ luật Lao động số 45/2019/QH14",
        "document_page": (
            "https://vanban.chinhphu.vn/"
            "?classid=1&docid=198540&pageid=27160&typegroupid=3"
        ),
        "download_url": (
            "https://datafiles.chinhphu.vn/cpp/files/vbpq/2019/12/45.signed.pdf"
        ),
        "issuer": "Quốc hội",
        "issued_date": "2019-11-20",
        "effective_date": "2021-01-01",
        "status_note": "Đã được sửa đổi, bổ sung hoặc bãi bỏ một phần.",
    },
    {
        "filename": "nghi-dinh-145-2020-nd-cp.pdf",
        "title": (
            "Nghị định số 145/2020/NĐ-CP hướng dẫn Bộ luật Lao động về "
            "điều kiện lao động và quan hệ lao động"
        ),
        "document_page": (
            "https://vanban.chinhphu.vn/?docid=201967&pageid=27160"
        ),
        "download_url": (
            "https://datafiles.chinhphu.vn/cpp/files/vbpq/2020/12/145.signed.pdf"
        ),
        "issuer": "Chính phủ",
        "issued_date": "2020-12-14",
        "effective_date": "2021-02-01",
        "status_note": "Đã được sửa đổi, bổ sung hoặc bãi bỏ một phần.",
    },
    {
        "filename": "nghi-dinh-12-2022-nd-cp-xu-phat-lao-dong.pdf",
        "title": (
            "Nghị định số 12/2022/NĐ-CP về xử phạt vi phạm hành chính "
            "trong lĩnh vực lao động"
        ),
        "document_page": (
            "https://vanban.chinhphu.vn/"
            "?classid=1&docid=205182&orggroupid=2&pageid=27160"
        ),
        "download_url": (
            "https://datafiles.chinhphu.vn/cpp/files/vbpq/2022/01/"
            "12-2022-nd.signed.pdf"
        ),
        "issuer": "Chính phủ",
        "issued_date": "2022-01-17",
        "effective_date": "2022-01-17",
        "status_note": "Kiểm tra lịch sử hiệu lực trên trang văn bản trước khi tư vấn.",
    },
)

LEGACY_SYNTHETIC_FILES = (
    "bo-luat-lao-dong-2019-thu-viec-va-hop-dong.pdf",
    "nghi-dinh-145-2020-nd-cp-ot-va-nghi-phep.pdf",
    "quy-dinh-cham-dut-hop-dong-va-sa-thai.pdf",
    "hop-dong-lao-dong-va-hoc-viec-mau.pdf",
)


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu nếu chưa tồn tại."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _download_pdf(url: str, destination: Path) -> None:
    """Tải PDF vào tệp tạm, kiểm tra tối thiểu rồi thay thế atomically."""
    request = Request(url, headers={"User-Agent": "K4-Day08-Lab/1.0"})
    handle, temp_name = tempfile.mkstemp(dir=DATA_DIR, suffix=".download")
    os.close(handle)
    temp_path = Path(temp_name)
    try:
        with urlopen(request, timeout=60) as response:  # noqa: S310 - trusted URLs
            content_type = response.headers.get_content_type()
            with temp_path.open("wb") as stream:
                shutil.copyfileobj(response, stream)
        if content_type != "application/pdf":
            raise ValueError(f"URL không trả về PDF: {url} ({content_type})")
        if temp_path.stat().st_size < 10_000:
            raise ValueError(f"PDF tải về quá nhỏ: {temp_path.stat().st_size} bytes")
        with temp_path.open("rb") as stream:
            signature = stream.read(5)
        if signature != b"%PDF-":
            raise ValueError(f"Tệp tải về không có PDF signature: {url}")
        temp_path.replace(destination)
    finally:
        temp_path.unlink(missing_ok=True)


def collect_legal_docs() -> None:
    """Tải bộ tài liệu Luật Lao động và ghi manifest nguồn."""
    setup_directory()

    for document in DOCUMENTS:
        destination = DATA_DIR / document["filename"]
        print(f"Đang tải: {document['title']}")
        _download_pdf(document["download_url"], destination)
        print(f"  Đã lưu: {destination.name} ({destination.stat().st_size:,} bytes)")

    for filename in LEGACY_SYNTHETIC_FILES:
        (DATA_DIR / filename).unlink(missing_ok=True)

    MANIFEST_PATH.write_text(
        json.dumps(DOCUMENTS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Đã lưu thông tin nguồn: {MANIFEST_PATH}")
    print(f"Hoàn thành Task 1: {len(DOCUMENTS)} PDF chính thức.")


if __name__ == "__main__":
    collect_legal_docs()
