# Architecture Documentation

This document describes the architectural patterns, design principles, and structure of the project template.

## Table of Contents

1. [Overview](#overview)
2. [Architectural Layers](#architectural-layers)
3. [Data Flow](#data-flow)
4. [Async-First Design](#async-first-design)
5. [Error Handling](#error-handling)
6. [Database Patterns](#database-patterns)
7. [Background Tasks](#background-tasks)
8. [Security](#security)
9. [Frontend Architecture](#frontend-architecture)

## Overview

This template follows a **layered architecture** pattern with clear separation of concerns. The backend is structured into distinct layers, each with specific responsibilities and communication patterns.

### Design Goals

- **Scalability**: Support horizontal scaling through async operations and worker processes
- **Maintainability**: Clear layer separation makes code easy to understand and modify
- **Type Safety**: Full type hints in Python, TypeScript in frontend
- **Performance**: Async-first design prevents blocking operations
- **Testability**: Each layer can be tested independently

## Architectural Layers

### Backend Layer Structure

```
┌─────────────────────────────────────────┐
│          API Layer (api/)               │  ← HTTP interface
├─────────────────────────────────────────┤
│       Service Layer (service/)          │  ← Business logic
├─────────────────────────────────────────┤
│        Domain Layer (domain/)           │  ← Core entities
├─────────────────────────────────────────┤
│     Repository Layer (repository/)      │  ← Data access
├─────────────────────────────────────────┤
│         Core Layer (core/)              │  ← Cross-cutting
└─────────────────────────────────────────┘
```

### 1. API Layer (`api/`)

**Responsibility**: HTTP interface and request/response handling

**Contains**:
- `routes/`: FastAPI route handlers
- `schemas.py`: Pydantic request/response models
- `exceptions.py`: Custom API exceptions
- `dependencies.py`: FastAPI dependency injection
- `app.py`: FastAPI application initialization

**Rules**:
- ✅ **100% async**: All route handlers must be async
- ✅ **No blocking operations**: Use async I/O for all operations
- ✅ **Thin layer**: Delegate business logic to service layer
- ✅ **Request validation**: Use Pydantic schemas for all inputs
- ✅ **Exception handling**: Only raise exceptions from `api/exceptions.py`
- ❌ **No direct database access**: Use service layer instead
- ❌ **No business logic**: Keep routes as simple coordinators

**Example**:
```python
@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignUpRequest,
    response: Response,
    db: AsyncSession = fastapi_db_dep,
) -> AuthResponse:
    # Delegate to service layer
    auth_service = AuthService(db)
    user, token = await auth_service.signup_user(request.email, request.password)

    # HTTP-specific logic (cookies, response)
    set_auth_cookie(response, token)
    return AuthResponse(message="User created successfully")
```

### 2. Service Layer (`service/`)

**Responsibility**: Business logic and transaction coordination

**Contains**:
- `base_service.py`: Base service class
- `auth_service.py`: Authentication business logic
- `user_service.py`: User management logic
- `security.py`: Password hashing and JWT utilities
- Additional service modules as needed

**Rules**:
- ✅ **All methods async**: Maintain async context
- ✅ **Business logic**: Implement domain rules and validation
- ✅ **Transaction management**: Coordinate database operations
- ✅ **Reusable**: Services can be called from API routes or background tasks
- ❌ **No HTTP concerns**: Don't reference Request/Response objects
- ❌ **No long-running tasks**: Use domain layer for heavy operations

**Example**:
```python
class AuthService(BaseService):
    async def signup_user(self, email: str, password: str) -> tuple[User, str]:
        # Business logic: check uniqueness
        existing_user = await self.db.scalars(
            select(User).where(User.email == email)
        ).one_or_none()

        if existing_user:
            raise UserAlreadyExistsException()

        # Business logic: create user
        hashed_password = get_password_hash(password)
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()

        # Business logic: generate token
        token = create_access_token({"sub": str(user.id)})
        return user, token
```

### 3. Domain Layer (`domain/`)

**Responsibility**: Core business entities and async task queue

**Contains**:
- `taskiq_broker.py`: Async task queue configuration
- Domain models (value objects, domain entities)
- Business rules that don't fit in services

**Rules**:
- ✅ **Long-running operations**: CPU-intensive or time-consuming tasks
- ✅ **Background tasks**: Email sending, report generation, etc.
- ✅ **Domain logic**: Pure business logic without external dependencies
- ❌ **No HTTP context**: Tasks run independently of web requests

**Example**:
```python
# domain/tasks.py
from domain.taskiq_broker import broker

@broker.task
async def send_welcome_email(user_id: str):
    """Send welcome email to new user (runs in background worker)."""
    # This can take several seconds without blocking API responses
    user = await get_user(user_id)
    await email_service.send_welcome(user.email)
```

### 4. Repository Layer (`repository/`)

**Responsibility**: Data persistence and database operations

**Contains**:
- `models.py`: SQLAlchemy ORM models
- `base_model.py`: Base model with common fields
- `connection.py`: Database session management
- `migrations/`: Alembic migration files

**Rules**:
- ✅ **Async operations**: Use async SQLAlchemy session
- ✅ **New mapped syntax**: Use SQLAlchemy 2.0 mapped_column syntax
- ✅ **Type annotations**: Use `Mapped[type]` for all columns
- ✅ **Migrations**: All schema changes via Alembic migrations
- ❌ **No business logic**: Just data access patterns

**Example**:
```python
class User(BaseTableModel):
    """User account model."""

    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    # Relationships example:
    # posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

### 5. Core Layer (`core/`)

**Responsibility**: Cross-cutting concerns and configuration

**Contains**:
- `settings.py`: Pydantic settings with environment variables
- `db.py`: Database session factory
- Logging configuration
- Monitoring setup (Sentry)

**Rules**:
- ✅ **Shared utilities**: Code used across multiple layers
- ✅ **Environment config**: All settings via environment variables
- ✅ **Type-safe settings**: Use Pydantic for configuration

## Data Flow

### Request Flow (Synchronous)

```
Client Request
    ↓
API Layer (route handler)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (database query)
    ↓
Database
    ↓
Repository Layer (model)
    ↓
Service Layer (transformation)
    ↓
API Layer (Pydantic schema)
    ↓
Client Response
```

### Background Task Flow

```
API Layer (route handler)
    ↓
Task Enqueued (taskiq.kiq())
    ↓
API Response Immediately
    ↓
Worker Process Picks Up Task
    ↓
Domain Layer (task execution)
    ↓
Service/Repository Layers
    ↓
Database/External Services
```

## Async-First Design

### Critical Rule: No Blocking in Request Path

**The API layer must NEVER block the async event loop during request processing.**

#### What's Allowed (Non-Blocking)

✅ **Async I/O operations**:
- `await db.execute(query)` - Database queries
- `await session.commit()` - Database commits
- `await http_client.get(url)` - HTTP requests
- `await redis.get(key)` - Cache operations

✅ **Fast CPU operations** (< 1ms):
- Password hashing (runs in thread pool automatically)
- JWT encoding/decoding
- Pydantic validation
- Simple data transformations

#### What's Forbidden (Blocking)

❌ **Long-running operations**:
- Image processing
- PDF generation
- Large file operations
- Complex calculations
- External API calls that might timeout
- Email sending (use background tasks)

#### Solution: Use Background Tasks

For operations that take > 100ms or have unpredictable timing:

```python
# ❌ WRONG: Blocks the event loop
@router.post("/generate-report")
async def generate_report(user_id: str):
    report = create_pdf_report(user_id)  # Takes 5 seconds!
    return report

# ✅ CORRECT: Enqueue background task
@router.post("/generate-report")
async def generate_report(user_id: str):
    await generate_report_task.kiq(user_id)
    return {"message": "Report generation started"}

# domain/tasks.py
@broker.task
async def generate_report_task(user_id: str):
    # Runs in separate worker process
    report = create_pdf_report(user_id)
    await store_report(report)
```

## Error Handling

### Exception Hierarchy

All API exceptions inherit from `APIException` and include:
- `status_code`: HTTP status code
- `internal_code`: Unique error code for frontend parsing
- `detail`: Human-readable error message

### Error Code Ranges

- **40000-40099**: Bad Request (400) errors
- **40100-40199**: Unauthorized (401) errors
- **40200-40299**: Forbidden (403) errors
- **40400-40499**: Not Found (404) errors
- **50000-59999**: Server (500) errors

### Adding New Exceptions

All exceptions must be defined in `api/exceptions.py`:

```python
class CustomException(BadRequestException):
    """Description of when this is raised."""

    internal_code = 40002  # Unique code
    detail = "User-friendly error message"
```

See `api/exceptions.py` for complete error code documentation.

## Database Patterns

### SQLAlchemy 2.0 Mapped Syntax

Always use the new mapped column syntax:

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from repository.base_model import BaseTableModel

class BlogPost(BaseTableModel):
    """Blog post model."""

    # Simple columns
    title: Mapped[str] = mapped_column(index=True)
    content: Mapped[str]

    # Optional columns
    subtitle: Mapped[str | None] = mapped_column(default=None)

    # Foreign keys
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))

    # Relationships
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")
```

### Async Session Usage

Always use async context managers:

```python
# ✅ CORRECT
async with get_session() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()

# ❌ WRONG: Sync operations
session = get_session()  # Don't do this
users = session.query(User).all()  # Blocking!
```

### Migrations

1. **Create migration**: `make migration MESSAGE="Add user profile"`
2. **Review migration**: Check generated file in `repository/migrations/versions/`
3. **Apply migration**: Automatic on backend startup, or `python main.py upgrade-database`

## Background Tasks

### Task Queue Architecture

```
API Request → Enqueue Task → Immediate Response
                    ↓
            Task Queue (Redis)
                    ↓
            Worker Process
                    ↓
            Task Execution
```

### When to Use Background Tasks

Use Taskiq for:
- **Email sending**: Welcome emails, notifications
- **Report generation**: PDFs, exports, analytics
- **Data processing**: Large file uploads, image processing
- **External API calls**: Third-party integrations with slow responses
- **Cleanup jobs**: Temporary file deletion, data archival

### Task Example

```python
# domain/tasks.py
from domain.taskiq_broker import broker
from service.email_service import EmailService

@broker.task
async def send_welcome_email_task(user_id: str):
    """Send welcome email to new user."""
    async with get_session() as session:
        email_service = EmailService(session)
        await email_service.send_welcome(user_id)

# api/routes/auth.py
@router.post("/signup")
async def signup(request: SignUpRequest):
    # ... create user ...

    # Enqueue background task
    await send_welcome_email_task.kiq(user.id)

    return {"message": "User created"}
```

## Security

### Authentication Flow

1. **User signup/signin**: Credentials validated
2. **JWT generation**: Token created with user ID
3. **Cookie storage**: Token stored in HTTP-only cookie
4. **Request authentication**: Middleware validates token from cookie
5. **User injection**: Current user injected into route handler

### Security Features

- **Argon2 password hashing**: Industry-standard password security
- **HTTP-only cookies**: Prevents XSS token theft
- **JWT tokens**: Stateless authentication
- **HTTPS support**: Secure cookie flag for production
- **Input validation**: Pydantic schemas validate all inputs

## Frontend Architecture

### Vue 3 Structure

```
frontend/src/
├── api/          # API client (Axios)
├── components/   # Reusable components
├── router/       # Vue Router (navigation)
├── store/        # Vuex (state management)
├── views/        # Page components
├── utils/        # Helper functions
└── styles/       # CSS files
```

### State Management (Vuex)

- **State**: Application data (user, auth status)
- **Mutations**: Synchronous state changes
- **Actions**: Async operations (API calls)
- **Getters**: Computed state values

### API Integration

- **Centralized Axios instance**: `api/apiClient.ts`
- **Error handling**: Custom `APIError` class
- **Base URL**: Configured via environment variables
- **Interceptors**: Automatic error parsing

### Authentication

- **Route guards**: `requiresAuth`, `requiresGuest`
- **Auto-redirect**: Unauthenticated users → login
- **State persistence**: Vuex stores auth state
- **Cookie-based**: JWT token in HTTP-only cookie (managed by backend)

## Best Practices

### Do's ✅

- Use async/await for all I/O operations
- Add comprehensive docstrings to functions
- Use type hints everywhere
- Write tests for business logic
- Use Pydantic for validation
- Keep layers separated
- Use background tasks for slow operations
- Document all exceptions

### Don'ts ❌

- Block the async event loop
- Mix layer responsibilities
- Skip input validation
- Ignore error handling
- Hard-code configuration
- Use sync database operations
- Put business logic in routes
- Create exceptions outside api/exceptions.py

## Extending the Template

### Adding a New Entity

1. **Create model**: Add SQLAlchemy model in `repository/models.py`
2. **Create migration**: `make migration MESSAGE="Add entity table"`
3. **Create service**: Add business logic in `service/entity_service.py`
4. **Create schemas**: Add Pydantic models in `api/schemas.py`
5. **Create routes**: Add endpoints in `api/routes/entity.py`
6. **Write tests**: Add tests in `tests/test_api/test_entity.py`
7. **Update docs**: Document new endpoints

### Adding a Background Task

1. **Define task**: Add task function in `domain/tasks.py`
2. **Use broker decorator**: `@broker.task`
3. **Enqueue from API**: Call `await my_task.kiq(args)`
4. **Test locally**: Ensure worker is running (`make backend-up` starts worker)

## Monitoring and Debugging

### Logging

- **Level**: Configured via `LOGGING_LEVEL` environment variable
- **Request logging**: Automatic via middleware
- **Format**: Structured logs with timestamps and context

### Error Tracking

- **Sentry**: Enabled via `SENTRY_ENABLED=true`
- **DSN**: Configure `SENTRY_DSN` in environment
- **Auto-capture**: All unhandled exceptions sent to Sentry

### Health Checks

- `GET /api/`: Root health check
- `GET /api/health`: Health status
- `GET /api/ping`: Simple ping endpoint

## Performance Considerations

### Database

- **Connection pooling**: Handled by SQLAlchemy
- **Indexes**: Add indexes to frequently queried columns
- **Eager loading**: Use `selectinload()` to avoid N+1 queries

### Caching

- **Redis**: Available for caching (already configured)
- **Use cases**: Session data, rate limiting, temporary data

### Scaling

- **Horizontal**: Multiple API instances behind load balancer
- **Workers**: Scale worker processes independently
- **Database**: Read replicas for read-heavy workloads
