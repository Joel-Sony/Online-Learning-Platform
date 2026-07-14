# Architecture — Online Learning Platform

## 1. What This Platform Does

An online learning marketplace where **students** discover, purchase, and consume courses; **mentors** create and manage courses; and **admins** oversee the entire platform. It covers the full lifecycle: course creation → publishing → enrollment (free or paid) → lesson consumption → progress tracking → quizzes → certificates → Q&A → notifications.

---

## 2. System Architecture (Bird's-Eye View)

```
┌────────────────────────────────────────────────────────────────────┐
│                        Browser (React SPA)                        │
│   ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│   │  REST calls │  │  WebSocket   │  │  Stripe/PayPal redirect │  │
│   │  (Axios)    │  │  (native WS) │  │  (browser redirect)     │  │
│   └──────┬─────┘  └──────┬───────┘  └───────────┬──────────────┘  │
└──────────┼───────────────┼───────────────────────┼─────────────────┘
           │               │                       │
           ▼               │                       ▼
┌──────────────────────┐   │   ┌─────────────────────────────┐
│   Django REST API    │   │   │  Stripe / PayPal            │
│   (Daphne ASGI :8001)│   │   │  (external payment          │
│   HTTP requests      │   │   │   processors)               │
└──────────┬───────────┘   │   └──────────────┬──────────────┘
           │               │                  │
           ▼               ▼                  │  Webhook callback
┌─────────────────────────────────────────┐   │
│          Daphne ASGI Server             │   │
│  ┌──────────────────┐ ┌──────────────┐  │   │
│  │  HTTP (WSGI)     │ │  WebSocket   │  │   │
│  │  Django REST     │ │  Consumers   │  │   │
│  └────────┬─────────┘ └──────┬───────┘  │   │
│           │                  │          │   │
└───────────┼──────────────────┼──────────┘   │
            │                  │              │
            ▼                  ▼              │
┌─────────────────────────────────────────┐   │
│            PostgreSQL 16                │   │
│  (all application data, search vectors) │   │
└─────────────────────────────────────────┘   │
            │                                  │
            ▼                                  │
┌──────────────────────┐                      │
│       Redis 7        │                      │
│  Channel layer only  │                      │
│  (WebSocket pub/sub) │                      │
└──────────────────────┘                      │
                                              │
            ┌─────────────────────────────────┘
            ▼
┌──────────────────────┐
│   Webhook handler    │
│   (Django view)      │
│   creates Enrollment │
└──────────────────────┘
```

### How the pieces connect

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19 + Vite 8 + React Router 7 | Client-side SPA. Makes REST calls via Axios, opens WebSocket connections for real-time features. |
| **API Server** | Django 5 + DRF (via Daphne ASGI) | Handles all HTTP REST requests: CRUD for courses, enrollments, progress, etc. JWT auth on every request. |
| **WebSocket Server** | Django Channels (same Daphne process) | Two real-time channels: course Q&A rooms and per-user notification stream. |
| **Database** | PostgreSQL 16 | All persistent data. Also handles full-text search via built-in `SearchVector`/`SearchRank`/`TrigramSimilarity`. |
| **Redis** | Redis 7 (Alpine) | **Only** used as the channel layer backend for Django Channels — publishes WebSocket messages to subscribers. No data caching. |
| **Payments** | Stripe + PayPal | Browser redirects to hosted checkout pages; payment confirmation arrives via server-side webhook. |

---

## 3. Technology Stack — Detailed

### 3.1 Backend (`backend/`)

| Component | What It Is | Why |
|-----------|-----------|-----|
| **Django 5** | Python web framework | ORM, admin, migrations, management commands |
| **Django REST Framework** | REST API toolkit | ViewSets, Serializers, Permissions, Pagination |
| **Django Channels** | WebSocket framework | ASGI application, consumers, channel layers |
| **Daphne** | ASGI server | Serves both HTTP and WebSocket on the same port |
| **SimpleJWT** | JWT auth plugin | Access + refresh token flow |
| **django-filter** | Query param filtering | `filterset_fields`, `DjangoFilterBackend` |
| **django-cors-headers** | CORS middleware | Allows frontend origin |
| **drf-nested-routers** | Nested URL routing | `/courses/{id}/qna/questions/{id}/replies/` |
| **channels_redis** | Redis channel layer backend | Pub/sub for WebSocket groups |
| **Stripe SDK** | Stripe API client | Checkout sessions, refunds, webhook verification |
| **PayPal SDK** | PayPal REST API client | Orders, payments, refunds |
| **Pillow** | Image processing | Thumbnail/profle-pic handling |
| **psycopg2-binary** | PostgreSQL adapter | Database driver |
| **django-environ** | Environment variables | Read `.env` files |

### 3.2 Frontend (`frontend/`)

| Component | What It Is |
|-----------|-----------|
| **React 19** | UI framework |
| **Vite 8** | Build tool and dev server |
| **React Router 7** | Client-side routing |
| **Axios** | HTTP client with JWT interceptors |
| **ReactMarkdown + remark-gfm** | Render Markdown lesson content |
| **Lucide React** | Icon library |

### 3.3 Infrastructure

| Component | What It Is | Why |
|-----------|-----------|-----|
| **PostgreSQL 16** | Primary database | Stores all models: users, courses, enrollments, progress, notifications, Q&A |
| **Redis 7** | In-memory pub/sub | Channels channel layer for WebSocket message routing |
| **Mailpit** | SMTP test server (dev) | Catches outgoing emails in development |
| **Docker Compose** | Container orchestration | Runs db + redis + mailpit + backend + daphne + frontend locally |
| **Render Blueprint** | Deployment as code | `render.yaml` defines all services |

---

## 4. Backend Apps — What Each Does

```
backend/
├── core/             # Django project config: settings, root URLs, ASGI/WSGI
├── users/            # Custom user model, JWT auth, registration, profile
├── courses/          # Course/module/lesson CRUD, quizzes, search, content gen
├── enrollments/      # Enrollment, payments, Stripe/PayPal webhooks, refunds
├── progress/         # Lesson progress tracking, certificates, mentor analytics
├── notifications/   # In-app notifications, announcements, WebSocket push
├── interactions/     # Reviews, legacy Q&A, review moderation
├── qna/              # Threaded course Q&A with real-time updates
```

### 4.1 `core/` — Project Config

`settings.py` is the nerve center. Key configs:

- **`AUTH_USER_MODEL = 'users.User'`** — custom user model used by entire app
- **`CHANNEL_LAYERS`** — configured with `channels_redis.pubsub.RedisPubSubChannelLayer` (reads `REDIS_URL` env var)
- **`REST_FRAMEWORK`** — default auth: SimpleJWT; default permission: `IsAuthenticatedOrReadOnly`
- **`INSTALLED_APPS`** — includes `daphne` first (for ASGI), `django.contrib.postgres` (for search), all 7 custom apps
- **`SIMPLE_JWT`** — access token 60 min, refresh 1 day

`urls.py` mounts:
- `/admin/` → Django admin
- `/api/users/` → auth endpoints
- `/api/` → courses, enrollments, progress, notifications, interactions
- `/api/courses/{id}/qna/` → nested Q&A routes
- `/api/admin/` → admin-only endpoints

`asgi.py` creates a `ProtocolTypeRouter`:
- HTTP → Django ASGI handler
- WebSocket → `AuthMiddlewareStack` routing to `interactions` and `notifications` consumers

`admin_urls.py` defines admin-only REST endpoints (separate from Django admin):
| Prefix | ViewSet | Purpose |
|--------|---------|---------|
| `admin/users/` | AdminUserViewSet | List users, ban/unban |
| `admin/mentors/` | AdminMentorApprovalViewSet | Approve/reject mentor registrations |
| `admin/courses/` | AdminCourseApprovalViewSet | Approve/reject courses |
| `admin/reviews/` | AdminReviewModerationViewSet | List flagged reviews, delete |
| `admin/qna/` | AdminQnAModerationViewSet | List flagged Q&A, delete |
| `admin/refunds/` | AdminRefundViewSet | Process/reject refund requests |
| `admin/reports/` | AdminReportsView | Platform-wide stats |

### 4.2 `users/` — Authentication & User Model

**Model — `User` (extends AbstractUser)**

| Field | Purpose |
|-------|---------|
| `role` | STUDENT / MENTOR / ADMIN — determines frontend nav + backend permissions |
| `is_mentor_approved` | Mentors need admin approval before they can create/publish courses |
| `profile_picture` | Uploaded avatar image |
| `bio` | Short biography |

**Auth flow:**

1. **Register** → `POST /api/users/register/` → creates user, returns JWT access + refresh tokens
2. **Login** → `POST /api/users/login/` (DRF's `TokenObtainPairView`) → returns tokens
3. **Authenticated requests** → Axios interceptor attaches `Authorization: Bearer <access>`
4. **Token refresh** → On 401, Axios interceptor calls `POST /api/users/token/refresh/` automatically
5. **Profile** → `GET /api/users/me/` → returns current user

**Role hierarchy on backend:**
- `IsAuthenticatedOrReadOnly` — anyone can GET, only authenticated can POST/PUT/DELETE
- `IsMentorOrReadOnly` — write requires MENTOR or ADMIN role
- `IsOwnerOrAdmin` — object-level: only the mentor of the resource or an admin can modify

### 4.3 `courses/` — Courses, Modules, Lessons, Quizzes

This is the largest app. It manages the entire curriculum hierarchy.

**Models:**

```
Course
  ├── Module (ordered)
  │    ├── Lesson (ordered) — VIDEO, PDF, or DOCUMENT
  │    │    ├── title, video_url, content (Markdown), file
  │    │    └── duration_minutes
  │    └── Quiz
  │         ├── QuizQuestion (ordered)
  │         │    └── QuizChoice (one marked is_correct)
  │         └── QuizAttempt (student, score, passed)
  ├── mentor (User FK)
  ├── status (PENDING / PUBLISHED / REJECTED)
  ├── is_published (boolean, same as status=PUBLISHED in practice)
  ├── thumbnail image
  ├── price, is_free
  ├── category, level, language, tags
  └── avg_rating, enrollment_count (annotated)
```

**Key backend features:**

| Feature | Implementation |
|---------|---------------|
| **Full-text search** | `courses/search.py` — custom `CourseSearchBackend`. Weighted `SearchVector` (title>A > tags>B > category>C > description>D), ranked by `SearchRank`, falls back to `TrigramSimilarity`, falls back to `icontains`. |
| **Autocomplete** | `GET /api/courses/autocomplete/?q=...` — same search pipeline, max 7 results. Used by frontend search bar. |
| **Filtering** | `CourseFilter` — by price range, duration range, min rating, category, level, language, is_free |
| **Pagination** | `CoursePagination` — 12 per page, max 100 |
| **Content generation** | Management commands: `generate_all_content` writes Markdown + image URLs for all 128 lessons; `download_thumbnails` re-downloads Unsplash images |
| **Quiz evaluation** | `QuizViewSet.submit_attempt` — checks answers, computes score %, auto-creates Certificate if all lessons done |

**Content generation on Render:**

The startup command runs `generate_all_content` on every deploy. It's idempotent — it overwrites lesson content using keyword-matched templates and Unsplash image URLs. This works around Render's ephemeral filesystem since all content is stored in PostgreSQL.

### 4.4 `enrollments/` — Enrollment & Payments

**Models:**

| Model | Key Fields |
|-------|-----------|
| **Enrollment** | student, course, enrolled_at, status (ACTIVE/COMPLETED/REFUNDED). Unique together: (student, course) |
| **Payment** | user, course, provider (STRIPE/PAYPAL), amount, currency, status, provider_payment_id |

**Payment flow (Stripe example):**

```
1. Student clicks "Purchase"
2. Frontend → POST /api/enrollments/create_stripe_checkout/
3. Backend creates Stripe CheckoutSession, creates Payment (PENDING), returns URL
4. Browser redirects to Stripe hosted checkout
5. Student pays on Stripe.com
6a. Stripe sends webhook → POST /api/webhooks/stripe/ (checkout.session.completed)
       → Backend verifies signature, creates Enrollment, updates Payment, sends notification
6b. Browser returns to frontend success page → POST /api/enrollments/verify_stripe_session/
       → Backend double-checks and idempotently creates Enrollment
```

PayPal flow is identical but uses PayPal orders instead of Stripe sessions.

**Free enrollment:** `POST /api/enrollments/enroll_free/` — skips payment, creates Enrollment immediately.

**Refunds:**
1. Student requests refund → `POST /api/enrollments/{id}/request_refund/` → marks Payment as `REFUND_REQUESTED`
2. Admin approves → `POST /api/admin/refunds/{id}/approve/` → calls Stripe/PayPal refund API, marks Payment `REFUNDED`, Enrollment `REFUNDED`, sends notification
3. Admin rejects → `POST /api/admin/refunds/{id}/reject/` → resets Payment to `COMPLETED`

### 4.5 `progress/` — Lesson Progress & Certificates

**Models:**

| Model | Key Fields |
|-------|-----------|
| **LessonProgress** | student, course, lesson, completed (bool), completed_at. Unique: (student, lesson) |
| **Certificate** | student, course, issued_at, certificate_id (unique UUID) |

**Mark complete flow:**
1. Student clicks "Mark Complete" → `POST /api/progress/mark_complete/` (with lesson_id)
2. Backend validates enrollment, creates/updates `LessonProgress`
3. Backend checks if ALL lessons for the course are now completed
4. If yes → auto-creates `Certificate` with a unique ID and sends notification

**Certificate download:**
`GET /api/certificates/{id}/download/?token=...` — generates styled HTML page (Cormorant serif font, gold divider, platform name, student name, course title). Supports JWT token auth via query param so students can download without being logged in.

**Mentor analytics:**
`GET /api/mentor-analytics/` — returns per-course enrollment count + completion count (mentor's own courses only).

### 4.6 `notifications/` — Notifications & Announcements

**Models:**

| Model | Key Fields |
|-------|-----------|
| **Notification** | recipient, type (ENROLLMENT/NEW_LESSON/NEW_ANSWER/REFUND/ANNOUNCEMENT), message, is_read, course |
| **Announcement** | course, mentor, title, content, send_email, created_at |

**How notifications work end-to-end:**

```
1. Any backend code calls create_notification(recipient, type, message, course)
2. create_notification (notifications/utils.py):
   a. Saves Notification to PostgreSQL
   b. Sends WebSocket message to Redis channel "notifications_{user_id}"
   c. Sends email via Django's send_mail()
3. Frontend useNotifications hook:
   a. Opens WebSocket to /ws/notifications/?token=JWT
   b. Receives real-time push → prepends to notification list, increments badge
   c. Also fetches GET /api/notifications/ on mount for initial load
```

**Announcement flow:**
1. Mentor creates announcement → `POST /api/announcements/` (with course_id, title, content)
2. `AnnouncementViewSet.perform_create`:
   a. Saves Announcement
   b. Iterates all ACTIVE enrollments for that course
   c. Creates Notification (type=ANNOUNCEMENT) for each enrolled student

### 4.7 `interactions/` — Reviews & Legacy Q&A

**Models:**

| Model | Key Fields |
|-------|-----------|
| **Review** | student, course, rating (1-5), review_text, is_flagged, created_at. Unique: (student, course) |
| **ReviewReport** | review, reported_by, reason |
| **Question** (legacy) | course, author, title, content |
| **Answer** (legacy) | question, author, content |

**Review flow:**
- Students can only review courses they're enrolled in
- One review per student per course
- Reviews can be flagged by anyone → admin moderates in admin dashboard

### 4.8 `qna/` — Threaded Course Q&A

**Models:**

| Model | Key Fields |
|-------|-----------|
| **Question** | course, author, title, body, is_pinned, is_flagged |
| **Reply** | question, author, body, is_mentor_response (auto-set), parent (one level of threading), is_flagged |

**How Q&A works:**

```
1. Student opens course Q&A page → connects WebSocket to /ws/course/{id}/qa/
2. Posts question → POST /api/courses/{id}/qna/questions/
   → Backend validates write permission (enrolled student, mentor, or admin)
   → Saves question
   → Broadcasts "new_question" via WebSocket to course_qa_{id} group
3. Any connected client receives real-time update
4. Mentor replies → POST /api/courses/{id}/qna/questions/{qid}/replies/
   → Backend auto-sets is_mentor_response=True if reply author is course mentor
   → Broadcasts "new_reply" via WebSocket
   → Sends NEW_ANSWER notification to question author
5. Mentor/admin can pin important questions → POST .../pin/
```

---

## 5. Frontend — Pages & Routes

The frontend is a single-page React app with these pages:

| Route | Component | What It Shows |
|-------|-----------|---------------|
| `/` | Home | Landing page with featured courses |
| `/courses` | CourseList | Catalog grid with search bar, filters, pagination |
| `/courses/:id` | CourseDetails | Full course page: description, curriculum, price, reviews |
| `/courses/:id/learn` | LearnCourse | Lesson player: sidebar with modules, main content area |
| `/courses/:id/learn/:lessonId` | LearnCourse | Same page, scrolled to specific lesson |
| `/courses/:id/qa` | QAPage | Real-time Q&A room for the course |
| `/quiz/:id` | TakeQuiz | Quiz interface: questions, choices, submit, results |
| `/login` | Login | JWT login form |
| `/register` | Register | Role-based registration form |
| `/learning` | LearningDashboard | Student: enrolled courses with progress |
| `/mentor` | MentorDashboard | Mentor: course list, create/edit/delete |
| `/mentor/create` | CreateCourse | Course creation form (modules, lessons, quizzes) |
| `/mentor/edit/:id` | EditCourse | Edit existing course |
| `/mentor/quiz/:id/edit` | EditQuiz | Quiz builder |
| `/mentor/analytics` | MentorAnalytics | Per-course enrollment + completion stats |
| `/mentor/announcement` | CreateAnnouncement | Create announcements for enrolled students |
| `/notifications` | Notifications | Full notification history |
| `/payment-success` | PaymentSuccess | Post-checkout success page |
| `/payment-failed` | PaymentFailed | Post-checkout failure page |
| `/admin` | AdminDashboard | User management, course moderation, refunds, reports |

**Navbar behavior by role:**
- **Student**: "Catalog", "My Learning", notification bell
- **Mentor**: "Catalog", "Studio", "Analytics", "Announce", notification bell
- **Admin**: "Catalog", "Admin", notification bell (My Learning and mentor links hidden)

**State management:** No Redux or external state library. Auth state is stored in `localStorage` (access token, refresh token, role, username). Page-level state uses React's built-in `useState` and `useEffect`.

---

## 6. API Route Map (Complete)

### Public (no auth needed)

| Method | URL | Purpose |
|--------|-----|---------|
| POST | `/api/users/register/` | Create account |
| POST | `/api/users/login/` | Get JWT tokens |
| POST | `/api/users/token/refresh/` | Refresh access token |
| GET | `/api/courses/` | List published courses (paginated) |
| GET | `/api/courses/{id}/` | Course detail with modules/lessons |
| GET | `/api/courses/autocomplete/?q=` | Search suggestions |
| GET | `/api/mentors/search/?search=` | Find mentors |
| GET | `/api/reviews/` | List reviews (non-flagged) |
| GET | `/api/reviews/course_ratings/?course_id=` | Average rating + count |
| GET | `/api/questions/` | List legacy Q&A questions |
| GET | `/api/answers/` | List legacy Q&A answers |
| GET | `/api/certificates/{id}/download/` | Download certificate HTML |
| POST | `/api/webhooks/stripe/` | Stripe webhook (external) |

### Authenticated (any role)

| Method | URL | Purpose |
|--------|-----|---------|
| GET/PATCH | `/api/users/me/` | View/update profile |
| CRUD | `/api/enrollments/` | List/create enrollments |
| POST | `/api/enrollments/enroll_free/` | Enroll in free course |
| POST | `/api/enrollments/create_stripe_checkout/` | Start Stripe checkout |
| POST | `/api/enrollments/create_paypal_order/` | Start PayPal checkout |
| POST | `/api/enrollments/verify_stripe_session/` | Confirm Stripe payment |
| POST | `/api/enrollments/capture_paypal_payment/` | Confirm PayPal payment |
| POST | `/api/enrollments/{id}/request_refund/` | Request refund |
| GET | `/api/payments/` | View payment history |
| CRUD | `/api/progress/` | Lesson progress |
| POST | `/api/progress/mark_complete/` | Mark lesson complete |
| GET | `/api/progress/course_progress/?course_id=` | Get course completion % |
| GET | `/api/certificates/` | List certificates |
| GET | `/api/notifications/` | List notifications |
| POST | `/api/notifications/{id}/read/` | Mark notification read |
| POST | `/api/notifications/read-all/` | Mark all read |
| GET | `/api/announcements/?course=` | List course announcements |
| POST | `/api/reviews/` | Create review |
| POST | `/api/reports/` | Report review |
| CRUD | `/api/courses/{id}/qna/questions/` | Course Q&A questions |
| CRUD | `/api/courses/{id}/qna/questions/{qid}/replies/` | Question replies |

### Mentor only

| Method | URL | Purpose |
|--------|-----|---------|
| CRUD | `/api/courses/` | Manage own courses |
| CRUD | `/api/modules/` | Manage modules (by course_id) |
| CRUD | `/api/lessons/` | Manage lessons (by module_id) |
| CRUD | `/api/quizzes/` | Manage quizzes |
| CRUD | `/api/quiz-questions/` | Manage questions (by quiz_id) |
| CRUD | `/api/quiz-choices/` | Manage choices (by question_id) |
| GET | `/api/quiz-attempts/` | View student attempts |
| GET | `/api/mentor-analytics/` | View course stats |
| POST | `/api/courses/{id}/qna/questions/{qid}/pin/` | Pin Q&A question |

### Admin only

| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/api/admin/users/` | List all users |
| POST | `/api/admin/users/{id}/ban/` | Ban/unban user |
| GET | `/api/admin/mentors/pending/` | List pending mentors |
| POST | `/api/admin/mentors/{id}/approve/` | Approve mentor |
| POST | `/api/admin/mentors/{id}/reject/` | Reject mentor |
| GET | `/api/admin/courses/pending/` | List pending courses |
| POST | `/api/admin/courses/{id}/approve/` | Approve course |
| POST | `/api/admin/courses/{id}/reject/` | Reject course (with reason) |
| GET | `/api/admin/reviews/flagged/` | List flagged reviews |
| DELETE | `/api/admin/reviews/{id}/delete_review/` | Delete review |
| GET | `/api/admin/qna/flagged/` | List flagged Q&A |
| DELETE | `/api/admin/qna/{id}/delete_question/` | Delete question |
| DELETE | `/api/admin/qna/{id}/delete_reply/` | Delete reply |
| GET | `/api/admin/refunds/` | List refund requests |
| POST | `/api/admin/refunds/{id}/approve/` | Process refund |
| POST | `/api/admin/refunds/{id}/reject/` | Reject refund |
| GET | `/api/admin/reports/` | Platform statistics |

---

## 7. WebSocket Architecture

There are two WebSocket channels, both served by the same Daphne ASGI process.

### Channel 1: Notifications (`/ws/notifications/`)

```
Connection: ws://host:8001/ws/notifications/?token=JWT_TOKEN

On connect:
  1. Consumer decodes JWT from query string
  2. Authenticates user
  3. Joins Redis group "notifications_{user_id}"

On notification event:
  1. Backend calls create_notification() → utils.py
  2. Saves to PostgreSQL
  3. Sends to Redis channel "notifications_{user_id}" via async_to_sync(channel_layer.group_send)
  4. Consumer's notification_message handler sends JSON to WebSocket client

On disconnect:
  Leaves Redis group
```

### Channel 2: Course Q&A (`/ws/course/{course_id}/qa/`)

```
Connection: ws://host:8001/ws/course/{course_id}/qa/?token=JWT_TOKEN

On connect:
  1. Consumer decodes JWT, authenticates
  2. Joins Redis group "course_qa_{course_id}"

Message types (server → client):
  - new_question — new question posted in this course
  - new_reply — new reply posted in this course
  - new_answer — from legacy Q&A (interactions app)

On create (QuestionViewSet or ReplyViewSet):
  1. Saves to PostgreSQL
  2. Calls broadcast_to_course(course_id, event_type, data)
  3. Sends to Redis group "course_qa_{course_id}"
  4. All connected clients receive real-time update
```

### Why Redis is only a channel layer

Redis has no other role in this application — it does not cache any data, store sessions, or hold rate limits. Every REST request goes directly from Django to PostgreSQL. Redis only sits in the middle for WebSocket message routing:

```
Backend → Django Channels → Redis Pub/Sub → Daphne → WebSocket Client
```

The `channels_redis.pubsub.RedisPubSubChannelLayer` uses Redis pub/sub (not lists or streams), so messages are fire-and-forget — if a WebSocket client is disconnected, they miss that message. The `useNotifications` hook fetches unread notifications via REST on mount to catch up.

---

## 8. Payment Flow (End-to-End)

### Free course

```
1. Student clicks "Enroll Free" on CourseDetails page
2. Frontend → POST /api/enrollments/enroll_free/ (with course_id)
3. Backend → creates Enrollment (ACTIVE), sends notification
4. Student can immediately access course content
```

### Paid course (Stripe)

```
1. Student clicks "Purchase" (price shown)
2. Frontend → POST /api/enrollments/create_stripe_checkout/ (with course_id)
3. Backend creates:
   a. Stripe CheckoutSession via API (success_url, cancel_url, line_items)
   b. Payment record (PENDING) with provider_payment_id = session_id
   c. Returns { url: "https://checkout.stripe.com/..." }
4. Browser redirects to Stripe hosted checkout page
5. Student enters card details on Stripe's page
6a. PRIMARY PATH — Stripe webhook:
    - Stripe sends POST /api/webhooks/stripe/ with event "checkout.session.completed"
    - Backend verifies signature with STRIPE_WEBHOOK_SECRET
    - Finds Payment by session_id
    - Updates Payment to COMPLETED, sets payment_intent_id
    - Creates Enrollment (ACTIVE)
    - Sends notification (type=ENROLLMENT)
6b. FALLBACK PATH — Client-side verification:
    - Stripe redirects browser to frontend success URL with ?session_id=...
    - Frontend → POST /api/enrollments/verify_stripe_session/ (with session_id)
    - Backend checks if Enrollment already exists (from webhook)
    - If not, creates it idempotently (same logic as webhook)
7. Frontend redirects to CourseDetails page with "Enrolled" state
```

### Paid course (PayPal)

```
1. Student clicks "Purchase with PayPal"
2. Frontend → POST /api/enrollments/create_paypal_order/ (with course_id)
3. Backend creates:
   a. PayPal payment via PayPal REST API
   b. Payment record (PENDING) with provider_payment_id = payment_id
   c. Returns approval_url
4. Browser redirects to PayPal
5. Student approves on PayPal
6. PayPal redirects back to frontend with paymentId + PayerID
7. Frontend → POST /api/enrollments/capture_paypal_payment/ (with paymentId, PayerID)
8. Backend executes PayPal payment, creates Enrollment, sends notification
```

---

## 9. Role-Based Access Control

### How roles are checked

**Frontend** — reads from `localStorage`:

```
localStorage: { access, refresh, role, username }
```

The Navbar renders different links based on `role`. The `AdminRoute` component wraps `/admin` and redirects non-admins.

**Backend** — three levels:

| Level | Mechanism | Example |
|-------|-----------|---------|
| ViewSet level | `permission_classes` | `AnnouncementViewSet: [IsAuthenticated]` — any logged-in user |
| Action level | Custom permissions | `IsMentorOrReadOnly` — write requires MENTOR/ADMIN |
| Object level | `has_object_permission` | `IsOwnerOrAdmin` — only the resource's mentor or admin can edit |

### Data isolation

| Data | Student sees | Mentor sees | Admin sees |
|------|-------------|-------------|------------|
| Courses | Published only | Own + published | All |
| Enrollments | Own only | Their course enrollments | None (via admin views) |
| Progress | Own only | Their course students' | None (via admin views) |
| Notifications | Own only | Own only | N/A |
| Reviews | Non-flagged only | Non-flagged only | All (flagged via admin) |
| Q&A | Course Q&A (enrolled) | Their course Q&A | All |

---

## 10. Search System

The search is built on PostgreSQL full-text search, not Elasticsearch or any external search service.

**Search pipeline** (in `courses/search.py`):

```
User types "python django"
  │
  ▼
1. SearchVector on Course model:
   - title (weight A)
   - tags (weight B)
   - category (weight C)
   - description (weight D)
  │
  ▼
2. SearchRank ranks results by relevance
  │
  ▼
3. If no results → TrigramSimilarity on title (fuzzy match)
  │
  ▼
4. If still no results → icontains on title, description, tags, category, mentor__username
```

The autocomplete endpoint uses the same pipeline but limits to 7 results.

---

## 11. Deployment Architecture

### Local development (`docker-compose.yml`)

```
Services:
  db (postgres:16-alpine)    :5432
  redis (redis:7-alpine)     :6379
  mailpit                    :1025 (SMTP) + :8025 (UI)
  backend                    :8000 (Django dev server)
  daphne                     :8001 (ASGI server)
  frontend                   :5173 (Vite dev server)
```

The backend and daphne run the same Docker image but different commands:
- **backend** runs `python manage.py runserver 0.0.0.0:8000` (Django dev server, HTTP only)
- **daphne** runs `daphne -b 0.0.0.0 -p 8001 core.asgi:application` (ASGI server, HTTP + WebSocket)

In production (Render), there is only one server process (daphne) that handles both HTTP and WebSocket.

### Production (Render.com)

Defined in `render.yaml` as a **Blueprint** (infrastructure-as-code):

| Service | Type | Key Config |
|---------|------|-----------|
| **learning-platform-db** | PostgreSQL database | Auto-generated |
| **learning-platform-redis** | Redis | ipAllowList: [] (private network) |
| **learning-platform-backend** | Web service | Start command: `migrate && generate_all_content && download_thumbnails && create_admin && daphne` |
| **learning-platform-frontend** | Static site | Build: `npm run build`, publish `dist` |

### Startup command chain

Every time the backend deploys or restarts, it runs this sequence:

```
1. python manage.py migrate           ← Apply any pending DB migrations
2. python manage.py generate_all_content  ← Generate/regenerate all 128 lessons' content
3. python manage.py download_thumbnails   ← Download Unsplash images for course thumbnails
4. python manage.py create_admin          ← Ensure admin user exists (admin/Admin@123)
5. daphne -b 0.0.0.0 -p $PORT core.asgi:application  ← Start ASGI server
```

Steps 2-4 are necessary because Render's filesystem is ephemeral — content and images don't persist between deploys.

---

## 12. Environment Variables

| Variable | Used By | What It Controls |
|----------|---------|-----------------|
| `DEBUG` | Django | Debug mode on/off |
| `SECRET_KEY` | Django | Cryptographic signing |
| `ALLOWED_HOSTS` | Django | Allowed hostnames |
| `DATABASE_URL` | Django | PostgreSQL connection (host, port, db, user, password) |
| `REDIS_URL` | Channels | Redis connection for channel layer |
| `CORS_ALLOWED_ORIGINS` | django-cors-headers | Frontend origin(s) allowed cross-origin |
| `FRONTEND_URL` | Django | Used for redirect URLs in payment flows |
| `STRIPE_SECRET_KEY` | Stripe SDK | Stripe API server-side key |
| `STRIPE_PUBLISHABLE_KEY` | Stripe SDK | Stripe API client-side key (used by frontend) |
| `STRIPE_WEBHOOK_SECRET` | Stripe SDK | Verifies webhook signatures |
| `PAYPAL_CLIENT_ID` | PayPal SDK | PayPal REST API client ID |
| `PAYPAL_CLIENT_SECRET` | PayPal SDK | PayPal REST API secret |
| `PAYPAL_CURRENCY` | PayPal SDK | Default currency (USD) |
| `EMAIL_HOST` / `EMAIL_PORT` | Django | SMTP server for outgoing email |
| `EMAIL_USE_TLS` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Django | SMTP credentials |
| `DEFAULT_FROM_EMAIL` | Django | Sender address for platform emails |
| `VITE_API_URL` / `VITE_WS_URL` | Vite | API and WebSocket URLs embedded in frontend build |
