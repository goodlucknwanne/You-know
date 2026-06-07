# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing course enrollments. Features JWT authentication, role-based access control (RBAC), PostgreSQL persistence, Alembic migrations, and a comprehensive automated test suite.

---

## Features

- **JWT Authentication** — secure register/login with bcrypt password hashing
- **Role-Based Access Control** — `student` and `admin` roles with distinct permissions
- **Course Management** — admin CRUD with unique codes, capacity, and active/inactive state
- **Enrollment Management** — students enroll/deregister; full enforcement of business rules
- **Admin Oversight** — view all enrollments, manage by course, remove students
- **Validation** — Pydantic v2 request validation with meaningful error responses
- **Testing** — 50+ tests covering all endpoints and edge cases using in-memory SQLite

---

## Project Structure

```
enrollment_platform/
├── app/
│   ├── api/
│   │   ├── deps.py               # Auth/RBAC dependencies
│   │   ├── router.py             # Aggregates all routers
│   │   └── endpoints/
│   │       ├── auth.py           # /api/v1/auth/*
│   │       ├── courses.py        # /api/v1/courses/*
│   │       └── enrollments.py    # /api/v1/enrollments/*
│   ├── core/
│   │   ├── config.py             # Settings (env vars)
│   │   └── security.py           # JWT + password hashing
│   ├── db/
│   │   └── session.py            # SQLAlchemy engine & session
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── course.py
│   │   └── enrollment.py
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── enrollment.py
│   │   └── token.py
│   ├── services/                 # Business logic layer
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   └── enrollment_service.py
│   └── main.py                   # FastAPI app entry point
├── migration/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py        # Initial migration
├── tests/
│   ├── conftest.py               # Fixtures and test helpers
│   ├── test_auth.py              # Auth endpoint tests
│   ├── test_courses.py           # Course endpoint tests
│   ├── test_enrollments.py       # Enrollment endpoint tests
│   └── test_security.py         # Unit tests for JWT & hashing
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## Setup Instructions

### 1. Clone and install dependencies

```bash
git clone <your-repo>
cd enrollment_platform

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/enrollment_db
SECRET_KEY=your-random-secret-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE enrollment_db;"
```

---

## Running Migrations

```bash
# Apply all migrations (creates tables)
alembic upgrade head

# Check current migration state
alembic current

# View migration history
alembic history

# Rollback last migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API base:** `http://localhost:8000/api/v1`
- **Interactive docs:** `http://localhost:8000/docs`
- **OpenAPI schema:** `http://localhost:8000/openapi.json`
- **Health check:** `http://localhost:8000/health`

---

## Running Tests

Tests use an in-memory SQLite database — **no PostgreSQL required**.

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_auth.py -v

# Run a specific test class or function
pytest tests/test_enrollments.py::TestEnroll::test_enrollment_fails_when_course_full -v
```

---

## API Reference

### Authentication

| Method | Endpoint              | Description             | Auth     |
|--------|-----------------------|-------------------------|----------|
| POST   | `/api/v1/auth/register` | Register new user       | None     |
| POST   | `/api/v1/auth/login`    | Login, receive JWT      | None     |
| GET    | `/api/v1/auth/me`       | Get own profile         | Any user |

### Courses

| Method | Endpoint                  | Description               | Auth    |
|--------|---------------------------|---------------------------|---------|
| GET    | `/api/v1/courses/`        | List all active courses   | Public  |
| GET    | `/api/v1/courses/{id}`    | Get course by ID          | Public  |
| POST   | `/api/v1/courses/`        | Create course             | Admin   |
| PUT    | `/api/v1/courses/{id}`    | Update course             | Admin   |
| DELETE | `/api/v1/courses/{id}`    | Delete course             | Admin   |

### Enrollments

| Method | Endpoint                              | Description                        | Auth    |
|--------|---------------------------------------|------------------------------------|---------|
| POST   | `/api/v1/enrollments/{course_id}`     | Enroll in a course                 | Student |
| DELETE | `/api/v1/enrollments/{course_id}`     | Deregister from a course           | Student |
| GET    | `/api/v1/enrollments/`               | List all enrollments               | Admin   |
| GET    | `/api/v1/enrollments/course/{id}`    | List enrollments for a course      | Admin   |
| DELETE | `/api/v1/enrollments/admin/{id}`     | Remove enrollment by ID            | Admin   |

---

## Business Rules Enforced

- Email must be unique across all users
- Inactive users cannot authenticate
- Course codes must be unique
- Course capacity must be > 0
- Students cannot enroll in the same course twice
- Students cannot enroll in full or inactive courses
- Only admins can create, update, or delete courses
- Only students can enroll or deregister
- Admins can forcibly remove any enrollment

---

## Deployment (Cloud)

### Option A: Railway / Render

1. Push to GitHub
2. Connect repo to Railway or Render
3. Set environment variables in the dashboard
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add a PostgreSQL plugin/addon and set `DATABASE_URL`
6. Run migrations via one-off command: `alembic upgrade head`

### Option B: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t enrollment-api .
docker run -p 8000:8000 --env-file .env enrollment-api
```