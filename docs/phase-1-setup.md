# Phase 1 Setup Documentation

## Overview
Phase 1 involved initializing the core project structure, configuring the environment, and setting up Docker containers for the modular monolith architecture.

## 1. Projects Initialized
- **Backend**: Django 5.x project named `core` located in the `/backend` directory.
- **Frontend**: React project (Vite) located in the `/frontend` directory.

## 2. Docker Configuration
The project is orchestrated using `docker-compose`.

### Services:
- `db`: PostgreSQL 16 image.
- `backend`: Custom Dockerfile (Python 3.12-slim) running Django on port 8000.
- `frontend`: Custom Dockerfile (Node 20-slim) running Vite on port 5173.

## 3. Environment Variables
A `.env` file template was created in `/backend/.env` containing:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`
- `CORS_ALLOWED_ORIGINS`
- Sandbox keys for Stripe and PayPal.

## 4. Database Setup
- PostgreSQL is configured as the primary database.
- `django-environ` is used to parse the connection string from the environment.
- Initial volume `postgres_data` is defined for persistence.

## 5. Verification Steps
1. Run `docker-compose build` to build images.
2. Run `docker-compose up` to start services.
3. Access Django at `http://localhost:8000`.
4. Access Vite at `http://localhost:5173`.
