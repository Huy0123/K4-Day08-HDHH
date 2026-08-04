"""
Task 4 — Chunking & Indexing vào Vector Store (Bộ luật Lao động 2019 Cho Người Trẻ - Gen Z).

Lựa chọn và lý do:
    - Chunking: RecursiveCharacterTextSplitter
        * CHUNK_SIZE=800: đủ lớn để giữ ngữ nghĩa đầy đủ của một điều khoản luật lao động,
          không quá nhỏ (mất context) cũng không quá lớn (kém chính xác khi retrieval).
        * CHUNK_OVERLAP=100: ~12.5% overlap giúp không bị mất thông tin ở biên chunk.

    - Embedding model: BAAI/bge-m3
        * Multilingual: hỗ trợ xuất sắc tiếng Việt trong văn bản pháp luật.
        * 1024 chiều: biểu diễn ngữ nghĩa phong phú.

    - Vector Store: ChromaDB (persistent local)
        * Đơn giản, không cần Docker.
"""

from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# =============================================================================
# CONFIGURATION
# =============================================================================

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

VECTOR_STORE = "chromadb"
COLLECTION_NAME = "labor_law_genz_docs"


# =============================================================================
# IMPLEMENTATION
# =============================================================================

def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str}}
    """
    documents = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        if md_file.name.startswith(".") or md_file.stat().st_size < 50:
            continue
        content = md_file.read_text(encoding="utf-8")
        if not content.strip():
            continue
        doc_type = "legal" if "legal" in str(md_file) else "news"
        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "source_path": str(md_file),
                "type": doc_type,
                "customer_role": _infer_customer_role(md_file.name, doc_type),
            }
        })
    return documents


def _infer_customer_role(filename: str, doc_type: str) -> str:
    if "hop-dong" in filename or "mau" in filename:
        return "seller"
    if "bo-luat" in filename or "thu-viec" in filename:
        return "buyer"
    return "both"


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents bằng RecursiveCharacterTextSplitter.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, chunk_text in enumerate(splits):
            if not chunk_text.strip():
                continue
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i,
                    "total_chunks": len(splits),
                }
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng BAAI/bge-m3.
    """
    from sentence_transformers import SentenceTransformer

    print(f"Loading embedding model: {EMBEDDING_MODEL} ...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [c["content"] for c in chunks]
    print(f"Embedding {len(texts)} chunks ...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào ChromaDB persistent local store tại chroma_db/.
    """
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted old collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [
        f"{c['metadata']['source']}_chunk_{c['metadata']['chunk_index']}"
        for c in chunks
    ]
    documents = [c["content"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_slice = slice(i, i + batch_size)
        collection.upsert(
            ids=ids[batch_slice],
            documents=documents[batch_slice],
            embeddings=embeddings[batch_slice],
            metadatas=metadatas[batch_slice],
        )
        print(f"  Indexed batch {i // batch_size + 1}: {len(ids[batch_slice])} chunks")

    total = collection.count()
    print(f"ChromaDB collection '{COLLECTION_NAME}' now has {total} chunks.")


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing (Luật Lao Động 2019 Gen Z)")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\nLoaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("Done! Indexed to ChromaDB at:", CHROMA_DIR)


if __name__ == "__main__":
    run_pipeline()
