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

**Một lần duy nhất trước khi bắt đầu (T0.3, ~10 phút):**
1. Chạy app — **Docker (môi trường chính)**: `docker compose up -d` → mở `http://localhost:7000` login. *(Dự phòng khi Docker trục trặc: `launch-windows.ps1` chạy native, cần Python 3.11+ — chi tiết xem CLAUDE.md.)*
2. T0.3: bật LM Studio server bind `0.0.0.0:1234` → Settings → thêm endpoint `http://host.docker.internal:1234/v1` → gửi 1 câu chat tiếng Việt, phản hồi < 30s. *(Nếu chạy native thì endpoint là `http://localhost:1234/v1`, bind mặc định là đủ.)*
3. T0.4 đã pass trong Docker (ntfy) — không cần làm lại.

**Sáng (5 phút):**
1. Kiểm tra Morning check-in 7h: có đến không? đúng giờ? nội dung hữu ích hay rỗng tuếch? → ghi bảng metric. **Lưu ý:** app phải đang chạy lúc 7h — nếu PC thường bật muộn hơn, đổi giờ check-in sang giờ bạn chắc chắn đã ngồi máy (vd. 8h30) trong Tasks.
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

## Lộ trình gợi ý 4 ngày (mỗi ngày nhắm một vùng gap)

**Ngày 1 — Lịch & tiếng Việt cơ bản:**
- Tạo 3-5 event/reminder bằng tiếng Việt đa dạng: *"mai 7h tối gọi mẹ"*, *"thứ 6 tuần sau họp đồ án"*, *"mốt deadline báo cáo"*, *"cuối tháng đóng tiền nhà"* → mở Calendar đối chiếu từng cái, ghi tỷ lệ đúng/tổng.
- Hỏi: *"hôm nay tôi có gì?"*, *"tuần này tôi bận những hôm nào?"*
- Nhờ nhớ 1 thông tin: *"nhớ là tôi đang học môn X, thi ngày Y"*.

**Ngày 2 — Agent làm việc thật & quản lý lịch qua chat:**
- Hỏi lại thông tin hôm qua (memory có nhớ không?).
- Nhờ agent: tìm web + tóm tắt 1 bài viết; giải thích 1 đoạn code đang học.
- **Sửa lịch bằng chat**: *"dời buổi X sang 9h sáng"*, *"hủy reminder Y"* → kiểm tra Calendar có cập nhật thật không.
- Tạo todo cho một việc thật, cuối ngày tick done.

**Ngày 3 — Tài liệu & tình huống phức:**
- Upload 1 PDF thật (lịch học, syllabus, bài báo có deadline) → *"trích các ngày quan trọng và thêm vào lịch"* → đếm: trích đúng / sót / sai giờ.
- Hỏi đáp 2-3 câu trên nội dung tài liệu vừa upload.
- **Thử conflict**: tạo 2 event trùng giờ → hệ thống có cảnh báo gì không? (dự đoán: không — đây chính là gap mà Planner P2b sẽ lấp, ghi lại làm bằng chứng).

**Ngày 4 — Tái hiện gap & chốt sổ:**
- Lặp lại các thao tác đã ghi gap ở ngày 1-3 → xác nhận gap tái hiện được (gap thật, không phải lỗi ngẫu nhiên 1 lần).
- Hỏi lại memory thông tin từ Ngày 1 (trí nhớ dài hơn 3 ngày?).
- Rà bảng metric 4 ngày, chốt ≥ 5 gap có mô tả cụ thể → báo Claude audit exit criteria P0 và điều chỉnh P1.

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

### G-01: Chat thường không tạo được lịch — model trả lời "không có quyền truy cập"
- **Ngày:** 2026-06-12
- **Tình huống:** Chat thường (không phải Agent mode) với qwen3-4b: "hãy thêm cho tôi một lịch ngày mai vào 2h chiều với đầu mục: 'đi với lớp thạc sĩ'"
- **Mong đợi:** Event xuất hiện trong Calendar.
- **Thực tế:** Model trả lời không có công cụ quản lý lịch, chỉ soạn template để copy tay. **Lưu ý:** tầng ngôn ngữ ĐÚNG hoàn toàn (ngày mai → T7 13/06 ✓, 2h chiều → 14:00 ✓) — vấn đề là chat thường không được cấp tool, không phải model không hiểu tiếng Việt.
- **Ưu tiên:** cao — trợ lý cá nhân không nên bắt user nhớ "phải bật agent mode mới thao tác được"
- **Việc cần làm tiếp:** ~~tái test ở Agent mode~~ → đã test, dẫn tới G-02 (nguyên nhân gốc).

### G-02: Intent classifier chỉ hiểu tiếng Anh → câu Việt bị coi là "low signal", agent mất sạch tool domain
- **Ngày:** 2026-06-12
- **Tình huống:** Agent mode + qwen3-4b, 3 phép thử chẩn đoán: (1) "liệt kê công cụ" → model chỉ có đúng bộ ALWAYS_AVAILABLE (`ask_user`, `manage_memory`, `update_plan`); (2) câu tiếng Anh trong cùng chat → vẫn từ chối; (3) nêu đích danh `manage_calendar` → vẫn từ chối.
- **Nguyên nhân gốc (đã xác minh trong code):** `_classify_agent_request` (`src/agent_loop.py:748`) phân loại domain bằng **regex tiếng Anh thuần** — câu Việt không khớp → `low_signal=True` → `agent_loop.py:1802` bỏ qua RAG retrieval, chỉ phát 3 tool mặc định. Test 3 fail vì `\bcalendar\b` không khớp trong `manage_calendar` (underscore = word char). Test 2 (English) nghi do anchoring cùng-chat — chờ xác nhận bằng chat mới.
- **Mong đợi:** Câu tiếng Việt tự nhiên về lịch/note/email phải kích hoạt được tool tương ứng.
- **Ưu tiên:** CAO NHẤT — chặn toàn bộ thao tác agent bằng tiếng Việt, bất kể model nào.
- **Workaround tạm (dùng trong T0.5):** chat mới + chêm từ khóa tiếng Anh vào câu Việt ("thêm vào **calendar**...", "tạo **reminder**...").
- **Hướng vá (P1):** thêm pattern tiếng Việt cho intent classifier qua helper file mới + vá điểm gọi ≤ 15 dòng trong agent_loop.py. **Lưu ý:** lỗi này ảnh hưởng MỌI người dùng non-English → ứng viên tốt để mở issue + PR ngược upstream (GĐ5 roadmap).
- **✅ Xác nhận thực nghiệm (2026-06-12, 23:20):** chat MỚI + tiếng Anh → `MANAGE_CALENDAR done` ✓; chat MỚI + tiếng Việt chêm "calendar" → `MANAGE_CALENDAR done` ✓ (cả model 4B cũng gọi tool ngon khi tool có mặt). Kết hợp với các lần fail trước → chẩn đoán đứng vững: hệ tool lành lặn, thủ phạm là classifier mù tiếng Việt; các lần "tiếng Anh cũng fail" trước đó là do **anchoring cùng-chat** (cùng câu, chat cũ fail — chat mới pass). Workaround chêm từ khóa: **dùng được**.
- **✅ Baseline "trước" cho T1.5 đã chốt (2026-06-12, 23:25, chat mới):** câu thuần Việt → badge `UPDATE_PLAN done` (KHÔNG phải manage_calendar) — model chỉ có 3 tool mặc định nên vớ sai tool, **không event nào được tạo**, nhưng trả lời "Tôi sẽ thêm lịch... vui lòng xác nhận" như thể thành công. Twist quan trọng: thiếu tool ≠ luôn từ chối — model có thể **dùng sai tool rồi báo cáo ảo**, nguy hiểm hơn từ chối vì user tưởng lịch đã có. Verify T1.5 sau này: câu này phải ra `MANAGE_CALENDAR done` + event đúng 13/06 14:00.

### G-03: Event tạo từ câu tiếng Việt bị lệch +1 ngày ("ngày mai" → ngày kia)
- **Ngày:** 2026-06-12
- **Tình huống:** 23:21, chat mới, "Thêm vào calendar ngày mai 14h: đi với lớp thạc sĩ" → `MANAGE_CALENDAR done`, model xác nhận thành công.
- **Mong đợi:** Event thứ Bảy 13/06 14:00.
- **Thực tế:** Event nằm ở **Chủ Nhật 14/06** 14:00 — lệch +1 ngày. Đối chứng: câu tiếng Anh "tomorrow at 2pm" (23:20, cùng tối) ra **đúng** 13/06 14:00. Cùng tool, cùng model — chỉ khác ngôn ngữ input.
- **Ưu tiên:** CAO — lỗi âm thầm (không báo lỗi, chỉ sai ngày); với trợ lý lịch, sai ngày tệ hơn từ chối.
- **Nghi phạm:** chuỗi due model phát ra ("ngày mai 14h"?) đi qua `parse_due_for_user` (routes/calendar_routes.py — heuristic + dateutil, KHÔNG hiểu tiếng Việt) hoặc lệch timezone khi diễn giải. Đúng vùng T1.2 + mục timezone của P1.
- **✅ Bằng chứng bổ sung (log 23:21):** event lưu thật 14/06 14:00–15:00 (không phải lỗi hiển thị); `Tool executed: manage_calendar -> exit_code=0` → lỗi nằm ở **giá trị due trong args**. Giả thuyết mạnh: model truyền chuỗi chứa "ngày mai 14h" → `parse_due_for_user` không hiểu "ngày mai" → dateutil vớ số "14" làm **ngày-của-tháng** → 14/06 14:00. T1.2 xác nhận khi điều tra.

### G-04: Máy native cấu hình ChromaDB kiểu Docker → vector tool-RAG chết, keyword fallback gánh toàn bộ
- **Ngày:** 2026-06-12 (phát hiện qua log T0.3)
- **Tình huống:** Log mỗi message agent: `ToolIndex init failed (will retry in 30.0s): ChromaDB is not reachable at localhost:8100`.
- **Nguyên nhân (đính chính 2026-06-12):** codebase **KHÔNG có chế độ ChromaDB embedded** — `src/chroma_client.py` chỉ là HTTP client (mặc định `localhost:8100`), `requirements.txt` chỉ cài `chromadb-client`. Comment `.env` không đổi được gì vì 8100 là default trong code. Máy native đơn giản là **chưa có ChromaDB server nào chạy**.
- **Hệ quả:** tool selection chỉ còn keyword fallback (tiếng Anh) — tầng vector semantic không chạy. Memory vector có thể cũng bị ảnh hưởng (cần kiểm tra recall chất lượng).
- **Ưu tiên:** trung — hệ vẫn chạy nhờ fallback, nhưng làm sai lệch mọi đánh giá về retrieval; **phải fix trước khi đo eval P2**.
- **Cách fix (native, không Docker):** chạy ChromaDB server bằng CLI trong **venv riêng** (cài full `chromadb` chung venv app sẽ xung đột `chromadb-client` — cảnh báo trong README): `py -3.11 -m venv chroma-venv` → `chroma-venv\Scripts\pip install chromadb` → `chroma-venv\Scripts\chroma run --host 127.0.0.1 --port 8100 --path .\data\chromadb`. App tự retry sau 30s → log phải hiện `ChromaDB connected` + `ToolIndex initialized`.
- **Hệ quả thiết kế cho T1.5:** Việt hóa phải phủ CẢ `_KEYWORD_HINTS` lẫn domain regex (không được dựa vào tầng vector, vì nó có thể chết âm thầm như vừa thấy).

