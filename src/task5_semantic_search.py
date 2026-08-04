"""
Task 5 — Semantic Search Module (Dense Retrieval & HyDE).

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store ChromaDB.

Yêu cầu:
    - Input: query string + top_k (+ optional use_hyde)
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

try:
    from .task4_chunking_indexing import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL
except ImportError:
    from task4_chunking_indexing import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

_model = None
_client = None
_collection = None


def get_embedding_model() -> SentenceTransformer:
    """Tải và cache embedding model từ Task 4."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def get_collection():
    """Lấy ChromaDB collection đã được index từ Task 4."""
    global _client, _collection
    if _collection is None:
        if not CHROMA_DIR.exists():
            raise RuntimeError(f"Thư mục ChromaDB không tồn tại tại {CHROMA_DIR}. Vui lòng chạy Task 4 trước.")
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            _collection = _client.get_collection(name=COLLECTION_NAME)
        except Exception:
            raise RuntimeError(f"Collection '{COLLECTION_NAME}' chưa được khởi tạo. Vui lòng chạy Task 4 (task4_chunking_indexing.py) trước để indexing dữ liệu vào ChromaDB.")
    return _collection


def generate_hypothetical_document(query: str) -> str:
    """
    HyDE (Hypothetical Document Embeddings):
    Tạo văn bản giả định nâng cao chất lượng tìm kiếm cho chủ đề Luật Lao động.
    """
    hyde_doc = (
        f"Quy định pháp luật lao động Việt Nam về: {query}.\n"
        "Theo Bộ luật Lao động 2019 và các Nghị định hướng dẫn thi hành:\n"
        "- Quyền và nghĩa vụ của người lao động và người sử dụng lao động.\n"
        "- Quy định chi tiết về hợp đồng lao động, thời gian thử việc, tiền lương làm thêm giờ (OT), nghỉ phép năm, bảo hiểm và xử lý kỷ luật sa thải."
    )
    return hyde_doc


def semantic_search(query: str, top_k: int = 10, use_hyde: bool = False) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity (với tùy chọn HyDE).

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa
        use_hyde: Nếu True, áp dụng Hypothetical Document Embeddings để mở rộng query

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index...
        }
        Sorted by score descending.
    """
    if not query or not query.strip():
        return []

    model = get_embedding_model()
    collection = get_collection()

    search_text = query
    if use_hyde:
        search_text = generate_hypothetical_document(query) + "\n\nTruy vấn gốc: " + query

    query_vector = model.encode(search_text, normalize_embeddings=True).tolist()

    total_chunks = collection.count()
    if total_chunks == 0:
        return []

    n_results = min(top_k * 2, total_chunks)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    if not results or not results.get("documents") or not results["documents"][0]:
        return []

    output = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        # Cosine distance -> similarity = 1 - distance
        score = max(0.0, 1.0 - dist)
        output.append({
            "content": doc,
            "score": round(float(score), 4),
            "metadata": meta
        })

    # Sắp xếp giảm dần theo similarity score
    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    test_query = "Thời gian thử việc tối đa cho lập trình viên là bao lâu"
    print(f"Query: {test_query}\n")
    results = semantic_search(test_query, top_k=3, use_hyde=True)
    for i, r in enumerate(results, 1):
        print(f"[{i}] Score: {r['score']:.4f}")
        print(f"    Source: {r['metadata'].get('source', 'N/A')}")
        print(f"    Content: {r['content'][:150]}...\n")
