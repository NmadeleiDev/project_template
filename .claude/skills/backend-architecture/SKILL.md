---
name: backend-architecture
description: Defines backend architecture with layered approach (API, Service, Domain, Repository, Core). Use when implementing backend features, creating new endpoints, or understanding the project structure.
---

# Backend Architecture

This skill provides an overview of the backend architecture and conventions for implementing backend code.

## When to Use

- When implementing any backend feature
- When creating new API endpoints
- When adding business logic
- When working with database models
- When understanding project structure
- When adding background tasks

## Instructions

### Architecture Layers

The backend follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│          API Layer (api/)               │  ← HTTP interface, routes
├─────────────────────────────────────────┤
│       Service Layer (service/)          │  ← Business logic
├─────────────────────────────────────────┤
│        Domain Layer (domain/)           │  ← Core entities, tasks
├─────────────────────────────────────────┤
│     Repository Layer (repository/)      │  ← Data access, models
├─────────────────────────────────────────┤
│         Core Layer (core/)              │  ← Configuration, DB
└─────────────────────────────────────────┘
```

### Layer Responsibilities

**1. API Layer (`api/`)**
- HTTP interface and request/response handling
- Contains: routes/, schemas.py, exceptions.py, dependencies.py
- Must be 100% async (see backend-async-conventions skill)
- Thin layer - just coordinate requests
- Delegate business logic to service layer
- No direct database access

**2. Service Layer (`service/`)**
- Business logic and transaction coordination
- Contains: base_service.py, auth_service.py, user_service.py, security.py
- All methods must be async
- Contains business rules and validation
- Reusable from API routes and background tasks
- No HTTP concerns (no Request/Response objects)

**3. Domain Layer (`domain/`)**
- Core business entities and background tasks
- Contains: taskiq_broker.py, tasks.py
- Long-running operations go here
- CPU-intensive operations go here
- External API calls, email sending, PDF generation

**4. Repository Layer (`repository/`)**
- Data persistence and database operations
- Contains: models.py, base_model.py, connection.py, migrations/
- Use async SQLAlchemy session
- Use new `Mapped[]` syntax (see backend-sqlalchemy-models skill)
- No business logic

**5. Core Layer (`core/`)**
- Cross-cutting concerns and configuration
- Contains: settings.py, db.py
- Shared utilities across layers
- All config from environment variables

### Adding a New Feature

1. **Define model** (if needed) in `repository/models.py`
2. **Create migration**: `make migration MESSAGE="Add model"`
3. **Define schemas** in `api/schemas.py`
4. **Implement service** in `service/`
5. **Create route** in `api/routes/`
6. **Write tests** in `tests/`

### Key Design Principles

- **Async-First**: API layer must NEVER block async loop (see backend-async-conventions skill)
- **Type Safety**: Full type hints on all functions
- **Exception Handling**: All exceptions in `api/exceptions.py` (see backend-exceptions skill)
- **Clean Separation**: Each layer has single responsibility

### Related Skills

- `backend-async-conventions` - Async/blocking rules (CRITICAL)
- `backend-sqlalchemy-models` - Database model syntax
- `backend-exceptions` - Exception handling (CRITICAL)

For detailed architecture documentation, see `docs/ARCHITECTURE.md`.
