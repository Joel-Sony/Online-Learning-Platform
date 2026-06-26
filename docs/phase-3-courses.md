# Phase 3: Course Management Implementation

## Overview
Phase 3 focused on the core education functionality: creating, managing, and browsing courses, modules, and lessons.

## 1. Models and Relationships
- **Course**: The primary container for educational content.
    - Mentored by a `User`.
    - Contains multiple `Modules`.
- **Module**: Organizes lessons within a course.
    - Belongs to a `Course`.
    - Contains multiple `Lessons`.
    - Supports custom ordering via `order` field.
- **Lesson**: Individual content pieces.
    - Belongs to a `Module`.
    - Types: `VIDEO`, `PDF`, `DOCUMENT`.
    - Supports custom ordering via `order` field.
    - Uses standard Django `FileField` for document uploads.

## 2. API Endpoints
All course management endpoints are prefixed with `/api/`.

| Endpoint | Method | Role Required | Description |
|----------|--------|---------------|-------------|
| `/courses/` | GET | Public | List all published courses. Mentors see their own drafts. |
| `/courses/` | POST | mentor | Create a new course. |
| `/courses/{id}/` | GET | Public | Retrieve course details including curriculum. |
| `/courses/{id}/` | PATCH | owner/admin | Update course details or publishing status. |
| `/courses/{id}/` | DELETE | owner/admin | Remove a course. |
| `/modules/` | POST | mentor | Add a module to a course. |
| `/lessons/` | POST | mentor | Add a lesson to a module. |

## 3. Frontend Pages
- **Home (`/`)**: Browse and filter published courses.
- **Course Details (`/courses/{id}`)**: Detailed view of course description and curriculum structure.
- **Mentor Dashboard (`/mentor`)**: Manage owned courses, view publishing status.
- **Create Course (`/mentor/create`)**: Form to initialize a new course with metadata and thumbnail.
- **Edit Course (`/mentor/edit/{id}`)**: Update course info and manage modules/lessons.

## 4. Permissions and Validation
- **IsOwnerOrAdmin**: Ensures only the mentor who created the course (or an admin) can modify or delete it.
- **Visibility**: Unpublished courses are strictly excluded from student and public list/retrieve views.
- **Validation**:
    - Mentors are automatically assigned to courses they create.
    - Price and ordering fields are validated for positive values.

## 5. Testing Steps
### Backend Testing
1. **List Courses**:
   - As an unauthenticated user, `GET /api/courses/` should return only published courses.
   - As a mentor, it should return published courses + your own drafts.
2. **Access Control**:
   - Try to `PATCH` a course owned by another mentor. Expected: `403 Forbidden`.

### Frontend Testing
1. Login as a **Mentor**.
2. Navigate to `Mentor Dashboard`.
3. Create a course with status "Draft" (is_published=false).
4. Verify it does NOT appear on the Home page.
5. In the Dashboard, click "Edit" and set "Is Published" to true.
6. Verify it now appears on the Home page.

## 6. Known Limitations
- Ordering of modules/lessons is manual via an integer field (no drag-and-drop UI yet).
- Video lessons only support URLs (no direct video uploads to storage in this phase).
- File uploads are stored locally; S3 integration is planned for later phases.
