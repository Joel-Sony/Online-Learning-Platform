# CLAUDE_PROJECT_RULES.md

# Objective

Build a complete Online Learning Platform that satisfies all assignment requirements while keeping complexity as low as possible.

The primary goal is:

1. Functional correctness.
2. Readability.
3. Maintainability.
4. Simplicity.

The goal is NOT to demonstrate advanced architecture or maximize technology usage.

---

# Core Development Philosophy

Always choose:

* Simple over clever.
* Explicit over abstract.
* Readable over optimized.
* Working over perfect.

Assume the code will be reviewed by:

* Internship mentors
* College evaluators
* Junior developers

The code should be easy to explain.

---

# Technology Constraints

Use the minimum number of technologies required.

Preferred stack:

Backend:

* Django
* Django REST Framework
* PostgreSQL

Frontend:

* React
* React Router
* Axios

Authentication:

* JWT

Realtime:

* Django Channels
* Redis

Payments:

* Stripe Sandbox
* PayPal Sandbox

Deployment:

* Docker
* AWS or equivalent cloud

Do NOT introduce:

* Microservices
* Kubernetes
* GraphQL
* CQRS
* Event Sourcing
* Repository Pattern
* Domain Driven Design
* Redux
* Zustand
* RabbitMQ
* Kafka

unless explicitly required.

Build a modular monolith.

---

# Implementation Strategy

Never build the entire system at once.

Implement in phases.

---

## Phase 1 - Project Setup

Create:

* Django project
* React project
* PostgreSQL configuration
* Environment variables
* Docker setup

Verify project runs.

---

## Phase 2 - Authentication

Implement:

* Registration
* Login
* JWT access token
* JWT refresh token
* Logout

Roles:

* Student
* Mentor
* Admin

Verify permissions work.

Only continue when authentication is complete.

---

## Phase 3 - Course Management

Implement:

* Course creation
* Course editing
* Course publishing
* Modules
* Lessons

Supported lesson content:

* Video URL
* PDF upload
* Document upload

Do not implement advanced media processing.

Store files simply.

---

## Phase 4 - Enrollment

Implement:

* Browse courses
* Course details
* Enrollment

For paid courses:

* Create enrollment after successful payment

Keep logic simple.

---

## Phase 5 - Learning Progress

Implement:

* Lesson completion
* Progress percentage
* Course completion

Certificates may be generated as PDF.

Use a simple implementation.

---

## Phase 6 - Ratings & Reviews

Implement:

* One review per student per course
* Star rating
* Review text
* Moderation flag

Average rating can be calculated using database aggregation.

Avoid unnecessary optimization.

---

## Phase 7 - Notifications & Search

Implement:

* In-app notifications
* WebSocket notification updates
* Email notifications

Supported events:

* Enrollment
* New lesson
* New answer
* Refund
* Announcement

Search & Discovery:

* Course search
* Mentor search
* Filters

Filters:

* Price
* Level
* Duration
* Language
* Rating

Optional:

* Elasticsearch integration
* Autocomplete
* Popularity sorting

Keep implementation straightforward.
## Phase 8 - Q&A System

Implement:

* Per-course discussion room
* Questions
* Replies
* Mentor responses

Persist all messages in database.

Implement threading only if reasonably simple.

Avoid complex chat architectures.

## Phase 9 - Payments

Implement:

* Stripe Sandbox
* PayPal Sandbox

Required:

* Successful payment
* Webhook verification
* Enrollment creation
* Refund support

Only implement assignment requirements.

Avoid subscription systems.

---

## Phase 10 - Search

Start with PostgreSQL search.

Only add Elasticsearch if assignment explicitly requires it and simpler approaches cannot satisfy requirements.

Implement:

* Course search
* Mentor search
* Filters

Filters:

* Price
* Level
* Duration
* Language
* Rating

---

## Phase 11 - Admin Features

Implement:

* User management
* Mentor approval
* Course approval
* Content moderation
* Refund handling
* Reports

Reports can be simple dashboards.

Do not create a complex analytics pipeline.

---

# Database Rules

Before writing APIs:

1. Design entities.
2. Design relationships.
3. Review schema.

Create ER diagram first.

Core entities:

* User
* Course
* Module
* Lesson
* Enrollment
* Progress
* Review
* Notification
* ChatMessage
* Payment

Keep schema normalized and straightforward.

---

# API Rules

Create REST APIs.

Example:

GET /courses
POST /courses
GET /courses/{id}
POST /courses/{id}/enroll

Use predictable naming.

Avoid unnecessary endpoint complexity.

---

# Frontend Rules

Prefer:

Pages:

* Login
* Register
* Course List
* Course Details
* Learning Dashboard
* Admin Dashboard
* Mentor Dashboard

Keep state local where possible.

Use React Context only when necessary.

Do not introduce Redux.

---

# Code Quality Rules

Functions should:

* Do one thing.
* Be easy to understand.
* Use descriptive names.

Avoid large files and deeply nested logic.

Avoid premature abstractions.

Do not create helper files, services, hooks, or utilities unless they provide real value.

---

# Documentation Rules

After every completed feature provide:

* Files created
* Files modified
* Database changes
* API endpoints
* Manual testing steps

Keep documentation concise.

---

# Completion Criteria

A feature is complete only when:

* Backend implemented
* Frontend connected
* Validation present
* Error handling present
* Permissions enforced
* Tested manually

Do not mark work complete before all conditions are satisfied.

---

# Final Rule

Whenever multiple solutions are possible, choose the one that a junior developer can understand in under five minutes.
