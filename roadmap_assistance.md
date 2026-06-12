# Roadmap: Trợ lý cá nhân (Odysseus fork + Second Brain)

> Nguyên tắc xuyên suốt
> - **Vận hành Python, sáng tạo Java**: fork Odysseus chỉ chạm nông (prompt, config, file mới, vá nhỏ); mọi logic riêng viết thành service Spring Boot, expose qua MCP.
> - **Ưu tiên thêm file mới** thay vì sửa file lớn của upstream (`agent_loop.py`, `static/app.js`) để merge upstream không đau.
> - **Provenance từ ngày đầu**: mọi fact trong kho tri thức phải truy được về nguồn (chat gốc + timestamp).
> - **Mỗi thay đổi retrieval phải qua eval**: không tin cảm giác, tin bộ test.

---

## Điểm tựa đã xác minh trong code (2026-06-11)

Đối chiếu roadmap với codebase thực tế, các giả định sau đã được kiểm chứng:

| Giả định | Xác minh |
|---|---|
| MCP Streamable HTTP không cần sửa Python | ✅ `src/mcp_manager.py:324` có `streamablehttp_client` + OAuth tự động; đăng ký qua Settings → MCP |
| Daily briefing thuần config | ✅ ntfy tích hợp sẵn (`src/task_scheduler.py`, `src/integrations.py`); scheduler hỗ trợ cron + IANA timezone per-task (`task_scheduler.py:187`) |
| Seam cắm Second Brain vào recall pipeline | ✅ **`src/memory_provider.py`** — interface `MemoryProvider` chính thức cho external memory; đăng ký registry tại `src/app_initializer.py:77`. Một file mới + 1 dòng đăng ký, pipeline tự gọi recall mỗi message |
| Tool MCP hiển thị với agent | ⚠️ Tool được chọn bằng **RAG top-K** (`src/tool_index.py:217`), không inject hết. Description tool MCP phải song ngữ Việt–Anh, giàu từ khóa, nếu không agent sẽ không "thấy" tool |
| Tiếng Việt hóa = chỉ prompt | ⚠️ Không đủ — `/api/calendar/quick-parse` còn parser heuristic Python (`parse_due_for_user` trong `routes/calendar_routes.py`, fallback `dateutil`) không hiểu "mốt", "tuần sau". Cần file helper mới + vá nhỏ điểm gọi |
| Memory 2 tầng tách bạch | ⚠️ `manage_memory` (ChromaDB nội bộ) nằm trong `ALWAYS_AVAILABLE` của `tool_index.py` — agent mặc định ghi vào kho nội bộ. Cần persona prompt định tuyến fact dài hạn sang `addFact` |
| Kênh chat từ bên ngoài (Telegram bridge) | ✅ `POST /v1/chat` trong `routes/webhook_routes.py:234` — endpoint chat sync hỗ trợ API token, đi qua pipeline chat đầy đủ. Bridge bên ngoài gọi vào không cần sửa Python |

---

## Giai đoạn 0 — Nền tảng (tuần 1)

**Mục tiêu: hệ thống chạy được, hiểu được hiện trạng.**

- [x] Tổ chức fork: thêm remote `upstream` (đã xong), giữ branch `dev` sạch chỉ để sync
- [ ] Tạo branch `my-features` cho mọi thay đổi riêng
  ```bash
  git checkout dev && git checkout -b my-features
  ```
- [ ] Dựng Odysseus bằng Docker Compose (Odysseus + ChromaDB + SearXNG + ntfy)
  - Lưu ý: máy dev là **Windows** — Cookbook cần `tmux` nên Docker gần như bắt buộc thay vì chạy native
- [ ] Kết nối model: Ollama trên RTX 3070 Ti (model 7-8B quantized) hoặc OpenRouter làm dự phòng; thử Cookbook để scan phần cứng
- [ ] Cấu hình CalDAV (Radicale self-host hoặc Google Calendar) và ntfy lên điện thoại
- [ ] Dùng thử chế độ Personal Assistant + scheduled check-in sẵn có ít nhất 3-4 ngày, **ghi lại danh sách gap thực tế** (đừng đoán gap)
- [ ] (Tùy chọn) Chạy Graphify trên repo Odysseus làm knowledge graph cho Claude Code — chỉ là dev tool, không liên quan kho tri thức

## Giai đoạn 1 — Trợ lý notes + lịch cơ bản (tuần 2-3)

**Mục tiêu: dùng thật hàng ngày. Toàn bộ là vùng "chạm nông".**

- [ ] **Daily briefing**: scheduled task 7h sáng tổng hợp lịch hôm nay + todo đến hạn + email qua đêm, đẩy qua ntfy. Chủ yếu là prompt template + preset task, tận dụng `manage_calendar`/`manage_notes`/email tools sẵn có
- [ ] **Tiếng Việt hóa lớp ngôn ngữ** (sâu hơn "chỉ prompt" — xem bảng xác minh ở đầu file):
  - [ ] Prompt tiếng Việt cho `/quick-parse` và `/parse` (reminder, sự kiện)
  - [ ] File helper mới `src/vietnamese_dates.py` xử lý cụm thời gian Việt ("mốt", "tuần sau", "7h tối thứ 6") + vá nhỏ điểm gọi `parse_due_for_user` trong `routes/calendar_routes.py` (fallback `dateutil` không hiểu tiếng Việt)
  - [ ] Timezone Asia/Ho_Chi_Minh nhất quán toàn hệ thống (scheduler đã hỗ trợ IANA tz per-task sẵn)
  - [ ] Bộ test mẫu câu Việt: "mai", "mốt", "tuần sau", "cuối tháng", "7h tối thứ 6"
- [ ] Tinh chỉnh persona trợ lý (system prompt) theo cách bạn muốn nó nói chuyện

## Giai đoạn 2 — Kho tri thức trong Second Brain (tuần 3-6)

**Mục tiêu: trái tim hệ thống, nằm hoàn toàn phía Java.**

- [ ] **Schema fact kiểu Graphiti** trên PostgreSQL + pgvector:
  - `content`, `labels[]`, `embedding`
  - Provenance: `source_type`, `source_ref` (link chat/episode gốc), `created_at`
  - Curation: `status` (pending / approved / rejected), `confidence`
  - Thời gian: `valid_from`, `invalid_at`, `superseded_by` (đánh dấu thay thế, không xóa)
- [ ] Embedding multilingual cho tiếng Việt (bge-m3 hoặc tương đương), chạy local
- [ ] **MCP server** bằng `spring-ai-starter-mcp-server-webmvc`, transport Streamable HTTP, bind localhost/mạng Docker nội bộ:
  - [ ] Tool `searchKnowledge(query)` — gọi RAG pipeline
  - [ ] Tool `addFact(content, labels, source)` — vào trạng thái pending
  - [ ] Tool `getRecentNotes()`
  - [ ] **Description tool viết song ngữ Việt–Anh, giàu từ khóa** — Odysseus chọn tool bằng RAG top-K (`src/tool_index.py`), description kém khớp = agent không thấy tool. Thêm câu test "agent có gọi đúng tool không" vào bộ eval
- [ ] Đăng ký MCP server này trong Odysseus (Settings → MCP, transport HTTP) — không cần sửa code Python
- [ ] **Skeleton `SecondBrainMemoryProvider`** (kéo từ Giai đoạn 4 về — rẻ và là seam chính thức): file mới `src/second_brain_provider.py` implement `MemoryProvider` (HTTP client mỏng ~100 dòng gọi endpoint search của Spring Boot) + 1 dòng đăng ký trong `src/app_initializer.py:77`. Pipeline tự gọi `recall()` mỗi message — không phụ thuộc agent nhớ gọi tool
- [ ] **Bộ eval 30-50 câu hỏi** kèm đáp án mong đợi; chạy trước/sau mỗi thay đổi retrieval
- [ ] Đưa Second Brain vào chung `docker-compose.yml` với Odysseus

## Giai đoạn 2b — Planner & truy cập từ xa (tuần 6-8, chạy song song GĐ 3)

**Mục tiêu: AI tự thiết kế lịch, theo dõi hoàn thành, phát hiện conflict trong chat; chat được từ mọi nơi qua Telegram.** Thiết kế chi tiết xem [plan.md](plan.md) §5-6.

- [ ] **Planner module** (Java): bảng `plans`/`plan_items`, MCP tools `proposePlan`/`activatePlan`/`getAgenda`/`checkConflict`/`updatePlanItem`/`reflowPlan`
- [ ] **Agenda digest trong composeContext** — LLM luôn biết lịch hiện tại mỗi message, không hỏi lại; conflict được nêu và thảo luận ngay trong chat
- [ ] **CalDAV export**: plan item ghi vào calendar riêng "Second Brain" trên Radicale → hiện trong Calendar UI Odysseus + điện thoại
- [ ] **Checkbox done 3 đường**: chat (`updatePlanItem`), Telegram (`/done`), Obsidian checklist (watcher đọc ngược)
- [ ] **Nightly reflow job**: quét item missed → đề xuất dãn/nén chương trình (diff trước-sau) → push ntfy/Telegram, user duyệt mới ghi
- [ ] **Telegram gateway** (Java, long-polling — không cần mở port khi host ở nhà): allowlist chat_id, lệnh nhanh `/agenda` `/done` `/brief`, tin thường đi qua `POST /v1/chat` của Odysseus (pipeline đầy đủ: context, tools, memory)

## Giai đoạn 3 — Pipeline chưng cất chat thành tri thức (tuần 6-8)

**Mục tiêu: chat không bị mất, tri thức tự tích lũy, bạn curate được.**

- [ ] **Thử Mem0 OSS** làm máy trích fact: chạy sidecar Python trong compose, cấu hình ghi vào pgvector của bạn. Đặt deadline 1-2 tuần đánh giá chất lượng trích fact **tiếng Việt**
  - Nếu không đạt → tự viết extraction bằng Spring AI (prompt trích fact + dedupe + supersede), kiểm soát tiếng Việt tốt hơn
- [ ] Scheduled task phía Odysseus: cuối ngày tóm tắt các chat mới → đẩy fact ứng viên sang Second Brain qua MCP tool (trạng thái pending)
- [ ] **Hàng đợi duyệt**: fact pending chỉ được retrieval dùng sau khi approve (hoặc xếp hạng tin cậy thấp hơn fact đã duyệt)
- [ ] **Obsidian làm tầng curate**: Second Brain export fact ra vault Markdown (frontmatter chứa id, labels, status, provenance); watch vault để đọc ngược chỉnh sửa của bạn vào DB. Tiết kiệm công xây UI duyệt riêng
- [ ] Job consolidation định kỳ (tuần/tháng): gom fact lẻ thành tri thức tổng hợp, dọn trùng lặp, phát hiện mâu thuẫn

## Giai đoạn 4 — Context engineering (tuần 8+)

**Mục tiêu: mỗi message được "AI thủ thư" soạn context tốt nhất, tiết kiệm token.**

> Kênh inject: đi qua `SecondBrainMemoryProvider.recall()` (đã dựng skeleton ở GĐ 2) — pipeline gọi tự động mỗi message, **không** dựa vào MCP tool call (agent có thể quên gọi). MCP tool giữ cho thao tác chủ động (`addFact`, tra cứu theo yêu cầu); provider lo phần context thụ động. Đến GĐ 4 phía Python không cần sửa thêm gì — mọi nâng cấp nằm trong logic `composeContext` phía Java.

Xây tăng dần, mỗi bước đo bằng bộ eval:

- [ ] **Bước 1**: endpoint `composeContext(message, conversationSummary)` trong Second Brain — retrieval trực tiếp, trả fact nguyên văn kèm nhãn + nguồn. Đo baseline. Provider gọi endpoint này từ `recall()`
- [ ] **Bước 2**: thêm query rewrite bằng model nhỏ/nhanh (Haiku hoặc local 7B) — khử tham chiếu mơ hồ, tách câu hỏi đa ý. Thường cải thiện rõ nhất với chi phí thấp nhất
- [ ] **Bước 3** (nếu eval cho thấy còn thiếu): truy vấn đa nguồn (fact + notes + lịch + chat cũ) có kế hoạch
- [ ] Quy tắc cứng:
  - AI trung gian chỉ **chọn và sắp xếp**, không diễn giải lại (tránh tạo trạm hallucinate mới)
  - Được phép trả "không có gì liên quan" — threshold thật
  - Có đường tắt bỏ qua pipeline cho message đơn giản/chitchat
  - Token budget rõ ràng cho phần context inject

## Giai đoạn 5 — Mở rộng (backlog, làm khi các giai đoạn trên chạy mượt)

- [ ] "Giao todo cho agent" từ UI (đúng item roadmap upstream đang cần → có thể PR ngược, đẹp profile)
- [ ] Tool domain riêng qua MCP: truy vấn PostgreSQL của TCG, tra cứu FAB card, wrap hệ nhận diện thẻ
- [ ] Cân nhắc graph database **chỉ khi** xuất hiện nhu cầu truy vấn quan hệ nhiều bước mà SQL làm đau đớn
- [ ] Sync upstream định kỳ (2-4 tuần/lần): `git fetch upstream && git checkout dev && git merge upstream/dev`, rồi merge `dev` vào `my-features`

---

## Quyết định đã chốt (để khỏi bàn lại)

| Chủ đề | Quyết định | Lý do ngắn |
|---|---|---|
| Nền tảng assistant | Fork Odysseus, hoàn thiện Personal Assistant sẵn có | Notes/calendar/tasks/reminder/scheduler đã có nền |
| Phân vai ngôn ngữ | Python = vận hành nông; Java = mọi logic riêng | Tránh phân tán, tận dụng sở trường |
| **Refactor Odysseus sang Java** | **Không, không bao giờ** | Mất khả năng sync upstream (giá lớn nhất — upstream rất active); tốn nhiều tháng nuốt trọn roadmap mà chưa tạo giá trị cá nhân hóa nào; viết lại logic có sẵn sang ngôn ngữ đã giỏi = không học được gì mới |
| Kho tri thức | PostgreSQL + pgvector, schema kiểu Graphiti | Quen thuộc, đủ dùng; không Neo4j giai đoạn đầu |
| Trích fact | Thử Mem0 OSS trước, fallback tự viết Spring AI | Mua phần khó, giữ quyền sở hữu dữ liệu |
| Curate | Obsidian vault sync 2 chiều | Khỏi xây UI duyệt từ đầu |
| Graphify | Chỉ làm dev tool cho Claude Code hiểu codebase | Sai mục đích nếu dùng làm kho tri thức |
| Memory 2 tầng | Odysseus = ngữ cảnh ngắn hạn; Second Brain = tri thức dài hạn có duyệt | Tránh 2 kho giẫm chân |
| Kênh inject context | `MemoryProvider` registry (file mới + 1 dòng `app_initializer.py`), không phải MCP tool | Pipeline gọi tự động mỗi message; tool call không đảm bảo chạy |
| Định tuyến memory | Persona prompt: fact dài hạn → `addFact` (pending); ngữ cảnh phiên → `manage_memory` nội bộ | `manage_memory` là ALWAYS_AVAILABLE, agent sẽ mặc định dùng nếu không hướng dẫn |
| Kiến trúc Second Brain | Modular monolith (1 Spring Boot app, module by package), KHÔNG microservices/Kafka/K8s ở MVP | Hệ 1 user 1 máy; chi phí microservices nằm ở vận hành, nuốt quỹ thời gian không tạo giá trị tri thức |
| Embedding | bge-m3 local (1024 chiều), KHÔNG text-embedding-3-small | Multilingual cho tiếng Việt, không tốn API, dữ liệu tại chỗ |
| Planner | Source of truth = Postgres Second Brain; CalDAV chỉ là "màn hình chiếu"; LLM biết lịch qua agenda digest trong composeContext; mọi thay đổi lịch = diff chờ duyệt | Không hỏi lại lịch; conflict 2 lớp (digest mềm + checkConflict cứng); xem plan.md §5 |
| Kênh chat từ xa | Telegram Bot API long-polling, KHÔNG Facebook | FB vi phạm ToS với acc cá nhân + đòi public webhook; Telegram long-poll không cần mở port khi host ở nhà. Bridge gọi `POST /v1/chat` (đã xác minh có sẵn) |
| Truy cập full UI từ xa | Tailscale (backlog), không expose public internet | Long-poll + ntfy đều là kết nối chiều ra, không mở port nào |

### Vì sao Python phía Odysseus không phải vấn đề (chốt 2026-06-11)

- Mức chạm Python của toàn roadmap rất nông: prompt, config, vài file mới nhỏ (`vietnamese_dates.py`, `second_brain_provider.py` ~100 dòng), vài chỗ vá 1-2 dòng. Đây là **đọc hiểu** Python với nền Java vững — không cần viết Python idiomatic hay nắm framework sâu.
- Với master AI, Python là lingua franca; đọc codebase này (agent loop, RAG, embeddings, MCP, context compaction) là **tài liệu học thực chiến** bổ trợ trực tiếp cho chương trình học, không phải gánh nặng.
- Toàn bộ chất xám kỹ thuật (Spring AI, pgvector, MCP server, retrieval eval) dồn vào Second Brain phía Java — đúng sở trường, đúng nội dung học, đúng "trái tim hệ thống".
- **Quy tắc tự kiểm ranh giới**: nếu thấy mình viết ngày càng nhiều logic Python (file riêng phình quá vài trăm dòng, có business logic thật) → đó là logic đặt **sai phía ranh giới**, dời sang Spring Boot qua MCP/REST — chứ không phải tín hiệu để refactor Odysseus.