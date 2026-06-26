# Phase 2: Authentication Implementation

## Overview
Phase 2 implemented a robust, role-based authentication system using JSON Web Tokens (JWT).

## 1. Custom User Model
A custom user model was implemented in `users.models.User` to support the platform's role-based architecture.

### Key Fields:
- `role`: Choices of `STUDENT`, `MENTOR`, or `ADMIN`.
- `is_mentor_approved`: Boolean flag for mentor verification.
- `bio` and `profile_picture`: Extended profile fields.

## 2. JWT Configuration
The system uses `djangorestframework-simplejwt` for authentication.
- **Access Tokens**: 60-minute lifetime.
- **Refresh Tokens**: 24-hour lifetime.
- **Header Type**: `Bearer`.

## 3. API Endpoints
All authentication endpoints are prefixed with `/api/users/`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register/` | POST | Register a new user with a specific role. |
| `/login/` | POST | Obtain access and refresh tokens. |
| `/token/refresh/` | POST | obtain a new access token using a refresh token. |
| `/me/` | GET | Retrieve/update current authenticated user's profile. |

## 4. Role System
Roles are enforced at the database level and can be used in upcoming phases to restrict access to specific views (e.g., student-only or mentor-only features).
- **STUDENT**: Default role upon registration.
- **MENTOR**: Requires approval for certain features (to be implemented in Phase 3/11).
- **ADMIN**: Full system access.

## 5. Manual Testing Steps
### Prerequisites
- Backend services running (e.g., via `docker-compose up`).

### Step 1: User Registration
- **URL**: `http://localhost:8000/api/users/register/`
- **Method**: `POST`
- **Body** (JSON):
  ```json
  {
      "username": "teststudent",
      "password": "testpassword123",
      "email": "student@example.com",
      "role": "STUDENT"
  }
  ```
- **Expected Result**: `201 Created` with user details (excluding password).

### Step 2: User Login
- **URL**: `http://localhost:8000/api/users/login/`
- **Method**: `POST`
- **Body** (JSON):
  ```json
  {
      "username": "teststudent",
      "password": "testpassword123"
  }
  ```
- **Expected Result**: `200 OK` with `access` and `refresh` tokens.

### Step 3: Access Protected Route
- **URL**: `http://localhost:8000/api/users/me/`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Expected Result**: `200 OK` with the authenticated user's profile.

### Step 4: Token Refresh
- **URL**: `http://localhost:8000/api/users/token/refresh/`
- **Method**: `POST`
- **Body** (JSON):
  ```json
  {
      "refresh": "<refresh_token>"
  }
  ```
- **Expected Result**: `200 OK` with a new `access` token.
