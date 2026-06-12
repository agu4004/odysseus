# Gap Log — P0 Usage Report

> Ghi lại các điểm bất tiện, thiếu sót, hoặc kỳ vọng chưa được đáp ứng khi dùng Odysseus thật sự.
> Mỗi mục cần: **mô tả cụ thể** (tình huống gì, mong đợi gì, thực tế ra sao) — không đoán chung chung.
> File này là input để điều chỉnh P1. Cần ≥ 5 mục để đạt exit criteria P0.

---

## Hướng dẫn điền

```
### G-XX: [Tiêu đề ngắn]
- **Ngày:** YYYY-MM-DD
- **Tình huống:** Tôi đang làm gì...
- **Mong đợi:** Tôi muốn Odysseus...
- **Thực tế:** Điều gì xảy ra thay thế...
- **Ưu tiên:** cao / trung / thấp
```

---

## Kịch bản dùng thật hằng ngày (~15-20 phút/ngày)

> Mục tiêu của T0.5 KHÔNG phải kiểm tra hệ thống chạy được — mà là **tìm chỗ nó làm bạn khó chịu**. Mỗi lần bạn định nhờ trợ lý nhưng rồi tự làm tay = 1 gap tiềm năng. Chỉ ghi điều đã xảy ra thật, không đoán.

**Một lần duy nhất trước khi bắt đầu (môi trường native — Docker không khởi động được, 10 phút):**
1. Chạy app: `powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1` → mở `http://localhost:7000` login (lần đầu sẽ cài venv + deps, các lần sau nhanh).
2. T0.3: bật LM Studio server (mặc định `localhost:1234` là đủ — không cần `0.0.0.0` khi chạy native) → Settings → thêm endpoint `http://localhost:1234/v1` → gửi 1 câu chat tiếng Việt, phản hồi < 30s.
3. T0.4: tạo 1 reminder thử trong Notes → xác nhận browser notification hiện trên PC (hoặc cấu hình topic ntfy.sh nếu thích).

**Sáng (5 phút):**
1. Kiểm tra Morning check-in 7h: có đến không? đúng giờ? nội dung hữu ích hay rỗng tuếch? → ghi bảng metric. **Lưu ý native:** app phải đang chạy lúc 7h — nếu PC/app thường bật muộn hơn, đổi giờ check-in sang giờ bạn chắc chắn đã ngồi máy (vd. 8h30) trong Tasks.
2. Hỏi chat: *"Hôm nay tôi có gì?"* — xem trợ lý nắm lịch/task của bạn đến đâu.

**Trong ngày (dùng tự nhiên, không gò ép):**
3. Có việc/hẹn mới → tạo qua chat bằng **tiếng Việt tự nhiên**: *"nhắc tôi mai 7h tối gọi điện cho mẹ"*, *"thứ 6 tuần sau họp đồ án"*, *"mốt deadline nộp báo cáo"* → kiểm tra trong Calendar/Notes xem ngày giờ có đúng không. Đây là phép thử trực tiếp cho P1 — ghi từng lần đúng/sai.
4. Nhờ agent làm ≥ 1 việc thật: tìm kiếm web, tóm tắt bài viết, giải thích đoạn code.
5. Nhờ nhớ 1 thông tin: *"nhớ là tôi đang học môn X, thi ngày Y"* → **hôm sau** hỏi lại xem có nhớ không.
6. Ghi 1-2 note/todo, tick hoàn thành cuối ngày.

**Tối (5 phút):**
7. App còn sống không (`http://localhost:7000` phản hồi)? Hôm nay có lần nào crash giữa chừng / phải khởi động lại không → ghi số lần.
8. Gặp gap hôm nay → điền theo template G-XX ở trên (điền NGAY, để qua ngày sẽ quên chi tiết).
9. Điền 1 dòng bảng metric bên dưới.

## Bảng theo dõi metric hằng ngày

| Ngày | Check-in (đến? đúng giờ?) | Parse t.Việt (đúng/tổng lần thử) | "Hôm nay có gì?" đạt? | Memory nhớ lại đúng? | App crash/restart | Gap mới |
|---|---|---|---|---|---|---|
| Ngày 1 | | /  | | (chưa có) | | |
| Ngày 2 | | /  | | | | |
| Ngày 3 | | /  | | | | |
| Ngày 4 | | /  | | | | |

**Điều kiện đóng P0 (đối chiếu execution_plan.md, bản native 2026-06-12):** ≥ 5 gap cụ thể bên dưới · ≥ 3 ngày dùng thật với 0 crash giữa lúc dùng, app khởi động ≤ 2 phút · T0.3 + T0.4 (native) đã pass.

---

## Danh sách Gap

<!-- Điền vào sau 3-4 ngày dùng thật. Xóa dòng này khi có đủ 5 mục. -->

