"""Tests for src/vietnamese_intent.py — Vietnamese-language domain classifier.

Each test asserts:
  1. The expected domain(s) appear in the result.
  2. The result is non-empty — meaning low_signal=False when merged into agent
     domains (i.e., agent gains access to domain tools, not just ALWAYS_AVAILABLE).

Taxonomy: area_unit (pure function, no I/O, no fixtures).
"""
import pytest

from src.vietnamese_intent import classify_vietnamese_intent

pytestmark = pytest.mark.area_unit


# ---------------------------------------------------------------------------
# notes_calendar_tasks domain
# ---------------------------------------------------------------------------

def test_calendar_add_explicit():
    """'thêm lịch' phrase must trigger calendar domain."""
    result = classify_vietnamese_intent("thêm lịch ngày mai 14h: đi với lớp thạc sĩ")
    assert "notes_calendar_tasks" in result
    assert result, "non-empty → low_signal=False"


def test_calendar_schedule_meeting():
    """'đặt lịch họp' must trigger calendar domain."""
    result = classify_vietnamese_intent("đặt lịch họp nhóm thứ 6 tuần sau lúc 10h sáng")
    assert "notes_calendar_tasks" in result
    assert result


def test_calendar_appointment_via_hen():
    """'hẹn gặp' must trigger calendar domain."""
    result = classify_vietnamese_intent("hẹn gặp khách hàng vào thứ 3 lúc 2 giờ chiều")
    assert "notes_calendar_tasks" in result
    assert result


def test_reminder_nhacc():
    """'nhắc tôi' must trigger calendar/notes domain."""
    result = classify_vietnamese_intent("nhắc tôi gọi điện cho mẹ lúc 7h tối nay")
    assert "notes_calendar_tasks" in result
    assert result


def test_note_ghi_chu():
    """'tạo ghi chú' must trigger notes domain."""
    result = classify_vietnamese_intent("tạo ghi chú nhắc tôi mua quà sinh nhật")
    assert "notes_calendar_tasks" in result
    assert result


def test_deadline_keyword():
    """'deadline' must trigger calendar/task domain."""
    result = classify_vietnamese_intent("deadline nộp bài thi là 23h59 ngày 30 tháng 6")
    assert "notes_calendar_tasks" in result
    assert result


def test_meeting_cuoc_hop():
    """'cuộc họp' must trigger calendar domain."""
    result = classify_vietnamese_intent("cuộc họp đồ án thứ 5 tuần sau 8h sáng")
    assert "notes_calendar_tasks" in result
    assert result


# ---------------------------------------------------------------------------
# web domain
# ---------------------------------------------------------------------------

def test_web_search_gia_vang():
    """'tìm giá vàng' must trigger web/search domain."""
    result = classify_vietnamese_intent("tìm giá vàng hôm nay")
    assert "web" in result
    assert result


def test_web_search_tim_kiem():
    """'tìm kiếm' must trigger web domain."""
    result = classify_vietnamese_intent("tìm kiếm thông tin về AI mới nhất")
    assert "web" in result
    assert result


def test_web_weather():
    """'thời tiết' must trigger web domain."""
    result = classify_vietnamese_intent("thời tiết hà nội ngày mai thế nào")
    assert "web" in result
    assert result


def test_web_ty_gia():
    """'tỷ giá' must trigger web domain."""
    result = classify_vietnamese_intent("tỷ giá đô la hôm nay là bao nhiêu")
    assert "web" in result
    assert result


# ---------------------------------------------------------------------------
# email domain
# ---------------------------------------------------------------------------

def test_email_send():
    """'gửi email' must trigger email domain."""
    result = classify_vietnamese_intent("gửi email cho sếp báo cáo tiến độ dự án")
    assert "email" in result
    assert result


def test_email_read_hop_thu():
    """'đọc thư mới trong hộp thư' must trigger email domain."""
    result = classify_vietnamese_intent("đọc thư mới trong hộp thư của tôi")
    assert "email" in result
    assert result


# ---------------------------------------------------------------------------
# documents domain
# ---------------------------------------------------------------------------

def test_documents_soan_bao_cao():
    """'soạn báo cáo' must trigger documents domain."""
    result = classify_vietnamese_intent("soạn báo cáo tháng 6 về kết quả học tập")
    assert "documents" in result
    assert result


# ---------------------------------------------------------------------------
# settings domain
# ---------------------------------------------------------------------------

def test_settings_cai_dat():
    """'cài đặt' must trigger settings domain."""
    result = classify_vietnamese_intent("cài đặt model mặc định cho agent")
    assert "settings" in result
    assert result


# ---------------------------------------------------------------------------
# Multi-domain
# ---------------------------------------------------------------------------

def test_multi_domain_web_and_calendar():
    """'tra cứu ... và thêm ... lịch' must trigger both web and calendar."""
    result = classify_vietnamese_intent(
        "tra cứu giá vàng và thêm lịch nhắc nhở mua vàng vào thứ 6"
    )
    assert "web" in result
    assert "notes_calendar_tasks" in result
    assert result


# ---------------------------------------------------------------------------
# Negative cases — chitchat / low-signal Vietnamese must NOT create domains
# ---------------------------------------------------------------------------

def test_chitchat_xin_chao_returns_empty():
    """Bare greeting must not match any domain (low_signal stays True)."""
    result = classify_vietnamese_intent("xin chào")
    assert result == set(), f"Expected empty set, got {result}"


def test_chitchat_ban_ten_gi_returns_empty():
    """'bạn tên là gì' is chitchat — no domain tools needed."""
    result = classify_vietnamese_intent("bạn tên là gì")
    assert result == set(), f"Expected empty set, got {result}"
