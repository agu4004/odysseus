# EXECUTION PLAN — Kiểm soát tiến trình AI code

> **Mục đích:** tài liệu điều khiển để AI coder (Claude Code) làm việc qua nhiều session mà không lệch hướng. Mỗi task có requirement + cách verify; mỗi phase có exit criteria đo được. **AI không được tự ý sang phase mới khi exit criteria phase trước chưa đạt.**
>
> Tài liệu gốc: [roadmap_assistance.md](roadmap_assistance.md) (chiến lược, quyết định đã chốt) · [plan.md](plan.md) (SDD Second Brain) · [CLAUDE.md](CLAUDE.md) (quy tắc làm việc).
> **Version:** 1.0 | 2026-06-12

---

## 0. QUY TẮC VẬN HÀNH CHO AI CODER

### 0.1 Trước khi làm bất kỳ task nào
1. Đọc bảng **Dashboard** (§1) xác định phase hiện tại; chỉ làm task trong phase đó, theo thứ tự.
2. Kiểm tra branch: `git branch --show-current` phải là `my-features` (trừ T0.1). Nếu đang ở `dev` → dừng, chuyển branch trước.
3. Đối chiếu task với bảng "Quyết định đã chốt" trong roadmap — nếu phát hiện mâu thuẫn → **dừng, hỏi user**, không tự quyết.

### 0.2 Khi hoàn thành task
1. Chạy đúng **lệnh verify** ghi trong task; chỉ tick ✅ khi verify pass thật (không tick dựa trên "code trông đúng").
2. Cập nhật checkbox + cột Status, ghi một dòng vào **Nhật ký** (§9): ngày, task ID, kết quả verify, metric đo được.
3. Nếu verify fail sau 3 lần thử cách khác nhau → đánh ⛔ blocked, ghi lý do vào Nhật ký, hỏi user.

### 0.3 Guardrails fork (vi phạm = dừng ngay)
- ❌ Không commit lên branch `dev`. Không push khi user chưa yêu cầu.
- ❌ Không sửa file lớn upstream (`agent_loop.py`, `static/js/app.js`, `chat_handler.py`...) — chỉ **thêm file mới**; nếu buộc phải vá file upstream, diff ≤ 15 dòng/file và ghi rõ vào Nhật ký.
- ❌ Không viết business logic mới vào Python — logic riêng thuộc về Second Brain (Java). File Python riêng vượt ~300 dòng có business logic = báo động đặt sai ranh giới.
- ✅ Sau mỗi thay đổi Python: chạy phần test nhỏ nhất liên quan (`pytest -m <area>` hoặc file test cụ thể) + `python -m py_compile <file>`.
- ✅ Secret (bot token, API key) chỉ nằm trong `.env`/env container — grep trước khi commit: không có chuỗi secret trong code.

### 0.4 Ký hiệu trạng thái
⬜ chưa làm · 🔄 đang làm · ✅ xong (verify pass) · ⛔ blocked · ⏭️ bỏ qua có lý do

---

## 1. DASHBOARD

| Phase | Tên | Trạng thái | Tiến độ | Cập nhật |
|---|---|---|---|---|
| P0 | Nền tảng Odysseus | 🔄 | 2/6 (T0.0, T0.1 xong) | 2026-06-12 |
| P1 | Trợ lý Việt hóa | ⬜ | 0/4 | — |
| P2 | Second Brain core (Sprint A-C) | ⬜ | 0/12 | — |
| P2b | Planner + Telegram (Sprint D-E) | ⬜ | 0/9 | — |
| P3 | Chưng cất tri thức (Sprint F-G) | ⬜ | 0/8 | — |
| P4 | Context engineering | ⬜ | 0/4 | — |
| P5 | Backlog | — | — | — |

**Phase hiện tại: P0.**

---

## 2. PHASE 0 — NỀN TẢNG ODYSSEUS (tuần 1)

**Mục tiêu:** hệ thống chạy được, hiểu hiện trạng bằng sử dụng thật.
**Prerequisite:** không.

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T0.0 | Thêm remote upstream | `upstream` = pewdiepie-archdaemon | `git remote -v` có upstream | ✅ |
| T0.1 | Tạo branch `my-features` từ `dev` | Mọi thay đổi riêng từ nay nằm trên branch này; commit 3 file .md hiện có vào đây | `git branch --show-current` → `my-features`; `git status` sạch | ✅ |
| T0.2 | Dựng Docker Compose full stack | `odysseus` + `searxng` + `ntfy` chạy; login được, đổi mật khẩu admin | `docker compose ps` — mọi service healthy; mở `http://localhost:7000` login OK | ⬜ |
| T0.3 | Kết nối model | Ollama (RTX 3070 Ti, model 7-8B quantized) HOẶC OpenRouter; chat trả lời được tiếng Việt | Gửi 1 câu chat trong UI → có phản hồi < 30s | ⬜ |
| T0.4 | CalDAV + ntfy | Radicale (hoặc Google Cal) sync 2 chiều; ntfy app trên điện thoại nhận push | Tạo event trong Odysseus → hiện trên điện thoại; gửi test notification → điện thoại nhận | ⬜ |
| T0.5 | Dùng thật 3-4 ngày, ghi gap list | Bật Personal Assistant + ≥1 scheduled check-in; ghi gap vào `gap_log.md` (file mới) | `gap_log.md` tồn tại, ≥ 5 gap có mô tả cụ thể (không đoán) | ⬜ |

**Exit criteria P0:**
- [ ] Toàn bộ T0.1–T0.5 ✅
- [ ] Metric: stack chạy liên tục ≥ 3 ngày không phải restart thủ công (ghi số lần restart vào Nhật ký)
- [ ] `gap_log.md` có ≥ 5 mục — đây là input điều chỉnh P1

---

## 3. PHASE 1 — TRỢ LÝ VIỆT HÓA (tuần 2-3)

**Mục tiêu:** dùng hàng ngày được. Toàn bộ là vùng chạm nông phía Python.
**Prerequisite:** P0 đạt exit criteria.

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T1.1 | Daily briefing 7h sáng | Scheduled task: lịch hôm nay + todo đến hạn + email qua đêm → ntfy. Chỉ dùng prompt template + preset, KHÔNG code mới | Briefing đến điện thoại 3 sáng liên tiếp, đúng giờ ±5 phút, đủ 3 phần nội dung | ⬜ |
| T1.2 | `src/vietnamese_dates.py` (file mới) | Parse: "mai", "mốt", "tuần sau", "cuối tháng", "7h tối thứ 6", "thứ 2 tuần sau", "15 tây"; trả datetime tz `Asia/Ho_Chi_Minh`; vá điểm gọi `parse_due_for_user` ([routes/calendar_routes.py](routes/calendar_routes.py)) ≤ 15 dòng diff | `pytest tests/test_vietnamese_dates.py` pass 100%; `pytest -m area_routes` không vỡ test cũ; `python -m py_compile` cả 2 file | ⬜ |
| T1.3 | Bộ test mẫu câu Việt (file mới `tests/test_vietnamese_dates.py`) | ≥ 15 case theo chuẩn [tests/TESTING_STANDARD.md](tests/TESTING_STANDARD.md), có case biên (23h59, qua năm, "chủ nhật") | Chạy độc lập pass; được taxonomy nhận diện (`pytest -m area_unit` hoặc sub-marker) | ⬜ |
| T1.4 | Persona trợ lý | System prompt tiếng Việt: giọng điệu mong muốn + **quy tắc định tuyến memory** (fact dài hạn → Second Brain sau này; ngữ cảnh phiên → `manage_memory`) | Checklist chủ quan của user; prompt lưu trong Settings, export ra file backup trong repo | ⬜ |

**Exit criteria P1:**
- [ ] T1.1–T1.4 ✅
- [ ] Metric: parse đúng **100%** bộ test tiếng Việt (≥ 15 case)
- [ ] Metric: tổng diff trên file upstream toàn phase ≤ 15 dòng (đếm bằng `git diff dev --stat -- routes/ src/` trừ file mới)
- [ ] Metric: briefing ổn định 3/3 ngày
- [ ] User xác nhận: "dùng được hàng ngày" (chủ quan nhưng bắt buộc)

---

## 4. PHASE 2 — SECOND BRAIN CORE (tuần 3-6, Sprint A-C)

**Mục tiêu:** kho fact + MCP + context inject hoạt động, có thước đo eval.
**Prerequisite:** P1 đạt exit. Repo Java riêng (vd. `../second-brain`), KHÔNG nằm trong repo Odysseus.

### Sprint A — Nền tảng Java

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T2.1 | Khởi tạo project | Spring Boot 3.x + Java 21, cấu trúc module by package (`knowledge/retrieval/ingestion/planner/mcp/api/gateway/obsidian`); cân nhắc Spring Modulith | `mvn verify` pass; cây package đúng 8 module | ⬜ |
| T2.2 | Postgres + pgvector vào compose | Service `postgres` (pgvector/pgvector:pg16) trong compose chung Odysseus, KHÔNG publish port ra host | `docker compose ps` healthy; từ container second-brain kết nối được; từ host KHÔNG kết nối được (5432 không mở) | ⬜ |
| T2.3 | Flyway migrations | Bảng `facts` (Graphiti: provenance, status, confidence, valid_from/invalid_at/superseded_by), `plans`, `plan_items`, `documents`, `chunks`, `ingest_jobs`; index HNSW; vector 1024 | Migration chạy 2 lần liên tiếp không lỗi (idempotent); Testcontainers test xanh | ⬜ |
| T2.4 | Embedding bge-m3 local | Service embedding trả vector 1024 chiều; tiếng Việt và tiếng Anh cùng không gian | Test: embed "con mèo"/"the cat" cosine > 0.7; embed "con mèo"/"hóa đơn điện" < 0.4; p95 latency ≤ 500ms/câu | ⬜ |

### Sprint B — MCP server + eval

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T2.5 | MCP server Streamable HTTP | `spring-ai-starter-mcp-server-webmvc`; tools `searchKnowledge`/`addFact`/`getRecentNotes`; description **song ngữ Việt-Anh giàu từ khóa**; bind mạng Docker nội bộ | MCP Inspector (hoặc curl JSON-RPC) list được 3 tool; gọi `addFact` → row mới `status='pending'` | ⬜ |
| T2.6 | Đăng ký vào Odysseus | Qua Settings → MCP, transport HTTP — KHÔNG sửa code Python | Trong UI Odysseus: server hiện "connected" kèm 3 tool | ⬜ |
| T2.7 | Bộ eval retrieval | `eval/questions.yaml`: 30-50 câu hỏi tiếng Việt + đáp án mong đợi (fact id); runner `POST /api/v1/eval/run` in recall@5, MRR | Chạy được bằng 1 lệnh; kết quả baseline ghi vào Nhật ký | ⬜ |
| T2.8 | Eval tool-routing | 10 câu kiểm tra agent Odysseus có gọi đúng tool MCP không (vd. "hôm trước tôi nói gì về dự án X?" → phải gọi `searchKnowledge`) | Tỷ lệ gọi đúng tool ≥ **8/10**; nếu dưới → viết lại description, đo lại | ⬜ |

### Sprint C — Context inject

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T2.9 | Endpoint `composeContext` | `POST /api/v1/context/compose`: nhận message + summary, trả fact liên quan kèm nhãn+nguồn; **được phép trả rỗng** (threshold thật); đường tắt chitchat; token budget ≤ 800 token | Integration test 5 kịch bản: câu có fact / không fact / chitchat / đa ý / tiếng Anh | ⬜ |
| T2.10 | `src/second_brain_provider.py` (file mới phía Odysseus) | Implement `MemoryProvider` (~100 dòng, HTTP client + timeout 2s + fail-open: Second Brain chết thì chat vẫn chạy); đăng ký 1 dòng tại [src/app_initializer.py](src/app_initializer.py) | `pytest tests/test_second_brain_provider.py` (mock HTTP); tắt container second-brain → chat Odysseus vẫn hoạt động bình thường | ⬜ |
| T2.11 | Đo baseline end-to-end | Chat thật trong Odysseus, hỏi 10 câu có fact đã seed | ≥ 7/10 câu trả lời chứa đúng fact; ghi số đo vào Nhật ký làm baseline P4 | ⬜ |
| T2.12 | Compose tích hợp | `second-brain` vào compose chung; healthcheck; restart policy | `docker compose up -d` từ máy sạch → toàn stack healthy trong ≤ 3 phút | ⬜ |

**Exit criteria P2:**
- [ ] T2.1–T2.12 ✅
- [ ] Metric: recall@5 baseline ≥ **0.7** trên bộ eval; tool-routing ≥ **80%**
- [ ] Metric: `composeContext` p95 ≤ **800ms** (đo 50 request); fail-open hoạt động
- [ ] Metric: pytest Odysseus (`-m "not slow"`) xanh — fork không vỡ gì
- [ ] Tổng file Python mới: đúng 1 (`second_brain_provider.py`) + 1 dòng vá registry

---

## 5. PHASE 2b — PLANNER + TELEGRAM (tuần 6-8, Sprint D-E)

**Mục tiêu:** AI tự thiết kế lịch, biết lịch khi chat, nhắc và dãn chương trình; chat từ xa.
**Prerequisite:** P2 đạt exit (cần composeContext cho agenda digest).

### Sprint D — Planner

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T3.1 | Planner domain + MCP tools | `proposePlan`/`activatePlan`/`getAgenda`/`checkConflict`/`updatePlanItem`/`reflowPlan`; plan luôn sinh ở `draft`, chỉ `activatePlan` mới ghi lịch thật | Unit test domain; qua chat Odysseus: "thiết kế lịch ôn 2 tuần" → nhận bảng kế hoạch draft | ⬜ |
| T3.2 | Agenda digest trong composeContext | Digest ≤ 400 token: hôm nay + quá hạn + 7 ngày + tiến độ plan active; tz `Asia/Ho_Chi_Minh` | Test 3 kịch bản chat nhắc giờ → LLM trả lời có đối chiếu lịch mà KHÔNG hỏi lại lịch | ⬜ |
| T3.3 | Conflict 2 lớp | `checkConflict` + `addPlanItem`/`activatePlan` luôn trả conflicts trong response | Bộ 10 kịch bản conflict (trùng hoàn toàn, chờm 15', khác ngày, xuyên đêm...) → phát hiện **10/10** | ⬜ |
| T3.4 | Reflow engine | `reflowPlan(strategy)`: shift-all / compress / drop-optional; trả diff trước-sau; tôn trọng `depends_on` | Test: plan 12 item trễ 2 → reflow không bao giờ xếp item sau trước item trước (0 vi phạm topo) | ⬜ |
| T3.5 | CalDAV export + reminder ntfy | Item của plan active → calendar "Second Brain" trên Radicale; nhắc trước `remind_lead_minutes`; nightly job 21:30 quét missed → đề xuất reflow qua ntfy | Event hiện trong Calendar UI Odysseus + điện thoại; reminder đến ±1 phút; giả lập item missed → 21:30 nhận đề xuất | ⬜ |

### Sprint E — Telegram gateway

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T3.6 | Bridge long-polling | Long-poll `getUpdates`; KHÔNG mở inbound port; allowlist `chat_id` từ env | Nhắn từ máy bạn → có trả lời; nhắn từ acc khác → im lặng + log warning; `docker compose port` không lộ port mới | ⬜ |
| T3.7 | Nối `POST /v1/chat` | Tin thường → Odysseus `/v1/chat` (Bearer API token) → trả lời về Telegram; gửi "⏳ đang xử lý" rồi edit message | Hỏi qua Telegram câu cần fact + lịch → trả lời đúng như chat web (chứng minh đi qua pipeline đầy đủ) | ⬜ |
| T3.8 | Lệnh nhanh | `/agenda`, `/done <số>`, `/brief` gọi thẳng module planner/briefing, không qua LLM | Mỗi lệnh phản hồi ≤ **2s**; `/done` cập nhật DB + CalDAV | ⬜ |
| T3.9 | Bảo mật gateway | Bot token + API token chỉ trong env; rate limit (≥ 20 msg/phút thì throttle); log không chứa nội dung tin nhắn đầy đủ | `grep -r` không có token trong source; test spam → bị throttle | ⬜ |

**Exit criteria P2b:**
- [ ] T3.1–T3.9 ✅
- [ ] Metric: conflict detection **10/10**; reflow 0 vi phạm dependency
- [ ] Metric: reminder đến đúng ±1 phút (theo dõi 3 ngày); lệnh nhanh ≤ 2s; chat Telegram round-trip ≤ 30s (model local)
- [ ] Kịch bản nghiệm thu end-to-end (user tự chạy): thiết kế plan qua chat → thấy trên điện thoại → báo bận qua Telegram → nhận đề xuất dời → confirm → lịch + reminder cập nhật. **Pass = phase xong.**

---

## 6. PHASE 3 — CHƯNG CẤT TRI THỨC (tuần 8-11, Sprint F-G)

**Mục tiêu:** chat không mất, tri thức tự tích lũy có duyệt.
**Prerequisite:** P2 exit; P2b có thể chạy song song.

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T4.1 | Document ingestion | Upload + Tika (PDF) + jsoup (web) + chunking sliding window; async qua bảng `ingest_jobs` (KHÔNG Kafka) | Ingest 10 PDF thật (có file tiếng Việt, file scan, file 100+ trang): 0 crash, status `indexed` hoặc `error` rõ ràng | ⬜ |
| T4.2 | Hybrid search | FTS config `'simple'` + `unaccent` (KHÔNG `'english'`); trọng số khởi điểm 0.7/0.3 | Eval: hybrid ≥ semantic-only trên recall@5; nếu kém hơn → ghi số liệu, giữ semantic-only, đánh ⏭️ | ⬜ |
| T4.3 | Thử Mem0 OSS — **gate 2 tuần** | Sidecar trong compose, ghi vào pgvector; đo trích fact tiếng Việt trên 30 đoạn chat mẫu | Precision ≥ **70%** và không bịa fact → giữ; dưới → loại, chuyển T4.4 | ⬜ |
| T4.4 | (Fallback) Extraction bằng Spring AI | Prompt trích fact + dedupe (cosine > 0.92 = trùng) + supersede | Cùng bộ 30 đoạn chat: precision ≥ 70%, dedupe bắt được cặp trùng đã gài | ⬜ |
| T4.5 | Scheduled distill cuối ngày | Task phía Odysseus (preset, không code mới): tóm tắt chat trong ngày → `addFact` (pending) | Sau 1 ngày dùng thật: fact pending xuất hiện, có `source_ref` trỏ đúng chat gốc | ⬜ |
| T4.6 | Hàng đợi duyệt | Fact `pending` KHÔNG vào composeContext (hoặc rank thấp + gắn nhãn "chưa duyệt"); chỉ `approved` dùng đầy đủ | Test: seed 1 pending + 1 approved cùng nội dung → context chỉ chứa approved | ⬜ |
| T4.7 | Obsidian export/watch | Fact + plan checklist ra vault Markdown (frontmatter: id, labels, status, provenance); watcher đọc ngược | Sửa status trong Obsidian → DB cập nhật ≤ 1 phút; tick checkbox plan → `plan_items.status` đổi | ⬜ |
| T4.8 | Consolidation job | Tuần: gom fact lẻ, dọn trùng, phát hiện mâu thuẫn → báo cáo ntfy | Chạy trên dữ liệu 2 tuần thật: báo cáo liệt kê ≥ 1 cặp trùng/mâu thuẫn nếu có gài test | ⬜ |

**Exit criteria P3:**
- [ ] T4.1–T4.8 ✅ (T4.4 chỉ bắt buộc nếu T4.3 fail gate)
- [ ] Metric: trích fact tiếng Việt precision ≥ **70%** (30 mẫu); 100% fact có provenance
- [ ] Metric: eval retrieval không giảm so với baseline P2 sau khi thêm nguồn document
- [ ] Sau 1 tuần chạy thật: ≥ 10 fact được duyệt qua Obsidian không lỗi sync

---

## 7. PHASE 4 — CONTEXT ENGINEERING (tuần 11+)

**Mục tiêu:** "AI thủ thư" soạn context tối ưu. **Mọi bước chỉ merge khi eval không giảm.**
**Prerequisite:** P3 exit; phía Python KHÔNG sửa gì thêm từ đây.

| ID | Task | Requirement | Verify | Status |
|---|---|---|---|---|
| T5.1 | Chuẩn hóa baseline | Chạy lại full eval (retrieval + tool-routing + 10 câu end-to-end) trên dữ liệu thật hiện có; chốt số | Số liệu ghi vào Nhật ký, đóng băng làm mốc so sánh | ⬜ |
| T5.2 | Query rewrite | Model nhỏ/nhanh (local 7B hoặc Haiku): khử tham chiếu mơ hồ, tách câu đa ý; thêm ≤ 300ms p95 | Eval sau ≥ eval trước trên recall@5; câu đa ý cải thiện rõ (đo riêng nhóm 10 câu đa ý) | ⬜ |
| T5.3 | Truy vấn đa nguồn có kế hoạch | CHỈ làm nếu T5.2 xong mà eval nhóm câu "cần nhiều nguồn" còn < 70%: fact + documents + agenda + chat cũ | Eval nhóm đa nguồn tăng; tổng token inject trung bình không tăng > 20% | ⬜ |
| T5.4 | Kiểm chứng quy tắc cứng | Test tự động: (a) context chỉ chứa fact nguyên văn — không diễn giải lại; (b) trả rỗng khi không liên quan; (c) chitchat bypass; (d) không vượt token budget | 4/4 nhóm test xanh, chạy trong CI của repo Java | ⬜ |

**Exit criteria P4:**
- [ ] Metric tổng: recall@5 ≥ baseline + 10% HOẶC giữ nguyên với token inject giảm ≥ 30%
- [ ] p95 composeContext (gồm rewrite) ≤ **1.5s**
- [ ] 0 trường hợp "bịa context" trong 20 câu kiểm tra tay cuối phase

---

## 8. PHASE 5 — BACKLOG (không có lịch, không metric)

Chỉ mở khi P0-P4 chạy mượt và có nhu cầu thật: "giao todo cho agent" từ UI (cơ hội PR ngược upstream) · MCP tool TCG/FAB card · graph database (chỉ khi SQL đau đớn thật) · React UI · Tailscale full UI · Kafka/Redis/K8s · multi-user. Nhịp định kỳ xuyên suốt: **sync upstream 2-4 tuần/lần** (`git fetch upstream && git checkout dev && git merge upstream/dev` → merge `dev` vào `my-features`, chạy lại `pytest -m "not slow"` sau mỗi lần).

---

## 9. NHẬT KÝ THỰC THI

> AI coder ghi MỘT dòng mỗi khi: hoàn thành task / fail verify / blocked / đo metric. Mới nhất lên đầu.

| Ngày | Task | Kết quả | Metric đo được | Ghi chú |
|---|---|---|---|---|
| 2026-06-12 | T0.1 | ✅ PASS | branch=my-features, git status sạch, 4 file .md committed (df98d7d) | roadmap_assistance.md cũng có nên commit 4 file, không phải 3 |
| 2026-06-12 | — | Khởi tạo tài liệu | — | Baseline: chưa có code, T0.0 đã xong từ trước |
