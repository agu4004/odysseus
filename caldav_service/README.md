# caldav_service — Decommissioned 2026-06-12

**Trạng thái: KHÔNG CHẠY — giữ lại làm tài liệu học RFC 4791.**

## Lý do bỏ

Không có nhu cầu sync lịch đa thiết bị trong kiến trúc hiện tại:
- Odysseus chạy trên 1 máy, calendar là local-first (SQLite).
- Nhu cầu "nắm hoạt động hôm nay" được phủ bởi daily briefing (ntfy) + agenda digest (composeContext P2b) + hỏi trong chat.
- Planner (P2b) sẽ ghi lịch qua Odysseus calendar REST API sau interface `CalendarExporter` — nếu tương lai cần đa thiết bị thì chỉ thêm `CaldavExporter` + Radicale mà không sửa logic planner.

Xem bảng "Quyết định đã chốt" trong [roadmap_assistance.md](../roadmap_assistance.md).

## Nội dung

`server.py` là implementation RFC 4791 subset (~230 dòng Starlette thuần):
- PROPFIND discovery chain (root → principal → calendar-home-set → list calendars)
- REPORT calendar-query (time-range) + calendar-multiget
- MKCALENDAR, GET/HEAD, PUT, DELETE, OPTIONS
- Basic Auth, flat `.ics` file storage, ETag qua MD5

Đây là tài liệu học giao thức CalDAV/WebDAV — không cần chạy production.
