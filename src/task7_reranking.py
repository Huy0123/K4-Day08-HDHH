"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement — khuyến nghị vì không cần API key

Nếu dùng MMR hoặc RRF, đảm bảo hiểu và giải thích được cơ chế.

Lưu ý quan trọng về RRF (sẽ dùng lại ở Task 9): điểm RRF fused CHỈ phụ thuộc thứ hạng,
không phải độ tương đồng thật. Top-1 sau khi fuse luôn xấp xỉ 1/(k+1) ≈ 0.0164 (k=60),
bất kể nội dung đó có thật sự liên quan đến câu hỏi hay không. Đừng dùng điểm RRF để
quyết định fallback ở Task 9 — xem ghi chú ở đó.
"""

from typing import Optional


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates sử dụng cross-encoder model.

    Args:
        query: Câu truy vấn
        candidates: List of {'content': str, 'score': float, 'metadata': dict}
        top_k: Số lượng kết quả sau rerank

    Returns:
        List of top_k candidates, re-scored và sorted by rerank_score descending.
    """
    if not candidates:
        return []

    try:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("BAAI/bge-reranker-base")
        pairs = [[query, c["content"]] for c in candidates]
        scores = model.predict(pairs)

        reranked = []
        for c, s in zip(candidates, scores):
            item = c.copy()
            item["score"] = float(s)
            reranked.append(item)

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:top_k]
    except Exception:
        # Fallback keyword overlap + candidate score ranking
        query_words = set(query.lower().split())
        results = []
        for c in candidates:
            item = c.copy()
            content_words = set(c["content"].lower().split())
            overlap = len(query_words.intersection(content_words)) / max(len(query_words), 1)
            item["score"] = float(c.get("score", 0.0)) + overlap
            results.append(item)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


def _cosine_sim(a: list[float], b: list[float]) -> float:
    import numpy as np
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.

    MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected_docs))

    Args:
        query_embedding: Vector embedding của query
        candidates: List of {'content': str, 'score': float, 'embedding': list, 'metadata': dict}
        top_k: Số lượng kết quả
        lambda_param: Trade-off giữa relevance (1.0) và diversity (0.0)

    Returns:
        List of top_k candidates selected by MMR.
    """
    if not candidates:
        return []

    valid_candidates = [c for c in candidates if "embedding" in c and c["embedding"]]
    if not valid_candidates:
        sorted_cands = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
        return sorted_cands[:top_k]

    selected_indices = []
    remaining_indices = list(range(len(valid_candidates)))

    for _ in range(min(top_k, len(valid_candidates))):
        best_idx = -1
        best_score = float("-inf")

        for idx in remaining_indices:
            cand_emb = valid_candidates[idx]["embedding"]
            relevance = _cosine_sim(query_embedding, cand_emb)

            max_sim_to_selected = 0.0
            for sel_idx in selected_indices:
                sim = _cosine_sim(cand_emb, valid_candidates[sel_idx]["embedding"])
                if sim > max_sim_to_selected:
                    max_sim_to_selected = sim

            mmr_score = lambda_param * relevance - (1.0 - lambda_param) * max_sim_to_selected

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        if best_idx != -1:
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

    results = []
    for idx in selected_indices:
        item = valid_candidates[idx].copy()
        results.append(item)

    return results


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.

    RRF(d) = Σ 1 / (k + rank_r(d))

    Args:
        ranked_lists: List of ranked result lists (mỗi list từ 1 ranker)
        top_k: Số lượng kết quả cuối cùng
        k: Smoothing constant (default=60, từ paper Cormack et al. 2009)

    Returns:
        List of top_k candidates sorted by RRF score descending.
    """
    if not ranked_lists:
        return []

    rrf_scores = {}  # content -> score
    content_map = {}  # content -> full dict

    for ranked_list in ranked_lists:
        if not ranked_list:
            continue
        for rank, item in enumerate(ranked_list, 1):
            key = item.get("content", "")
            if not key:
                continue
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (k + rank)
            if key not in content_map:
                content_map[key] = item

    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for content, score in sorted_items[:top_k]:
        item = content_map[content].copy()
        item["score"] = score
        results.append(item)

    return results


# =============================================================================
# Main rerank interface
# =============================================================================

def rerank(
    query: str,
    candidates: list[dict] | list[list[dict]],
    top_k: int = 5,
    method: str = "rrf",  # "cross_encoder" | "mmr" | "rrf"
) -> list[dict]:
    """
    Unified reranking interface.

    Args:
        query: Câu truy vấn
        candidates: Danh sách candidates từ retrieval (hoặc list of ranked lists nếu dùng RRF)
        top_k: Số lượng kết quả sau rerank
        method: Phương pháp reranking

    Returns:
        List of top_k reranked candidates.
    """
    if not candidates:
        return []

    if method == "rrf":
        if isinstance(candidates[0], list):
            ranked_lists = candidates
        else:
            ranked_lists = [candidates]
        return rerank_rrf(ranked_lists, top_k=top_k)

    elif method == "cross_encoder":
        if isinstance(candidates[0], list):
            flat_candidates = [item for lst in candidates for item in lst]
        else:
            flat_candidates = candidates
        return rerank_cross_encoder(query, flat_candidates, top_k=top_k)

    elif method == "mmr":
        if isinstance(candidates[0], list):
            flat_candidates = [item for lst in candidates for item in lst]
        else:
            flat_candidates = candidates

        query_embedding = None
        for c in flat_candidates:
            if "embedding" in c and c["embedding"]:
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer("BAAI/bge-m3")
                    query_embedding = model.encode(query, normalize_embeddings=True).tolist()
                except Exception:
                    pass
                break

        if query_embedding is not None:
            return rerank_mmr(query_embedding, flat_candidates, top_k=top_k)
        else:
            sorted_cands = sorted(flat_candidates, key=lambda x: x.get("score", 0.0), reverse=True)
            return sorted_cands[:top_k]

    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    # Test with dummy data
    dummy_candidates = [
        {"content": "Chính sách trả hàng và hoàn tiền Shopee trong 15 ngày", "score": 0.8, "metadata": {}},
        {"content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam", "score": 0.6, "metadata": {}},
        {"content": "Quy định đăng bán sản phẩm dành cho người bán", "score": 0.5, "metadata": {}},
    ]
    results = rerank("chính sách trả hàng shopee", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")

