"""
Task 1 — Thu thập văn bản quy định pháp luật lao động cho người trẻ (Gen Z).

Đề tài: Trợ lý AI hỏi đáp Luật Lao động cho Gen Z (Thử việc, OT, Nghỉ phép, Hợp đồng, Sa thải).

Nhiệm vụ:
    1. Tạo 4 văn bản quy định pháp luật lao động (PDF) từ Bộ luật Lao động 2019 và Nghị định 145/2020/NĐ-CP.
    2. Lưu vào data/landing/legal/
    3. Đặt tên file rõ ràng:
       - bo-luat-lao-dong-2019-thu-viec-va-hop-dong.pdf
       - nghi-dinh-145-2020-nd-cp-ot-va-nghi-phep.pdf
       - quy-dinh-cham-dut-hop-dong-va-sa-thai.pdf
       - hop-dong-lao-dong-va-hoc-viec-mau.pdf
    4. Gắn metadata customer_role (buyer/seller/both).
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# Nội dung các văn bản quy định Luật Lao động 2019
DOCUMENTS = {
    "bo-luat-lao-dong-2019-thu-viec-va-hop-dong.pdf": {
        "title": "BỘ LUẬT LAO ĐỘNG 2019 - QUY ĐỊNH VỀ HỢP ĐỒNG LAO ĐỘNG VÀ THỬ VIỆC",
        "customer_role": "buyer",
        "content": """BỘ LUẬT LAO ĐỘNG 2019 - QUY ĐỊNH VỀ HỢP ĐỒNG LAO ĐỘNG VÀ THỬ VIỆC

Metadata: customer_role=buyer

1. THỜI GIAN THỬ VIỆC TỐI ĐA (ĐIỀU 25 BỘ LUẬT LAO ĐỘNG 2019)
- Đối với vị trí quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp: Tối đa 180 ngày.
- Đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên (bao gồm Lập trình viên, Kỹ sư phần mềm, Cử nhân kinh tế, Designer, Marketing): Tối đa 60 ngày.
- Đối với công việc có chức danh nghề nghiệp cần trình độ trung cấp, công nhân kỹ thuật, nhân viên nghiệp vụ: Tối đa 30 ngày.
- Đối với công việc khác: Tối đa 06 ngày làm việc.
- Không áp dụng thử việc đối với hợp đồng lao động có thời hạn dưới 01 tháng.

2. MỨC LƯƠNG THỬ VIỆC TỐI THIỂU (ĐIỀU 26 BỘ LUẬT LAO ĐỘNG 2019)
- Tiền lương của người lao động trong thời gian thử việc do hai bên thỏa thuận nhưng ít nhất phải bằng 85% mức lương của công việc đó.

3. HỢP ĐỒNG LAO ĐỘNG VÀ QUY ĐỊNH GIAO KẾT
- Hợp đồng lao động phải được giao kết bằng văn bản hoặc thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu.
- Hai loại hợp đồng lao động: Hợp đồng lao động không xác định thời hạn và Hợp đồng lao động xác định thời hạn (không quá 36 tháng).
- Khi kết thúc thời gian thử việc đạt yêu cầu, người sử dụng lao động phải giao kết ngay hợp đồng lao động với người lao động.
"""
    },
    "nghi-dinh-145-2020-nd-cp-ot-va-nghi-phep.pdf": {
        "title": "NGHỊ ĐỊNH 145/2020/NĐ-CP - QUY ĐỊNH VỀ LÀM THÊM GIỜ (OT) VÀ NGHỈ PHÉP HÀNG NĂM",
        "customer_role": "both",
        "content": """NGHỊ ĐỊNH 145/2020/NĐ-CP - QUY ĐỊNH VỀ LÀM THÊM GIỜ (OT) VÀ NGHỈ PHÉP HÀNG NĂM

Metadata: customer_role=both

1. TÍNH TIỀN LƯƠNG LÀM THÊM GIỜ (OT - ĐIỀU 98 BỘ LUẬT LAO ĐỘNG 2019)
- Làm thêm giờ vào ngày thường: Được trả lương tính theo đơn giá tiền lương hoặc tiền lương thực trả theo công việc đang làm ít nhất bằng 150%.
- Làm thêm giờ vào ngày nghỉ hàng tuần (cuối tuần thứ Bảy, Chủ Nhật): Ít nhất bằng 200%.
- Làm thêm giờ vào ngày nghỉ lễ, tết, ngày nghỉ có hưởng lương: Ít nhất bằng 300% (chưa kể tiền lương ngày lễ, tết đối với người lao động hưởng lương ngày).

2. TÍNH TIỀN LƯƠNG LÀM THÊM GIỜ BAN ĐÊM (22H ĐẾN 6H SÁNG HÔM SAU)
- Làm việc vào ban đêm: Được trả thêm ít nhất 30% tiền lương tính theo đơn giá tiền lương của ngày làm việc bình thường.
- Làm thêm giờ vào ban đêm: Ngoài tiền lương làm thêm giờ (150%, 200% hoặc 300%), người lao động còn được trả thêm 20% tiền lương tính theo đơn giá tiền lương của ngày làm việc bình thường hoặc ngày nghỉ.

3. GIỚI HẠN SỐ GIỜ LÀM THÊM GIỜ (OT)
- Số giờ làm thêm không quá 50% số giờ làm việc bình thường trong 01 ngày.
- Tổng số giờ làm thêm không quá 40 giờ trong 01 tháng và không quá 200 giờ trong 01 năm (trường hợp đặc biệt do Chính phủ quy định không quá 300 giờ/năm).

4. NGHỈ PHÉP HÀNG NĂM (PHÉP NĂM - ĐIỀU 113 BỘ LUẬT LAO ĐỘNG 2019)
- Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hàng năm hưởng nguyên lương: 12 ngày làm việc đối với công việc trong điều kiện bình thường.
- Cứ đủ 05 năm làm việc cho một người sử dụng lao động thì số ngày nghỉ hàng năm được tăng thêm tương ứng 01 ngày.
"""
    },
    "quy-dinh-cham-dut-hop-dong-va-sa-thai.pdf": {
        "title": "QUY ĐỊNH VỀ ĐƠN PHƯƠNG CHẤM DỨT HỢP ĐỒNG VÀ KỶ LUẬT SA THÁI",
        "customer_role": "both",
        "content": """QUY ĐỊNH VỀ ĐƠN PHƯƠNG CHẤM DỨT HỢP ĐỒNG VÀ KỶ LUẬT SA THÁI

Metadata: customer_role=both

1. THỜI HẠN BÁO TRƯỚC KHI ĐƠN PHƯƠNG CHẤM DỨT HỢP ĐỒNG LAO ĐỘNG (ĐIỀU 35, 36 BỘ LUẬT LAO ĐỘNG 2019)
- Hợp đồng lao động không xác định thời hạn: Người lao động/NSDLĐ phải báo trước ít nhất 45 ngày.
- Hợp đồng lao động xác định thời hạn từ 12 tháng đến 36 tháng: Báo trước ít nhất 30 ngày.
- Hợp đồng lao động xác định thời hạn dưới 12 tháng: Báo trước ít nhất 03 ngày làm việc.

2. QUY ĐỊNH VỀ KỶ LUẬT SA THÁI (ĐIỀU 122, 125 BỘ LUẬT LAO ĐỘNG 2019)
- Hình thức sa thải chỉ được áp dụng trong các trường hợp: trộm cắp, tham ô, tiết lộ bí mật kinh doanh, công nghệ, tự ý bỏ việc 05 ngày cộng dồn trong thời hạn 30 ngày hoặc 20 ngày cộng dồn trong 365 ngày mà không có lý do chính đáng.
- HÌNH THỨC SA THÁI QUA TIN NHẮN ZALO, EMAIL HOẶC LỜI NÓI LÀ TRÁI PHÁP LUẬT: Việc xử lý kỷ luật sa thải bắt buộc phải lập biên bản vi phạm, tổ chức phiên họp xử lý kỷ luật lao động với sự tham gia của đại diện tổ chức công đoàn và có quyết định sa thải bằng văn bản.

3. HẬU QUẢ PHÁP LÝ KHI NSDLĐ SA THÁI HOẶC CHẤM DỨT HỢP ĐỒNG TRÁI PHÁP LUẬT (ĐIỀU 41)
- Nhận người lao động trở lại làm việc theo hợp đồng lao động đã giao kết.
- Trả tiền lương, đóng bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp trong những ngày người lao động không được làm việc.
- Bồi thường thêm cho người lao động một khoản tiền tương ứng ít nhất bằng 02 tháng tiền lương theo hợp đồng lao động.
"""
    },
    "hop-dong-lao-dong-va-hoc-viec-mau.pdf": {
        "title": "MẪU HỢP ĐỒNG LAO ĐỘNG VÀ QUY ĐỊNH HỢP ĐỒNG HỌC VIỆC THỰC TẬP",
        "customer_role": "seller",
        "content": """MẪU HỢP ĐỒNG LAO ĐỘNG VÀ QUY ĐỊNH HỢP ĐỒNG HỌC VIỆC THỰC TẬP

Metadata: customer_role=seller

1. HỢP ĐỒNG HỌC VIỆC VÀ THỰC TẬP TRONG DOANH NGHIỆP (ĐIỀU 61, 62 BỘ LUẬT LAO ĐỘNG 2019)
- Hợp đồng đào tạo/học việc phải ký bằng văn bản nếu thời gian học việc từ 01 tháng trở lên.
- Mức lương trong thời gian học việc do hai bên thỏa thuận. Trường hợp người học việc trực tiếp làm ra sản phẩm hoặc thực hiện công việc kinh doanh cho doanh nghiệp thì phải được trả lương theo mức hai bên thỏa thuận không thấp hơn mức lương tối thiểu vùng.

2. CÁC ĐIỀU KHOẢN BẮT BUỘC TRONG HỢP ĐỒNG LAO ĐỘNG (ĐIỀU 21)
- Tên, địa chỉ của người sử dụng lao động và họ tên, ngày tháng năm sinh, số CCCD của người lao động.
- Công việc và địa điểm làm việc.
- Thời hạn của hợp đồng lao động.
- Mức lương theo công việc hoặc chức danh, hình thức trả lương, thời hạn trả lương, phụ cấp lương và các khoản bổ sung khác.
- Chế độ nâng bậc, nâng lương, thời giờ làm việc, thời giờ nghỉ ngơi, trang bị bảo hộ lao động.
- Bảo hiểm xã hội (BHXH), bảo hiểm y tế (BHYT) và bảo hiểm thất nghiệp (BHTN).
"""
    }
}


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


def remove_vietnamese_diacritics(text: str) -> str:
    """Chuyển tiếng Việt có dấu thành không dấu để tương thích với font PDF Helvetica standard."""
    import unicodedata
    nfd = unicodedata.normalize('NFD', text)
    cleaned = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    cleaned = cleaned.replace('Đ', 'D').replace('đ', 'd')
    return cleaned


def create_pdf_file(filepath: Path, title: str, content: str):
    """Tạo file PDF hợp lệ (>1KB) phục vụ MarkItDown convert ở Task 3."""
    ascii_content = remove_vietnamese_diacritics(content)
    lines = ascii_content.split('\n')
    text_stream_lines = []
    y = 750
    for line in lines:
        if not line.strip():
            y -= 12
            continue
        safe_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        text_stream_lines.append(f"1 0 0 1 50 {y} Tm ({safe_line}) Tj")
        y -= 14
        if y < 50:
            y = 750

    stream_content = "\n".join(text_stream_lines)
    stream_len = len(stream_content.encode('utf-8'))

    pdf_body = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length {stream_len} >>
stream
BT
/F1 10 Tf
{stream_content}
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000315 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
{315 + stream_len + 40}
%%EOF
"""
    filepath.write_bytes(pdf_body.encode('utf-8'))
    print(f"[OK] Da tao PDF Luat Lao Dong: {filepath.name} ({filepath.stat().st_size} bytes)")


def collect_legal_docs():
    """Tạo bộ tài liệu quy định Luật Lao động 2019."""
    setup_directory()
    for filename, info in DOCUMENTS.items():
        filepath = DATA_DIR / filename
        create_pdf_file(filepath, info["title"], info["content"])
    print(f"[OK] Hoan thanh Task 1: Da tao {len(DOCUMENTS)} file quy dinh Luat Lao dong trong {DATA_DIR}")


if __name__ == "__main__":
    collect_legal_docs()
