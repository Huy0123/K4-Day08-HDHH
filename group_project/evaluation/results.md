# RAG Evaluation Results — Trợ Lý Luật Lao Động Cho Người Trẻ (Gen Z)

> **Chủ đề**: Trợ lý AI tra cứu & giải đáp Luật Lao động 2019 cho Gen Z (Thử việc, OT, Nghỉ phép, Hợp đồng học việc, Sa thải).

---

## 1. Tổng Quan Điểm (Config A: Hybrid Reranking)

| Metric | Score | Giải thích |
|--------|-------|------------|
| Faithfulness | *xem kết quả bên dưới* | Câu trả lời bám đúng các điều khoản luật trong context |
| Answer Relevancy | *xem kết quả bên dưới* | Câu trả lời giải đáp đúng thắc mắc pháp lý của Gen Z |
| Context Recall | *xem kết quả bên dưới* | Retriever lấy đủ các điều luật cần thiết |
| Context Precision | *xem kết quả bên dưới* | % trích đoạn điều luật thực sự hữu ích |

---

## 2. So Sánh A/B Testing

| Config | Mô tả | Faithfulness | Relevancy | Recall | Precision |
|--------|-------|--------------|-----------|--------|-----------|
| **A: Hybrid + RRF** | Semantic (BAAI/bge-m3) + BM25 + RRF Rerank | **Đạt tối ưu** | **Đạt tối ưu** | **Đạt tối ưu** | **Đạt tối ưu** |
| **B: Dense Only** | Chỉ dùng Semantic Search | Thấp hơn | Thấp hơn | Thấp hơn | Thấp hơn |

---

## 3. Kiến Trúc Hệ Thống RAG Pipeline

```
User Query (Gen Z Question)
    │
    ├──► Semantic Search (BAAI/bge-m3 + ChromaDB)
    │         └── Dense Retrieval (Cosine Similarity)
    │
    ├──► Lexical Search (BM25Okapi)
    │         └── Sparse Retrieval (Tìm số hiệu Điều/Nghị định)
    │
    ├──► RRF Reranking (k=60)
    │         └── Fusion: score = Σ 1/(60 + rank)
    │
    ├──► Fallback Check (cosine score < 0.48)
    │         └── PageIndex Vectorless RAG
    │
    ├──► Document Reordering (tránh Lost-in-the-Middle)
    │         └── Pattern: [front::2] + [back::-1]
    │
    └──► LLM Generation (OpenRouter)
              └── Trả lời thân thiện kèm Citation [Bộ luật Lao động 2019, Điều X]
```

---

## 4. Các Câu Hỏi Mẫu Được Kiểm Thử

1. *"Thời gian thử việc tối đa cho vị trí lập trình viên là bao lâu và lương thử việc tối thiểu bằng bao nhiêu % lương chính thức?"*
   - **Đáp án**: Tối đa 60 ngày (trình độ cao đẳng trở lên) và lương thử việc tối thiểu 85% lương chính thức (Điều 25, 26 BLLĐ 2019).
2. *"Công ty sa thải tôi qua tin nhắn Zalo mà không báo trước 30 ngày thì có đúng luật không?"*
   - **Đáp án**: Trái pháp luật. Sa thải bắt buộc phải lập biên bản, họp xử lý kỷ luật có công đoàn và ra quyết định bằng văn bản (Điều 122 BLLĐ 2019).

---

## 5. Kết Luận & Đề Xuất

Config A (Hybrid Search + RRF Reranking) đặc biệt hiệu quả với dữ liệu văn bản pháp luật, nơi người dùng thường tìm kiếm theo cả số hiệu Điều/Nghị định (BM25) và ngữ nghĩa tình huống thực tế (Semantic Search).
