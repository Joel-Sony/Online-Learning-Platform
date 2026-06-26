# Phase 6: Interaction System & Real-Time Q&A

## Overview
Phase 6 enriched the platform with social features, allowing students to rate courses, review content, and engage in real-time discussions with mentors and peers.

## 1. Ratings & Reviews
- **Review System**: Students can leave a 1-5 star rating and text review.
- **Enforcement**: Only enrolled students can leave reviews, and only one review is allowed per course/student pair.
- **Aggregation**: Course average ratings and review counts are calculated in real-time using Django database aggregation.

## 2. Real-Time Q&A Room
- **WebSocket Protocol**: Built using Django Channels and Redis to handle asynchronous communication.
- **Broadcasting**: When a student asks a question or posts an answer, the backend broadcasts the event to all connected users in that course's room.
- **Persistance**: All discussions are saved to the database for future reference by new students.
- **Group isolation**: Discussion rooms are isolated by `course_id`.

## 3. Moderation & Abuse Reporting
- **Reporting**: Users can flag reviews for moderation.
- **Moderation**: Flags are tracked via the `ReviewReport` model. Admins can toggle the `is_flagged` status on reviews to hide inappropriate content.

## 4. API Endpoints
| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/reviews/` | POST | Enrolled | Submit a course review. |
| `/reviews/course_ratings/` | GET | Public | Get aggregate stats for a course. |
| `/questions/` | GET/POST | Auth | List/Ask questions. |
| `/answers/` | POST | Auth | Respond to a question. |
| `/reports/` | POST | Auth | Report a review. |

## 5. Frontend Features
- **Rating Overlay**: Home page shows average stars for each course.
- **Review Section**: Course detail page includes a scrollable review feed and submission form.
- **Live Q&A Page**: A dedicated real-time discussion board for each course.

## 6. Testing Performed
1. **Concurrency Check**: Verified that posting a question in one browser tab immediately triggers a UI update in another tab without refreshing.
2. **Permission Check**: Verified that non-enrolled users receive a "403 Forbidden" when attempting to POST to the reviews endpoint.
3. **Aggregation Verification**: Verified that the average rating updates immediately after a new 5-star review is submitted.

## 7. Known Limitations
- Rich text editing (Markdown/HTML) for reviews and questions is not yet supported.
- Redis is required in the environment for WebSocket broadcasting to function.
