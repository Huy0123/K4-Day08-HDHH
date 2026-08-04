"""
Task 6 - Lexical Search Module (BM25).

Mac dinh su dung BM25 tren corpus markdown trong data/standardized/.
"""

import re
from pathlib import Path

from rank_bm25 import BM25Okapi

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Cache tai runtime de tranh build lai BM25 moi lan goi search.
CORPUS: list[dict] = []
_TOKENIZED_CORPUS: list[list[str]] = []
_BM25_INDEX: BM25Okapi | None = None


def tokenize(text: str) -> list[str]:
    """Tokenize don gian, phu hop cho BM25 baseline."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def load_corpus() -> list[dict]:
    """
    Doc cac file markdown trong data/standardized/ thanh corpus.

    Returns:
        List of {'content': str, 'metadata': dict}
    """
    corpus = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not md_file.is_file():
            continue

        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue

        doc_type = "legal" if "legal" in md_file.parts else "news"
        corpus.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "source_path": str(md_file),
                    "type": doc_type,
                },
            }
        )
    return corpus


def build_bm25_index(corpus: list[dict]):
    """
    Xay dung BM25 index tu corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    return BM25Okapi(tokenized_corpus), tokenized_corpus


def _ensure_index() -> None:
    """Khoi tao corpus va BM25 index neu chua co."""
    global CORPUS, _TOKENIZED_CORPUS, _BM25_INDEX

    if _BM25_INDEX is not None and CORPUS:
        return

    CORPUS = load_corpus()
    if not CORPUS:
        _TOKENIZED_CORPUS = []
        _BM25_INDEX = None
        return

    _BM25_INDEX, _TOKENIZED_CORPUS = build_bm25_index(CORPUS)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tim kiem tu khoa su dung BM25.

    Args:
        query: Cau truy van
        top_k: So luong ket qua toi da

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict
        }
        Sorted by score descending.
    """
    _ensure_index()

    if not query.strip() or _BM25_INDEX is None or not CORPUS:
        return []

    tokenized_query = tokenize(query)
    if not tokenized_query:
        return []

    scores = _BM25_INDEX.get_scores(tokenized_query)
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda idx: scores[idx],
        reverse=True,
    )

    results = []
    for idx in ranked_indices:
        score = float(scores[idx])
        if score <= 0:
            continue

        results.append(
            {
                "content": CORPUS[idx]["content"],
                "score": score,
                "metadata": CORPUS[idx]["metadata"],
            }
        )

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    results = lexical_search("nghi dinh lao dong", top_k=5)
    for result in results:
        print(f"[{result['score']:.3f}] {result['metadata']['source']}")
