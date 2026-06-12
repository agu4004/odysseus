# CLAUDE.md

## Project là gì

Odysseus — AI workspace tự host (FastAPI + vanilla JS): chat đa model, agent có tool, deep research, email/calendar/notes/tasks, memory, MCP. Đây là **fork cá nhân** (`origin` = agu4004, `upstream` = pewdiepie-archdaemon) đang phát triển theo hướng **trợ lý cá nhân + Second Brain** — đọc [roadmap_assistance.md](roadmap_assistance.md) trước khi làm feature riêng. SDD của Second Brain (service Java/Spring đi kèm: kho fact, planner, Telegram gateway) nằm ở [plan.md](plan.md). **Khi được giao code theo roadmap: làm theo [execution_plan.md](execution_plan.md)** — task tuần tự, verify bằng lệnh ghi sẵn, tick checkbox + ghi Nhật ký, không sang phase khi exit criteria chưa đạt.

## Quy tắc fork (quan trọng nhất)

- Branch `dev` giữ **sạch** chỉ để sync upstream; mọi thay đổi riêng vào branch `my-features`.
- **Chạm nông**: ưu tiên thêm file mới thay vì sửa file lớn của upstream (`agent_loop.py`, `static/js/app.js`...) để merge upstream không đau.
- Logic riêng phức tạp **không viết vào Python** — viết thành service Spring Boot bên ngoài, expose qua MCP (Streamable HTTP). Phía Python chỉ là điểm cắm mỏng.
- **Không bao giờ refactor Odysseus sang Java** (đã chốt — xem roadmap): mất sync upstream, tốn nhiều tháng, không học được gì. Nếu logic Python riêng phình to (>vài trăm dòng, có business logic) → dời sang Spring Boot qua MCP, không refactor tại chỗ.
- Sync upstream: `git fetch upstream && git checkout dev && git merge upstream/dev`, rồi merge `dev` vào `my-features`. Luồng MỘT chiều: upstream → dev → my-features; **không bao giờ merge my-features vào dev**, không dùng nút "Sync fork"/"Contribute" trên GitHub (sự cố 2026-06-12: PR #1 làm bẩn dev, phải force-push dọn lại).

## Kiến trúc

- [app.py](app.py) — slim orchestrator, chỉ wiring; khởi tạo thật nằm ở [src/app_initializer.py](src/app_initializer.py).
- [routes/](routes/) — ~50 module HTTP API theo domain (chat, email, calendar, cookbook, mcp, memory...). Helper dùng chung của domain nằm cạnh (`*_helpers.py`).
- [src/](src/) — logic lõi:
  - Agent: [agent_loop.py](src/agent_loop.py), tool schema ở [tool_schemas.py](src/tool_schemas.py), implementation ở [tool_implementations.py](src/tool_implementations.py) + [agent_tools/](src/agent_tools/).
  - **Tool selection bằng RAG top-K** ([tool_index.py](src/tool_index.py)) — tool (kể cả MCP tool) chỉ "hiện ra" với agent nếu description khớp ngữ nghĩa message. Description tool mới phải giàu từ khóa, song ngữ Việt–Anh.
  - MCP client: [mcp_manager.py](src/mcp_manager.py) — hỗ trợ stdio / SSE / Streamable HTTP (+OAuth).
  - **Memory provider seam**: [memory_provider.py](src/memory_provider.py) — interface chính thức để cắm kho memory ngoài; đăng ký registry tại app_initializer.py (~dòng 77). Đây là điểm cắm Second Brain.
  - Scheduler: [task_scheduler.py](src/task_scheduler.py) — cron task, IANA timezone per-task, đẩy ntfy.
- [services/](services/) — service lớn: search (SearXNG + ranking), hwfit (scan phần cứng), research, stt/tts, shell.
- [core/](core/) — auth, database, middleware, session.
- [static/js/](static/js/) — frontend ES modules, không framework.
- [mcp_servers/](mcp_servers/) — MCP server built-in (email, memory, rag, image_gen).

## Lệnh thường dùng

```bash
# Máy dev CHẠY ĐƯỢC Docker — Docker là môi trường chính
docker compose up -d --build
docker compose logs --tail=120 odysseus

# Dự phòng không-Docker (chính thức, dùng khi Docker trục trặc): cần Python 3.11+,
# chạy launch-windows.ps1 (tự tạo venv+deps). Khác biệt ở chế độ native:
#   ChromaDB: KHÔNG có embedded mode (src/chroma_client.py chỉ là HTTP client → localhost:8100).
#     Native phải tự chạy server: venv RIÊNG (tránh xung đột chromadb-client) →
#     `pip install chromadb` → `chroma run --host 127.0.0.1 --port 8100 --path .\data\chromadb`.
#     Thiếu nó: vector tool-RAG/memory chết âm thầm, keyword fallback gánh (xem gap G-04).
#   ntfy→browser notification hoặc ntfy.sh · LM Studio chỉ cần localhost:1234
#   Cookbook đầy đủ cần Git for Windows (bash.exe) · vLLM/SGLang serve cần WSL2
python -m uvicorn app:app --host 127.0.0.1 --port 7000

# Test — chạy phần nhỏ nhất liên quan đến thay đổi
python -m pytest                          # toàn bộ
python -m pytest -m "not slow"            # fast lane
python -m pytest -m area_routes           # theo taxonomy: area_security / area_routes / area_services / ...
python -m py_compile app.py routes/*.py src/*.py
node --check static/js/<file-đã-sửa>.js
```

Test taxonomy khai báo trong [pyproject.toml](pyproject.toml); chuẩn viết test xem [tests/TESTING_STANDARD.md](tests/TESTING_STANDARD.md).

## Quy ước & lưu ý

- Máy dev là **Windows 11** (PowerShell); codebase có nhiều workaround Windows (MIME types, HF symlinks, BOM trong `.env`) — đừng xóa khi refactor.
- Người dùng làm việc bằng **tiếng Việt**; tính năng ngôn ngữ (parse ngày giờ, prompt) phải test với mẫu câu Việt ("mai", "mốt", "tuần sau", "7h tối thứ 6"). Timezone chuẩn: `Asia/Ho_Chi_Minh`.
- Parse thời gian tự nhiên của calendar nằm ở `parse_due_for_user` trong [routes/calendar_routes.py](routes/calendar_routes.py) (heuristic + dateutil, chưa hiểu tiếng Việt).
- Memory 2 tầng: memory nội bộ (`manage_memory`, ChromaDB) = ngữ cảnh ngắn hạn; Second Brain (qua MCP/provider) = tri thức dài hạn có duyệt. Đừng trộn.
- Nếu định PR ngược lên upstream: PR nhỏ, mở issue trước, base = `dev` (xem [CONTRIBUTING.md](CONTRIBUTING.md)).
- Chủ project specialized **Java/Spring**, đang học **master AI**; giải thích phần Python ở mức đọc-hiểu là đủ, phần thiết kế sâu dồn về phía Java.

## Bảo trì tài liệu sau mỗi session

"Phiên" = một **session** (cuộc hội thoại), không phải từng message. Mỗi khi hoàn thành một khối việc đáng kể trong session (phân tích lớn, quyết định mới, xong hạng mục roadmap), **tự phân tích và đánh giá** xem có thông tin nào nên ghi lại để session sau không phải khám phá lại (tiết kiệm token + thời gian):

- **Ghi vào file này**: quy ước mới, lệnh hay dùng, phát hiện kiến trúc bền vững (seam, file quan trọng, caveat), quyết định kỹ thuật đã chốt.
- **Ghi vào [roadmap_assistance.md](roadmap_assistance.md)**: tiến độ các giai đoạn (tick checkbox), quyết định mới vào bảng "Quyết định đã chốt", phát hiện làm thay đổi kế hoạch.
- **Không ghi**: chi tiết chỉ liên quan phiên hiện tại, thông tin suy ra được từ code/git, nội dung trùng lặp.
- Giữ file này **ngắn gọn** — nó được nạp vào context mỗi phiên, mỗi dòng thừa là token trả phí lặp lại. Khi thêm mục mới, cân nhắc xóa/gộp mục cũ đã lỗi thời.
- Đề xuất cập nhật cho người dùng xác nhận khi thay đổi mang tính quyết định; sửa trực tiếp khi chỉ là bổ sung sự kiện khách quan.
