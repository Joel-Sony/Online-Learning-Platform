# Architecture Design — Online Learning Platform

## 1. Project Overview

A modular monolith online learning marketplace built with Django and React. The platform supports three user roles — **Students**, **Mentors**, and **Admins** — and covers the full lifecycle of online education: course creation, publishing, enrollment (free or paid), content delivery, progress tracking, quizzes, certificates, real-time Q&A, notifications, and administrative moderation.

---

## 2. System Architecture

The system follows a decoupled frontend/backend architecture communicating over HTTP REST and WebSocket.

```
Browser (React SPA)
    │
    ├── REST (JSON) ──────────────────► Django REST API ──► PostgreSQL
    │                                     (Daphne ASGI)
    │
    ├── WebSocket ────────────────────► Django Channels ──► Redis
    │                                     (pub/sub)
    │
    └── Payment Redirect ─────────────► Stripe / PayPal ──► Webhook ──► Django
```

**Key design decisions:**

- **Monolith over microservices** — simpler deployment, lower operational overhead, single codebase for all 7 backend apps.
- **PostgreSQL for everything** — search, transactions, and persistent storage in one database. No Elasticsearch or external search service needed.
- **Redis only for WebSocket pub/sub** — no caching, no session storage, no background queues. Keeps infrastructure minimal.
- **Daphne ASGI server** — handles both HTTP requests and WebSocket connections on the same process, avoiding a separate WSGI server.
- **JWT authentication** — stateless auth eliminates server-side sessions, enabling horizontal scaling without a shared session store.

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python, Django 5, Django REST Framework | API development, ORM, serialization |
| **Real-Time** | Django Channels, Daphne ASGI | WebSocket server for live features |
| **Frontend** | React 19, Vite 8, React Router 7 | Client-side SPA |
| **HTTP Client** | Axios | REST calls with JWT interceptor |
| **Database** | PostgreSQL 16 | All persistent data + full-text search |
| **Message Broker** | Redis 7 | Channel layer for WebSocket groups |
| **Payments** | Stripe SDK, PayPal REST SDK | Payment processing |
| **Containerization** | Docker, Docker Compose | Local development environment |
| **Deployment** | Render Blueprint (render.yaml) | Production hosting |
| **Auth** | SimpleJWT | JWT access/refresh token flow |
| **Image Processing** | Pillow | Thumbnail and profile picture handling |

---

## 4. Backend Application Structure

The backend is organized into 7 Django apps, each with its own models, views, serializers, and URLs.

```
backend/
├── core/              Django project config (settings, root URLs, ASGI/WSGI)
├── users/             Custom User model, JWT auth, registration, profile
├── courses/           Course/module/lesson CRUD, quizzes, search, filters
├── enrollments/       Enrollment management, Stripe/PayPal payments, webhooks, refunds
├── progress/          Lesson progress tracking, certificates, mentor analytics
├── notifications/     In-app notifications, announcements, WebSocket push, email
├── interactions/      Reviews, ratings, review reporting, legacy Q&A
└── qna/               Threaded course Q&A with real-time updates and pinning
```

### 4.1 Users App

Provides a custom **User** model with role-based access (STUDENT, MENTOR, ADMIN). Mentors require admin approval before they can create courses. Authentication uses JWT (60-minute access tokens, 24-hour refresh tokens) via SimpleJWT.

**Endpoints:** Register, Login, Token Refresh, Profile (GET/PATCH).

### 4.2 Courses App

Manages the educational content hierarchy:

- **Course** — container with metadata (title, description, price, category, level, language, tags, thumbnail, status)
- **Module** — ordered groups within a course
- **Lesson** — individual content pieces (VIDEO with YouTube URL, PDF, or DOCUMENT with Markdown content)
- **Quiz** — per-module assessments with questions, multiple-choice answers, and student attempts

Features full-text search using PostgreSQL's `SearchVector` with weighted ranking (title > tags > category > description), falling back to trigram similarity and `icontains`. Includes a filterset for price range, duration, rating, level, language, category, and free status.

Content is generated programmatically via management commands (`generate_all_content`) that write rich Markdown with embedded Unsplash images for all 128 lessons.

### 4.3 Enrollments App

Handles course enrollment and payment processing. Supports three enrollment paths:

- **Free enrollment** — immediate enrollment without payment
- **Stripe checkout** — browser redirects to Stripe hosted checkout; confirmation arrives via webhook (primary) or client-side verification (fallback)
- **PayPal order** — browser redirects to PayPal for approval; server-side capture finalizes payment

Refund workflow: student requests refund → payment marked REFUND_REQUESTED → admin approves (processes actual refund via Stripe/PayPal API) or rejects.

### 4.4 Progress App

Tracks lesson-level completion for each enrolled student. When all lessons in a course are marked complete, a **Certificate** is automatically generated with a unique ID. Certificates are downloadable as styled HTML.

Mentor analytics provide per-course enrollment counts and completion rates.

### 4.5 Notifications App

Multi-channel notification engine. When any system event occurs (enrollment, new lesson, new Q&A answer, refund, announcement), the system:

1. Saves a Notification record to the database
2. Broadcasts a real-time message via WebSocket to the recipient's notification channel
3. Sends an email via SMTP

Announcements are a special type where mentors broadcast messages to all enrolled students in a course.

### 4.6 Interactions App

Supports course reviews (1-5 star rating with text) and review reporting. Only enrolled students can review, and only one review per course per student is allowed. Flagged reviews are visible to admins for moderation.

### 4.7 Q&A App

Modern threaded Q&A system per course. Features:

- One level of threading (replies can have parent replies)
- Automatic mentor badge on responses from the course mentor
- Pinning of important questions by mentors or admins
- Real-time broadcasting via WebSocket to all users viewing the course Q&A room
- Automated notifications when mentors reply to student questions

---

## 5. Database Design

The database follows a relational schema with 15+ tables. Key relationships:

```
User (role-based)
  ├── mentors Course
  ├── enrolls in Course (via Enrollment)
  ├── writes Review
  ├── receives Notification
  ├── makes Payment
  └── earns Certificate

Course
  ├── has many Modules (ordered)
  │     └── has many Lessons (ordered) + Quizzes
  ├── has many Enrollments
  ├── has many Reviews
  ├── has many Notifications
  └── has many Payments

Lesson
  └── has many LessonProgress records (one per student)

Quiz
  ├── has many Questions
  └── has many Attempts (one per student)

Question
  └── has many Choices (one marked correct)

Notification
  └── polymorphic type (ENROLLMENT, NEW_LESSON, NEW_ANSWER, REFUND, ANNOUNCEMENT)
```

---

## 6. Authentication Flow

1. **Registration** — User submits username, email, password, and role. Backend creates the user record and returns JWT tokens.
2. **Login** — User provides credentials, receives access token (60 min) and refresh token (1 day).
3. **Authenticated requests** — Frontend Axios interceptor attaches `Authorization: Bearer <access_token>` to every request.
4. **Token refresh** — On HTTP 401, the interceptor automatically calls the refresh endpoint. If refresh fails, the user is redirected to login.
5. **Role enforcement** — Frontend controls UI visibility (nav links, routes) based on role stored in localStorage. Backend enforces via permission classes on every view.

---

## 7. Real-Time Features

Two WebSocket channels serve real-time functionality:

**Notifications Channel** (`/ws/notifications/`)
- Authenticated via JWT token in query string
- Receives push events for: enrollment confirmation, new lessons, Q&A answers, refund updates, announcements
- Frontend `useNotifications` hook manages the connection and state

**Q&A Channel** (`/ws/course/{course_id}/qa/`)
- Course-scoped discussion rooms
- Broadcasts new questions and replies to all connected users in that course
- Works alongside REST endpoints for persistence

Both channels use Redis pub/sub through Django Channels' `RedisPubSubChannelLayer` for message routing.

---

## 8. Payment Flow

**Free courses:** Immediate enrollment via API, no payment involved.

**Paid courses (Stripe):**
1. Frontend requests a Stripe Checkout Session from the backend
2. Backend creates the session via Stripe API and saves a PENDING payment record
3. Browser redirects to Stripe's hosted checkout page
4. After payment, Stripe sends a `checkout.session.completed` webhook to the backend
5. Backend verifies the webhook signature, creates the enrollment, marks payment as COMPLETED
6. As a fallback, the frontend also verifies the session on return (handles cases where the webhook arrives after the user)

**Paid courses (PayPal):**
1. Frontend requests a PayPal order from the backend
2. Backend creates the order via PayPal REST API and saves a PENDING payment record
3. Browser redirects to PayPal for user approval
4. On return, frontend sends the payment ID and payer ID to the backend
5. Backend captures (executes) the payment via PayPal API, creates the enrollment

**Refunds:**
1. Student requests refund from the learning dashboard
2. Admin reviews and approves/rejects from the admin panel
3. On approval, backend calls Stripe's refund API or PayPal's refund API
4. Enrollment status set to REFUNDED, notification sent to student

---

## 9. Deployment

**Local development** uses Docker Compose with 6 services:
- `db` (PostgreSQL 16)
- `redis` (Redis 7)
- `mailpit` (email capture UI)
- `backend` (Django dev server on port 8000)
- `daphne` (ASGI server on port 8001)
- `frontend` (Vite dev server on port 5173)

**Production** uses Render Blueprint (`render.yaml`) with auto-provisioned PostgreSQL, Redis, and Docker-based web services. The startup chain ensures fresh content on every deploy:

```
python manage.py migrate
python manage.py generate_all_content
python manage.py download_thumbnails
python manage.py create_admin
daphne -b 0.0.0.0 -p $PORT core.asgi:application
```

---

## 10. Development Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Project setup, Docker, database | Complete |
| 2 | Authentication, JWT, roles | Complete |
| 3 | Course/module/lesson CRUD | Complete |
| 4 | Enrollment & Stripe payments | Complete |
| 5 | Progress tracking & certificates | Complete |
| 6 | Reviews & legacy real-time Q&A | Complete |
| 7 | Notifications & search | Complete |
| 8 | Modern threaded Q&A system | Complete |
| 9 | PayPal multi-gateway & refunds | Complete |
| 10 | Admin features (moderation, reports) | Pending |

---

## 11. Known Limitations

- Video lessons only support URL linking (YouTube, etc.) — no direct video uploads
- File uploads use local storage — no S3 integration
- Progress tracking counts lesson completion — no time-spent tracking
- Certificates are styled HTML — no PDF generation yet
- No drag-and-drop UI for reordering modules/lessons
- No rich text editor for reviews and Q&A content

---

## 12. Future Roadmap

- OAuth/social login (Google, GitHub)
- Mobile apps (React Native / Flutter)
- Live streaming via WebRTC
- AI-powered course recommendations
- Multi-language support (i18n)
- Advanced analytics and student engagement metrics
- Coupon codes and promotional pricing
- Course bundles and subscription models
- Assignment submission with mentor grading
- Mentor revenue sharing and automated payouts
