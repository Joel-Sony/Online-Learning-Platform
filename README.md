# Online Learning Platform

A full-stack online learning marketplace where students can discover, purchase, and consume courses; mentors can create and manage courses; and admins oversee the platform.

---

## Features

- **Role-based system** — Students, Mentors, and Admins with separate dashboards
- **Course management** — Create courses with modules, lessons (video/markdown), and quizzes
- **Payments** — Stripe and PayPal integration for paid courses; free enrollment option
- **Progress tracking** — Mark lessons complete, auto-generate certificates on completion
- **Quizzes** — Per-module quizzes with auto-grading and pass/fail
- **Real-time Q&A** — Course-specific Q&A rooms powered by WebSockets
- **Notifications** — In-app, real-time push, and email notifications
- **Search** — Full-text course search with filters (price, level, category, rating)
- **Admin panel** — User management, mentor/course approval, review moderation, refunds

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django, Django REST Framework, Django Channels |
| Frontend | React, Vite, React Router, Axios |
| Database | PostgreSQL |
| Real-time | Redis (WebSocket pub/sub) |
| Payments | Stripe, PayPal |

---

## Run Locally

**Prerequisites:** Docker and Docker Compose.

```bash
git clone <repo-url>
cd Online-Learning-Platform
docker compose up --build
```

This starts 6 services:
- **db** — PostgreSQL
- **redis** — Redis
- **mailpit** — Dev email UI at `http://localhost:8025`
- **backend** — Django dev server on `http://localhost:8000`
- **daphne** — ASGI server (WebSockets) on `http://localhost:8001`
- **frontend** — Vite dev server on `http://localhost:5173`

Open `http://localhost:5173` in your browser.

### Environment

Copy `backend/.env.example` to `backend/.env` and adjust if needed. The defaults work with Docker Compose.

---

## Default Credentials

An admin user is created automatically on startup:

- **Username:** `admin`
- **Password:** `Admin@123`

---

## Project Structure

```
backend/          Django REST API (7 apps)
frontend/         React SPA
docs/             Architecture docs and presentation
docker-compose.yml   Local dev setup
render.yaml         Production deployment config
```
