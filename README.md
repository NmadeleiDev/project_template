# Project Template

Full-stack application with a Python/FastAPI backend and Vue 3 frontend.

## Architecture

### Backend (Layered Architecture)

```
backend/
├── api/          # API layer: FastAPI routes, schemas, auth, exceptions
├── service/      # Service layer: intermediary between API and domain
├── domain/       # Domain layer: business logic + Celery task definitions
├── repository/   # Repository layer: SQLAlchemy models, DB operations, Alembic migrations
└── core/         # Core utilities: settings, logging, Sentry
```

**Key principles:**
- Clear separation of concerns between layers
- Dependencies flow inward (API → Service → Domain → Repository)
- Pydantic for API schemas, SQLAlchemy for ORM
- Alembic for database migrations
- Celery for async task processing

### Frontend (Vue 3 + TypeScript)

```
frontend/src/
├── api/          # Axios-based API client with error handling
├── store/        # Vuex state management
├── router/       # Vue Router with auth guards
├── views/        # Page components
├── components/   # Reusable components
└── styles/       # Custom CSS UI library (design tokens, components, utilities)
```

**Key principles:**
- Composition API with TypeScript
- Centralized error handling via Vuex store
- CSS-based design system with CSS variables
- Viewport-locked layout (no body scroll)

## Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend dev)

### Setup

1. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

2. **Add to /etc/hosts:**
   ```
   127.0.0.1 app-local.com
   ```

3. **Start backend services:**
   ```bash
   make backend-up
   ```
   This starts: PostgreSQL, Redis, API server, Celery worker, Flower, and Traefik.

4. **Start frontend (separate terminal):**
   ```bash
   cd frontend
   npm install
   npm run serve
   ```

### Access Points
| Service  | URL                          |
|----------|------------------------------|
| API      | http://app-local.com/api     |
| Flower   | http://app-local.com/flower  |
| Frontend | http://app-local.com:8080    |

## Database Migrations

**Create a new migration:**
```bash
make migration MESSAGE='your migration description'
```

**Migrations run automatically** when starting the backend via `make backend-up`.

