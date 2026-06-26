# Phase 8 — Q&A System

## Summary
Phase 8 introduced a modern, threaded Q&A system for course-specific discussions. This replaced the basic interaction system with a more robust architecture supporting one-level nesting, mentor verification, and pinning of important discussions.

## Technical Implementation

### Threaded Discussion Model
- **Nested Architecture**: Implemented `Question` and `Reply` models in a dedicated `qna` app. Replies support a single level of nesting via a `parent` self-relationship.
- **Mentor Recognition**: Automatically identifies and badges responses from course mentors using the `is_mentor_response` flag, which is auto-set in the backend based on user roles.
- **Pinning Mechanism**: Mentors and admins can pin high-quality or frequently asked questions to the top of the course Q&A board.

### Real-time & Permissions
- **Channel Broadcasts**: Integrated with existing WebSocket infrastructure to push new questions and replies to all users currently viewing the course Discussion Room.
- **Enforced Scoping**: All Q&A activity is scoped to specific courses. Students must be enrolled in a course to participate in its discussions.
- **Automated Notifications**: Mentors are automatically notified when students post questions, and students receive alerts when mentors reply to their queries.

## Core Components

### Backend
- `qna.models.Question`: Core discussion entity with pinning and search support.
- `qna.models.Reply`: Threaded responses with mentor verification logic.
- `qna.views.QuestionViewSet`: Handles course-scoped questions and pinning actions.
- `qna.views.ReplyViewSet`: Manages nested replies and triggers notifications.

### Frontend
- `QAPage`: Unified discussion board with real-time updates.
- `QuestionCard`: Responsive card displaying question details and its threaded replies.
- `ReplyItem`: Component for individual replies with mentor badges and nested reply support.
- `ReplyForm`: Dynamic form for posting both top-level and nested replies.

## API Routes
- `GET /api/courses/{id}/qna/questions/`: List course questions (pinned shown first).
- `POST /api/courses/{id}/qna/questions/`: Post a new question.
- `POST /api/courses/{id}/qna/questions/{id}/pin/`: Pin a question (Mentor/Admin only).
- `GET /api/courses/{id}/qna/questions/{id}/replies/`: List replies for a question.
- `POST /api/courses/{id}/qna/questions/{id}/replies/`: Post a reply.
- `WS /ws/course/{id}/qa/`: Real-time discussion stream.
