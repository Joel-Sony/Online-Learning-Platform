# Phase 7 — Notifications & Search

## Summary
Phase 7 focused on enhancing platform engagement through real-time communication and improving course discoverability. We implemented a robust notification system and an advanced search interface.

## Technical Implementation

### Real-time Notifications
- **Notification Model**: A centralized model in the `notifications` app to track alerts for enrollments, new content, and interactions.
- **WebSocket Integration**: Leveraging Django Channels to push live updates to users. Authenticated via JWT query parameters for secure real-time connectivity.
- **Automated Triggers**: Notifications are automatically generated and broadcasted on:
    - Successful course enrollments.
    - New lessons added by mentors.
    - New answers posted in course Q&A.
    - Refund processing.
    - Mentor announcements.

### Advanced Search & Discovery
- **Enhanced Course Querying**: Integrated `django-filter` and DRF `SearchFilter` to provide powerful filtering capabilities.
- **Annotated Metrics**: Courses are dynamically annotated with average ratings and enrollment counts to enable sorting by popularity and quality.
- **Discovery Sidebar**: A new frontend interface for filtering courses by level, language, price range, and rating.
- **Mentor Discovery**: A dedicated search endpoint for finding mentors and reviewing their aggregate stats.

## Core Components

### Backend
- `notifications.utils.create_notification`: Unified helper for creating and broadcasting alerts.
- `courses.filters.CourseFilter`: Advanced filterset for course discovery.
- `CourseViewSet.get_queryset`: Annotated and optimized querying.

### Frontend
- `useNotifications`: Custom hook encapsulating notification state and WebSocket logic.
- `NotificationDropdown`: Navbar component with unread badges and time-ago formatting.
- `CourseList`: Discovery page with responsive filter sidebar.

## API Routes
- `GET /api/notifications/`: List user notifications.
- `POST /api/notifications/{id}/read/`: Mark as read.
- `POST /api/notifications/read-all/`: Mark all as read.
- `WS /ws/notifications/`: Real-time notification stream.
- `GET /api/courses/`: Advanced filtering and search.
- `GET /api/mentors/search/`: Mentor performance discovery.
