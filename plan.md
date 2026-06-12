# SECOND BRAIN — SOFTWARE DESIGN DOCUMENT

> **Version:** 1.2 | **Date:** 2026-06-12 | **Author:** Mình Bình Thường
>
> **Scope:** Thiết kế kiến trúc, data model, API và pattern tích hợp cho **Second Brain** — backend tri thức + planner phục vụ Odysseus. Đây là tài liệu kỹ thuật, đồng bộ với [roadmap_assistance.md](roadmap_assistance.md) (đọc bảng "Quyết định đã chốt" trước khi sửa thiết kế).
>
> **v1.1 thay đổi gì so với v1.0:** định vị lại sản phẩm (backend cho Odysseus, KHÔNG phải AI workspace độc lập — tránh xây "Odysseus thứ hai bằng Java"); hạ hạ tầng từ microservices+Kafka+K8s xuống modular monolith; đổi embedding sang bge-m3; thêm schema `facts` kiểu Graphiti; thêm MCP server + `composeContext`; **thêm 2 module mới: Planner (lịch trình thông minh) và Channel Gateway (Telegram)**; chuyển chat UI/conversations/React/Kafka/Redis/MinIO/K8s xuống backlog.

---

## 1. EXECUTIVE SUMMARY

### 1.1 Vai trò trong hệ sinh thái

Second Brain **không phải** một AI workspace độc lập. Nó là **bộ não dài hạn + người giữ lịch** cho Odysseus:

- Odysseus (Python, fork giữ nguyên): chat UI, agent loop, email/calendar/notes, model serving — **mặt tiền**.
- Second Brain (Java/Spring, sở hữu hoàn toàn): kho fact có duyệt, document RAG, **planner**, context engineering — **hậu phương**.

### 1.2 Bài toán giải quyết

1. **Tri thức từ chat bị mất** → chưng cất chat thành fact có provenance, có duyệt (pending/approved).
2. **Tài liệu cá nhân (PDF, web, note) không hỏi được** → ingestion + RAG tiếng Việt.
3. **Lịch trình phải tự quản** *(mới — v1.1)*: AI tự thiết kế chương trình/lịch, theo dõi hoàn thành bằng checkbox, tự đề xuất dãn/dời khi trễ; khi chat, LLM **luôn biết lịch hiện tại** — phát hiện conflict và thảo luận trực tiếp, không hỏi lại "lịch bạn thế nào".
4. **Truy cập từ mọi nơi** *(mới — v1.1)*: chat qua Telegram khi xa máy chính, hệ thống vẫn host ở nhà, thông báo vẫn đẩy về điện thoại/máy chính.

### 1.3 Phạm vi

| Trong scope (MVP) | Ngoài scope / Backlog |
|---|---|
| Bảng `facts` kiểu Graphiti (provenance, curation, supersede) | Chat UI, bảng conversations/messages (việc của Odysseus) |
| Document ingestion (Tika/jsoup) + chunking + hybrid search | React web UI (Obsidian + Odysseus UI là đủ) |
| Embedding bge-m3 local (multilingual, tiếng Việt) | Agent orchestration riêng (agent loop là của Odysseus) |
| MCP server (Streamable HTTP) expose tool cho Odysseus | Kafka, Redis, MinIO, API Gateway, gRPC |
| REST `composeContext` cho `SecondBrainMemoryProvider` | Kubernetes, RDS, S3, multi-user, JWT |
| **Planner**: plan/plan_item, conflict check, reflow, export qua `CalendarExporter` (REST API Odysseus) | GraphRAG, multi-agent, analytics |
| **Telegram gateway**: chat từ xa qua Bot API long-polling | Facebook Messenger (xem 6.1 — rủi ro ToS/ban) |
| Obsidian vault export/watch (tầng curate) | |
| Nhắc lịch qua ntfy (push trực tiếp từ Java) | |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Kiến trúc tổng thể — modular monolith

**Một** Spring Boot app duy nhất, tách module bằng package (cân nhắc Spring Modulith để ép ranh giới module bằng test). Lý do đã chốt: hệ 1 người dùng trên 1 máy; chi phí microservices nằm ở vận hành, sẽ nuốt quỹ thời gian mà không tạo giá trị tri thức. Ranh giới module sạch ⇒ tách service sau này nếu thật sự cần.

```
            ĐIỆN THOẠI / MỌI NƠI                      MÁY CHÍNH (home server)
        ┌──────────┐  ┌──────────┐         ┌─────────────────────────────────────────┐
        │ Telegram  │  │ ntfy app │         │  ODYSSEUS (Python — fork, giữ nguyên)   │
        └─────┬─────┘  └────▲─────┘         │  • Chat UI / Agent loop / Email / Notes │
              │ long-poll   │ push          │  • Calendar UI (local-first)             │
              │ (không cần  │               │  • SecondBrainMemoryProvider (file mới) │
              │  mở port)   │               │  • POST /v1/chat (API token — có sẵn)   │
              ▼             │               └───────┬─────────────────▲───────────────┘
┌─────────────────────────────────────────┐        │ MCP tools        │ REST reply
│  SECOND BRAIN (Java/Spring — 1 app)     │        │ (Streamable HTTP)│
│                                         │◄───────┘                  │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │                           │
│  │knowledge│ │retrieval │ │ingestion │ │   gateway ────────────────┘
│  │facts +  │ │bge-m3 +  │ │Tika,jsoup│ │   (Telegram bridge gọi Odysseus /v1/chat)
│  │documents│ │hybrid    │ │chunking  │ │
│  └─────────┘ └──────────┘ └──────────┘ │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │ planner │ │   mcp    │ │   api    │ │──── push ntfy (nhắc lịch, đề xuất reflow)
│  │plan/item│ │tool defs │ │compose-  │ │──── Calendar REST API export (Odysseus bearer)
│  │ reflow  │ │          │ │Context   │ │──── Obsidian vault export/watch
│  └─────────┘ └──────────┘ └──────────┘ │
└────────────────────┬────────────────────┘
                     ▼
         PostgreSQL + pgvector (1 DB duy nhất)
```

### 2.2 Module

| Module (package) | Trách nhiệm |
|---|---|
| `knowledge` | CRUD facts (Graphiti-style) + documents/chunks; trạng thái curation |
| `retrieval` | Embedding (bge-m3), semantic + hybrid search, threshold, token budget |
| `ingestion` | Upload, Tika/jsoup extract, chunking, async index (Spring `@Async` + bảng job, KHÔNG Kafka) |
| `planner` | Plan/PlanItem, conflict check, reflow engine, export qua `CalendarExporter` (REST API Odysseus), reminder qua ntfy |
| `mcp` | MCP server (spring-ai-starter-mcp-server-webmvc, Streamable HTTP) — mặt tiền cho agent Odysseus |
| `api` | REST cho `composeContext` + nội bộ (eval runner, health) |
| `gateway` | Telegram bridge: long-poll Bot API ⇄ gọi Odysseus `POST /v1/chat` |
| `obsidian` | Export fact/plan ra vault Markdown; watch vault đọc ngược chỉnh sửa |

### 2.3 Kênh giao tiếp với Odysseus

| Kênh | Chiều | Dùng cho |
|---|---|---|
| MCP tools (Streamable HTTP, localhost/Docker network) | Odysseus → SB | Thao tác **chủ động** của agent: addFact, proposePlan, markDone... |
| REST `composeContext` | Odysseus → SB | Thao tác **thụ động** mỗi message: `SecondBrainMemoryProvider.recall()` tự gọi — đây là lý do LLM "luôn biết lịch" |
| Odysseus Calendar REST API (Bearer token, sau interface `CalendarExporter`) | SB → Odysseus | Plan item hiện trên Calendar UI của Odysseus |
| ntfy (HTTP POST) | SB → user | Nhắc lịch, đề xuất reflow, fact chờ duyệt |
| `POST /v1/chat` (API token) | gateway → Odysseus | Telegram bridge chuyển tin nhắn vào pipeline chat đầy đủ (đã xác minh endpoint tồn tại — `routes/webhook_routes.py:234`) |

---

## 3. DATA MODEL

### 3.1 Quan hệ

```
FACT (độc lập, kiểu Graphiti)          DOCUMENT ──< CHUNK ──< EMBEDDING
  • provenance về chat gốc                • từ PDF/web/note
  • status pending/approved               • RAG tài liệu
  • supersede, không xóa

PLAN ──< PLAN_ITEM                     INGEST_JOB (thay Kafka)
  • chương trình do AI thiết kế          • hàng đợi index async
  • checkbox done / reflow
```

Không có bảng `users` (single-user), `conversations`/`messages` (chat sống ở Odysseus — Second Brain chỉ giữ `source_ref` trỏ về).

### 3.2 Schema chính

```sql
-- Tri thức chưng cất từ chat (Giai đoạn 2-3 roadmap)
CREATE TABLE facts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content       TEXT NOT NULL,
    labels        TEXT[] DEFAULT '{}',
    embedding     VECTOR(1024),                -- bge-m3
    -- Provenance (nguyên tắc roadmap: truy được về nguồn)
    source_type   VARCHAR(30) NOT NULL,        -- 'chat','document','manual','telegram'
    source_ref    TEXT,                        -- link/id chat gốc + timestamp
    -- Curation
    status        VARCHAR(20) DEFAULT 'pending', -- pending/approved/rejected
    confidence    REAL DEFAULT 0.5,
    -- Bitemporal: thay thế, không xóa
    valid_from    TIMESTAMPTZ DEFAULT now(),
    invalid_at    TIMESTAMPTZ,
    superseded_by UUID REFERENCES facts(id),
    created_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON facts USING hnsw (embedding vector_cosine_ops); -- HNSW thay ivfflat

-- Tài liệu (giữ từ v1.0, đổi vector 1536→1024)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content_type VARCHAR(50) NOT NULL,          -- 'pdf','web','note','code'
    source_url VARCHAR(2000), file_path VARCHAR(1000), checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'pending',        -- pending/processing/indexed/error
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(), indexed_at TIMESTAMPTZ
);
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL, chunk_index INT NOT NULL,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- PLANNER (mới v1.1)
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    goal TEXT,                                   -- mục tiêu gốc user nêu trong chat
    status VARCHAR(20) DEFAULT 'draft',          -- draft/active/paused/done/abandoned
    source_ref TEXT,                             -- chat đã sinh ra plan này
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE plan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    item_index INT NOT NULL,                     -- thứ tự trong chương trình
    scheduled_start TIMESTAMPTZ,                 -- Asia/Ho_Chi_Minh khi render
    scheduled_end   TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'todo',           -- todo/done/missed/skipped
    done_at TIMESTAMPTZ,
    depends_on UUID REFERENCES plan_items(id),   -- ràng buộc thứ tự khi reflow
    odysseus_event_id VARCHAR(255),              -- map sang event đã export vào Odysseus calendar REST API
    remind_lead_minutes INT DEFAULT 30,
    notes TEXT
);
```

### 3.3 Lưu ý retrieval tiếng Việt

- **bge-m3** (1024 chiều, multilingual) chạy local — KHÔNG dùng `text-embedding-3-small` (English-focused, 1536, tốn API).
- Full-text trong hybrid search: **không dùng** `to_tsvector('english', ...)` — stem sai tiếng Việt. Dùng config `'simple'` + extension `unaccent`, cân nhắc thêm `pg_trgm`. Trọng số khởi điểm 0.7 semantic / 0.3 full-text, tune bằng bộ eval.
- Mọi thay đổi retrieval chạy qua **bộ eval 30-50 câu** (nguyên tắc roadmap).

---

## 4. API & MCP TOOLS

### 4.1 MCP tools (mặt tiền cho agent Odysseus)

> Description của MỌI tool viết **song ngữ Việt–Anh, giàu từ khóa** — Odysseus chọn tool bằng RAG top-K (`src/tool_index.py`), description kém khớp = agent không thấy tool. Bộ eval phải có câu test "agent có gọi đúng tool không".

| Tool | Chức năng | Ghi chú |
|---|---|---|
| `searchKnowledge(query, topK)` | Tìm fact + document chunk liên quan | Trả kèm nhãn + nguồn, threshold thật (được phép trả rỗng) |
| `addFact(content, labels, source)` | Thêm fact → trạng thái `pending` | Không bao giờ ghi thẳng approved |
| `getRecentNotes()` | Fact/note mới gần đây | |
| `proposePlan(goal, constraints, deadline)` | AI thiết kế chương trình → plan `draft` + items | Trả bản kế hoạch để user duyệt ngay trong chat |
| `activatePlan(planId)` | Duyệt plan → `active`, ghi Odysseus Calendar qua REST API, đặt reminder | Chỉ chạy sau khi user đồng ý |
| `getAgenda(rangeDays)` | Lịch + plan item sắp tới & overdue | Cũng được nhúng tự động qua composeContext |
| `checkConflict(start, end)` | Kiểm tra trùng giờ với plan item + (tùy chọn) Odysseus Calendar event | Trả danh sách conflict cụ thể |
| `updatePlanItem(itemId, {status\|newStart\|newEnd})` | Tick checkbox done / dời giờ | |
| `reflowPlan(planId, strategy)` | Dãn/dồn lại các item chưa xong | `strategy`: shift-all / compress / drop-optional; trả diff trước-sau để user duyệt |

### 4.2 REST (cho MemoryProvider + nội bộ)

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/v1/context/compose` | `{message, conversationSummary}` → context block: fact liên quan + **agenda digest** (xem 5.3). Có đường tắt trả rỗng cho chitchat; token budget rõ ràng |
| POST | `/api/v1/documents` | Upload tài liệu (multipart) → ingest async |
| GET | `/api/v1/plans`, `/api/v1/plans/{id}` | Xem plan (phục vụ Obsidian export + debug) |
| POST | `/api/v1/eval/run` | Chạy bộ eval retrieval, in báo cáo |
| GET | `/actuator/health` | Health check cho compose |

Bảo mật: bind localhost/mạng Docker nội bộ; một API key tĩnh trong env giữa Odysseus ↔ Second Brain. KHÔNG JWT/multi-user ở MVP.

---

## 5. PLANNER — THIẾT KẾ CHI TIẾT (requirement mới #1)

### 5.1 Nguyên tắc

- **Source of truth là Postgres của Second Brain** (không phải Odysseus calendar). Calendar UI Odysseus là "màn hình chiếu" — Second Brain ghi vào qua REST API sau interface `CalendarExporter`; nếu tương lai cần đa thiết bị thì thêm `CaldavExporter` mà không sửa logic planner.
- LLM **không bao giờ phải hỏi lại lịch**: agenda digest được nhúng vào mọi message qua `composeContext` (kênh thụ động, không phụ thuộc agent nhớ gọi tool).
- Mọi thay đổi lịch do AI đề xuất đều ở dạng **diff chờ duyệt** — user xác nhận trong chat (hoặc Telegram) rồi mới ghi.

### 5.2 Flow A — AI tự thiết kế chương trình

```
User (chat): "thiết kế cho tôi lịch ôn thi AI trong 3 tuần, tối 2-4-6"
  → agent gọi proposePlan(goal, constraints)
  → Second Brain sinh plan draft: N items có scheduled_start/end, tránh conflict sẵn có
  → agent trình bày bảng kế hoạch trong chat
User: "ok" → agent gọi activatePlan(planId)
  → ghi các item vào Odysseus Calendar qua REST API (Bearer token, interface CalendarExporter)
  → đặt reminder ntfy theo remind_lead_minutes
```

### 5.3 Flow B — LLM luôn biết lịch (không hỏi lại)

`composeContext` luôn đính kèm **agenda digest** (~200-400 token, nằm trong token budget):

```
[AGENDA 2026-06-12, Asia/Ho_Chi_Minh]
Hôm nay: 19:00-21:00 Ôn chương 3 (plan "Ôn thi AI", item 5/12) [todo]
Quá hạn: item 4/12 "Bài tập chương 2" (hôm qua) [missed]
7 ngày tới: ... (rút gọn)
Plan đang active: "Ôn thi AI" (tiến độ 4/12, lệch -1 buổi)
```

Nhờ digest này, khi user nhắc đến bất kỳ cam kết thời gian nào trong chat, LLM có đủ dữ kiện để đối chiếu ngay.

### 5.4 Flow C — Phát hiện & thảo luận conflict ngay trong chat

```
User: "tối thứ 6 này đi ăn với team nhé, nhớ giữ chỗ"
  → LLM thấy trong digest: thứ 6 19:00 đã có "Ôn chương 4"
  → LLM nêu conflict NGAY trong câu trả lời + đề xuất phương án
     (dời buổi ôn sang sáng thứ 7 / nén vào tối thứ 5)
  → User chọn → agent gọi updatePlanItem / reflowPlan
  → Second Brain cập nhật DB + đồng bộ Odysseus Calendar (REST API) + reset reminder
```

Chốt chặn 2 lớp: lớp mềm là LLM đối chiếu digest; lớp cứng là `checkConflict`/`addPlanItem` luôn trả danh sách conflict trong response — kể cả khi LLM "quên" nhìn digest, tool result sẽ ép nó xử lý.

### 5.5 Flow D — Checkbox hoàn thành & dãn chương trình (reflow)

- **Tick done từ 3 nơi**: chat ("xong buổi ôn hôm nay rồi" → `updatePlanItem`), Telegram (lệnh `/done`), hoặc Obsidian (plan export ra vault dạng `- [ ]` checklist; watcher đọc ngược tick vào DB).
- **Nightly job** (Spring `@Scheduled`, 21:30): quét item `missed` → tính độ lệch tiến độ → nếu lệch, sinh **đề xuất reflow** (diff trước-sau) → push ntfy + Telegram: *"Bạn trễ 2 buổi. Đề xuất: dãn deadline 4 ngày HOẶC nén còn 10 buổi. Trả lời 1/2/giữ nguyên."*
- User trả lời qua Telegram/chat → `reflowPlan(strategy)` → cập nhật DB + Odysseus Calendar (REST API) + reminder. Item bị dời giữ nguyên `depends_on` (không bao giờ xếp bài chương 4 trước chương 3).

### 5.6 Reminder

Second Brain push **ntfy trực tiếp từ Java** (ntfy chỉ là HTTP POST — không cần đụng scheduler Python). Mỗi item nhắc trước `remind_lead_minutes`. Kênh nhắc: ntfy (điện thoại + desktop) và/hoặc Telegram.

---

## 6. CHANNEL GATEWAY — TELEGRAM (requirement mới #2)

### 6.1 Vì sao Telegram, không phải Facebook

| Tiêu chí | Telegram Bot API | Facebook Messenger |
|---|---|---|
| Tự động hóa tài khoản cá nhân | ✅ Bot chính thức, free | ❌ Vi phạm ToS, nguy cơ khóa acc; API chính thức đòi Page + app review |
| Host ở nhà sau NAT | ✅ **Long-polling** — bot tự gọi ra api.telegram.org, KHÔNG cần mở port/domain/SSL | ❌ Webhook bắt buộc public HTTPS endpoint |
| Độ ổn định API | Ổn định nhiều năm | Thay đổi thường xuyên, review lại |

→ **Chốt: Telegram.** Facebook chỉ xem lại nếu sau này có nhu cầu không thể thay thế.

### 6.2 Thiết kế bridge

```
Telegram app (mọi nơi)
   │  user gửi tin
   ▼
api.telegram.org  ◄── long-poll (getUpdates) ── gateway module (Java)
                                                  │ 1. lọc allowlist chat_id (chỉ mình bạn)
                                                  │ 2. POST /v1/chat (Odysseus, Bearer API token)
                                                  │    → đi qua pipeline chat ĐẦY ĐỦ:
                                                  │      composeContext, agent tools, memory
                                                  │ 3. trả reply về Telegram (sendMessage)
                                                  ▼
                                            Odysseus (máy chính)
```

- **Allowlist `chat_id`**: chỉ Telegram ID của bạn được trả lời; tin khác bị bỏ qua + log.
- Lệnh nhanh: `/agenda` (lịch hôm nay), `/done <item>` (tick checkbox), `/brief` (chạy daily briefing ngay). Lệnh nhanh gọi thẳng module planner, khỏi qua LLM — rẻ và nhanh.
- Tin nhắn dài/stream: `/v1/chat` là sync — gateway gửi "đang xử lý…" rồi edit message khi có kết quả.
- Secret (bot token, API token) nằm trong env của container, không hardcode.
- **Quan trọng**: vì tin Telegram đi qua đúng pipeline chat của Odysseus, mọi năng lực (biết lịch, conflict, memory, tools) hoạt động y hệt như chat trên web — không phải xây "trợ lý thứ hai".

### 6.3 Host ở nhà vs cloud & truy cập từ xa

- **Mặc định: host ở nhà** (máy chính RTX 3070 Ti — model local, dữ liệu tại chỗ). Long-polling Telegram + push ntfy đều là kết nối **chiều ra** → không mở port nào, không lộ IP.
- Cần **full web UI** từ xa (không chỉ chat): dùng **Tailscale** (VPN mesh, miễn phí cá nhân) — vẫn không expose public internet. Backlog, không bắt buộc MVP.
- Nếu sau này dời lên cloud VPS: kiến trúc không đổi (compose y nguyên), chỉ mất GPU local — model chuyển sang OpenRouter. Quyết định khi nhu cầu thật xuất hiện.

---

## 7. DEPLOYMENT

Một `docker-compose.yml` duy nhất (mở rộng compose sẵn có của Odysseus):

```yaml
services:
  odysseus:        # sẵn có
  searxng:         # sẵn có
  ntfy:            # sẵn có / thêm nếu chưa
  postgres:
    image: pgvector/pgvector:pg16
    volumes: [pg_data:/var/lib/postgresql/data]
    # KHÔNG publish port ra ngoài — chỉ mạng nội bộ compose
  second-brain:
    build: ./second-brain        # repo riêng, mount vào đây khi build
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/secondbrain
      - ODYSSEUS_API_TOKEN=${ODYSSEUS_API_TOKEN}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - NTFY_URL=http://ntfy
    depends_on: [postgres]
```

Backlog (chỉ khi có nhu cầu thật): Kubernetes, RDS, S3/MinIO, Redis, Prometheus/Grafana.

---

## 8. DEVELOPMENT ROADMAP

Tiền đề: **Giai đoạn 0-1 của roadmap_assistance.md đi trước** (branch `my-features`, dựng Docker, dùng thật 3-4 ngày ghi gap list, daily briefing). Sprint Java chỉ bắt đầu khi đã dùng thật.

| Sprint (2 tuần) | Nội dung | Khớp roadmap |
|---|---|---|
| **A** | Spring Boot 3.x + Java 21, Postgres+pgvector vào compose, Flyway, Testcontainers. Schema `facts` + `plans`/`plan_items`. Embedding bge-m3 local | GĐ 2 |
| **B** | MCP server Streamable HTTP: `searchKnowledge`/`addFact`/`getRecentNotes` (description song ngữ); đăng ký vào Odysseus; **bộ eval 30-50 câu chạy bằng lệnh** | GĐ 2 |
| **C** | `composeContext` + agenda digest; file `src/second_brain_provider.py` phía Odysseus (~100 dòng) + 1 dòng đăng ký registry. Đo baseline eval | GĐ 2→4 |
| **D** | **Planner đầy đủ**: proposePlan/activatePlan/checkConflict/updatePlanItem/reflowPlan, export qua `CalendarExporter` (REST API Odysseus), reminder ntfy, nightly reflow job | GĐ 2b (mới) |
| **E** | **Telegram gateway**: long-poll, allowlist, `/agenda` `/done` `/brief`, nối `POST /v1/chat` | GĐ 2b (mới) |
| **F** | Document ingestion: upload + Tika/jsoup + chunking + hybrid search (FTS `'simple'`+unaccent) | GĐ 2 mở rộng |
| **G** | Obsidian export/watch 2 chiều (fact + plan checklist); song song thử Mem0 OSS (deadline 2 tuần) | GĐ 3 |

### Definition of Done (giữ từ v1.0)

- [ ] Code reviewed (self + AI review)
- [ ] Unit test các module chính; integration test với Testcontainers
- [ ] API documented (OpenAPI)
- [ ] Docker image build được, compose chạy đủ stack
- [ ] Không lộ secret; bind nội bộ; allowlist Telegram hoạt động
- [ ] Mỗi thay đổi retrieval: chạy bộ eval, ghi kết quả trước/sau

---

## 9. TECH STACK (đã tinh giản)

| Layer | Technology | Ghi chú |
|---|---|---|
| Language | Java 21 | |
| Framework | Spring Boot 3.x (+ Spring Modulith — cân nhắc) | 1 app, module by package |
| AI | Spring AI 1.x | LLM client, MCP server starter |
| Data | Spring Data JPA + Flyway | |
| Vector | pgvector (HNSW) | bge-m3, 1024 chiều |
| Async | Spring `@Async` + `@Scheduled` + bảng job | KHÔNG Kafka |
| Ingest | Apache Tika, jsoup | |
| Test | JUnit 5 + Testcontainers | |
| Notify | ntfy (HTTP POST) | |
| Remote chat | Telegram Bot API (long-polling) | |
| LLM | Ollama local (chính) / OpenRouter (dự phòng) | qua Odysseus hoặc trực tiếp Spring AI cho extraction |

---

## 📝 CHANGE LOG

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-06-12 | 1.0 | Initial design document | Mình Bình Thường |
| 2026-06-12 | 1.1 | Định vị lại làm backend cho Odysseus; modular monolith; bge-m3; schema facts; MCP server + composeContext; **thêm Planner + Telegram gateway**; chuyển chat UI/React/Kafka/K8s xuống backlog | Claude (duyệt bởi chủ project) |
| 2026-06-12 | 1.2 | **Bỏ CalDAV/Radicale**: calendar Odysseus local-first, 1 máy, không cần sync đa thiết bị. Planner export qua `CalendarExporter` (REST API Odysseus bearer token); `caldav_uid` → `odysseus_event_id`; mọi tham chiếu CalDAV trong §2/§3/§4/§5/§8 đã cập nhật. Nếu sau này cần đa thiết bị → thêm `CaldavExporter` implement interface, không sửa planner. | Claude (duyệt bởi chủ project) |

> *Tài liệu sống — cập nhật khi quyết định kiến trúc đổi, đồng bộ với bảng "Quyết định đã chốt" trong roadmap_assistance.md.*
