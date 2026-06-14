"""Vietnamese-language domain signals for agent intent classifier.

Companion to the English regex patterns in agent_loop._classify_agent_request.
All domain names returned must match keys in agent_loop._DOMAIN_TOOL_MAP so that
the domain-tool injection at line ~1867 of agent_loop.py picks the right tools.

Design: liberal matching is intentional — the cost of a false-positive (an extra
tool in context) is much lower than the cost of a false-negative (no tool at all,
causing the model to fabricate an answer or use the wrong tool silently).

Upstream-PR candidate: gap G-02 affects every non-English user of Odysseus.
"""
from __future__ import annotations

import re
from typing import Set

# ---------------------------------------------------------------------------
# Per-domain compiled patterns.  Evaluated on the *lowercased* query text,
# same as the English classifier (q = retrieval_query.lower() in agent_loop).
# ---------------------------------------------------------------------------

# notes_calendar_tasks — lịch, sự kiện, ghi chú, nhắc nhở, việc cần làm
_CALENDAR_NOTES_RE = re.compile(
    r"(?:"
    r"lịch\b"                            # lịch: calendar / schedule
    r"|sự kiện"                          # event
    r"|cuộc hẹn"                         # appointment
    r"|cuộc họp"                         # meeting
    r"|hẹn gặp"                          # rendezvous / meet-up
    r"|kế hoạch\b"                       # plan
    r"|nhắc\b|nhắc nhở|nhắc tôi"        # remind / reminder
    r"|ghi chú"                          # note
    r"|ghi lại\b"                        # write down / log
    r"|ghi nhớ\b"                        # memorise / remember
    r"|việc cần"                         # to-do (việc cần làm)
    r"|danh sách\s+(?:việc|mua|làm|task)"  # task list / shopping list
    r"|deadline\b|hạn nộp|hạn chót"     # deadline
    r"|đặt lịch|thêm lịch|tạo lịch|xem lịch|hủy lịch|dời lịch"  # calendar CRUD verbs
    r")"
)

# web — tìm kiếm, tra cứu, giá thị trường, tin tức, thời tiết
_WEB_RE = re.compile(
    r"(?:"
    r"tìm kiếm"                          # search
    r"|tra cứu|tra thông tin"            # look up
    r"|tìm\s+(?:hiểu|thông tin|giá|cách|ra|kiếm)"  # find-out / search for
    r"|giá\s+(?:vàng|xăng|đô|usd|bitcoin|cổ phiếu|bất động sản|nhà đất)"  # market prices
    r"|tỷ giá\b"                         # exchange rate
    r"|thời tiết\b"                      # weather
    r"|dự báo\b"                         # forecast
    r"|tin tức\b"                        # news
    r"|mới nhất\b"                       # latest
    r")"
)

# email — thư điện tử / hộp thư
_EMAIL_RE = re.compile(
    r"(?:"
    r"(?:gửi|đọc|xem|trả lời|kiểm tra|soạn|viết)\s+(?:email|thư|tin nhắn)"
    r"|hộp thư\b|hòm thư\b"             # mailbox
    r"|email mới\b|thư mới\b"           # new email
    r"|thư đến\b|thư đi\b"              # inbox / outbox
    r")"
)

# documents — soạn thảo văn bản
_DOCUMENTS_RE = re.compile(
    r"(?:"
    r"soạn\s+(?:bài|báo cáo|tài liệu|văn bản|thư|email)"
    r"|viết\s+(?:bài|báo cáo|luận văn|essay|outline|bản thảo)"
    r"|bản thảo\b|bản nháp\b"           # draft
    r"|biên soạn\b|biên tập\b"          # compose / edit (formal)
    r")"
)

# ui — giao diện, chủ đề, dark/light mode
_UI_RE = re.compile(
    r"(?:"
    r"(?:bật|tắt|mở|đóng|chuyển)\s+(?:giao diện|chế độ|sidebar|panel|theme|chủ đề)"
    r"|giao diện\s+(?:tối|sáng)"
    r"|dark mode\b|light mode\b"
    r"|chủ đề\s+(?:tối|sáng|đen|trắng)"
    r")"
)

# settings — cài đặt, thiết lập, cấu hình
_SETTINGS_RE = re.compile(
    r"(?:"
    r"cài đặt\b"                         # settings
    r"|thiết lập\b"                      # setup / configure
    r"|cấu hình\b"                       # configure
    r"|thay đổi\s+(?:cài đặt|thiết lập|model|giọng nói)"
    r"|model mặc định\b|giọng đọc\b"
    r")"
)

# files — tệp tin, thư mục, lệnh shell
_FILES_RE = re.compile(
    r"(?:"
    r"(?:đọc|mở|xem|tìm|xóa|tạo|chỉnh sửa)\s+(?:tệp|file|thư mục|folder)"
    r"|tệp tin\b"                        # file
    r"|chạy\s+(?:script|lệnh|terminal|bash|code)"  # run command
    r")"
)

# sessions — lịch sử trò chuyện, đổi tên/xóa session
_SESSIONS_RE = re.compile(
    r"(?:"
    r"(?:đổi tên|xóa|lưu trữ|ẩn)\s+(?:cuộc trò chuyện|chat|phiên|session)"
    r"|lịch sử\s+(?:chat|trò chuyện)"   # chat history
    r"|cuộc trò chuyện\s+(?:cũ|trước|này)"
    r")"
)

_DOMAIN_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("notes_calendar_tasks", _CALENDAR_NOTES_RE),
    ("web",                  _WEB_RE),
    ("email",                _EMAIL_RE),
    ("documents",            _DOCUMENTS_RE),
    ("ui",                   _UI_RE),
    ("settings",             _SETTINGS_RE),
    ("files",                _FILES_RE),
    ("sessions",             _SESSIONS_RE),
]


def classify_vietnamese_intent(text: str) -> Set[str]:
    """Return the set of domain names matched by Vietnamese-language patterns.

    Caller: agent_loop._classify_agent_request — call with ``q`` (the already-
    lowercased retrieval query) and merge the result into the ``domains`` set::

        domains.update(classify_vietnamese_intent(q))

    When the returned set is non-empty, ``domains`` becomes non-empty and
    ``low_signal = not continuation and not domains`` evaluates to False,
    allowing the full RAG/keyword tool-retrieval pipeline to run.
    """
    matched: Set[str] = set()
    for domain, pattern in _DOMAIN_PATTERNS:
        if pattern.search(text):
            matched.add(domain)
    return matched
