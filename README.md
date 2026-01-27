# Project Template

A production-ready full-stack web application template with modern Vue.js frontend and Python FastAPI backend, featuring user authentication, async task processing, and clean architecture patterns.

## Features

- **🔐 Authentication System**: Complete user signup/signin/signout with JWT tokens
- **⚡ Async-First Backend**: FastAPI with async SQLAlchemy and asyncpg for high performance
- **📦 Background Task Processing**: Taskiq with Redis for async job execution
- **🎨 Modern Frontend**: Vue 3 with TypeScript, Vuex state management, and Vue Router
- **🗄️ Database Management**: PostgreSQL with Alembic migrations
- **🐳 Docker Ready**: Full containerization with Docker Compose
- **🔍 Production Monitoring**: Sentry integration for error tracking
- **🏗️ Clean Architecture**: Layered backend structure (API → Service → Domain → Repository)
- **🔒 Security**: Argon2 password hashing, HTTP-only cookies, input validation

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 18 with SQLAlchemy 2.0 (async)
- **Cache/Queue**: Redis 8 with Taskiq
- **Migrations**: Alembic
- **Authentication**: JWT with python-jose, Argon2 password hashing
- **Monitoring**: Sentry SDK
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **State Management**: Vuex
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Build Tool**: Vue CLI 5

### DevOps
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Traefik v3
- **Development**: Hot reload for both frontend and backend

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd project_template

# Create backend environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

### 2. Start Backend Services

```bash
# Start all backend services (API, PostgreSQL, Redis, Worker)
make backend-up

# Services will be available at:
# - API: http://app-local.com/api (via Traefik)
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

**Note**: Add `127.0.0.1 app-local.com` to your `/etc/hosts` file for local development.

### 3. Start Frontend (in separate terminal)

```bash
cd frontend
npm install
npm run serve

# Frontend will be available at http://localhost:8080
```

### 4. Access the Application

- Frontend: http://localhost:8080
- Backend API: http://app-local.com/api
- API Documentation: http://app-local.com/api/docs (Swagger UI)

## Project Structure

```
project_template/
├── backend/                    # Python FastAPI backend
│   ├── api/                   # HTTP layer (routes, schemas, exceptions)
│   │   ├── routes/           # API endpoints
│   │   ├── app.py            # FastAPI application
│   │   ├── schemas.py        # Pydantic request/response models
│   │   ├── exceptions.py     # Custom API exceptions
│   │   ├── dependencies.py   # FastAPI dependencies (auth, DB session)
│   │   └── security.py       # Password hashing, JWT utilities
│   ├── service/              # Business logic layer
│   ├── domain/               # Domain models and task queue
│   │   └── taskiq_broker.py  # Async task queue configuration
│   ├── repository/           # Data access layer
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── base_model.py     # Base model with common fields
│   │   └── migrations/       # Alembic database migrations
│   ├── core/                 # Core configuration
│   │   ├── settings.py       # Application settings
│   │   └── db.py             # Database session management
│   └── main.py               # CLI entry point
├── frontend/                  # Vue.js 3 frontend
│   ├── src/
│   │   ├── api/              # API client configuration
│   │   ├── components/       # Reusable Vue components
│   │   ├── router/           # Vue Router setup
│   │   ├── store/            # Vuex state management
│   │   ├── views/            # Page components
│   │   └── main.ts           # Application entry point
│   └── public/               # Static assets
├── docs/                      # Documentation
├── docker-compose.yaml        # Multi-service orchestration
└── Makefile                   # Development shortcuts
```

## Development

### Backend Commands

```bash
# Start backend with hot reload
make backend-up

# Create database migration
make migration MESSAGE="Add user table"

# Run backend locally (without Docker)
cd backend
python main.py serve --reload

# Start async worker
python main.py worker

# Run database migrations
python main.py upgrade-database

# Create migration
python main.py generate-migration -m "description"
```

### Frontend Commands

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run serve

# Build for production
npm run build

# Lint and fix
npm run lint
```

### Available Make Commands

```bash
make help           # Show all available commands
make backend-up     # Start backend services
make migration      # Create new database migration
```

## Architecture

This template follows a **layered architecture** pattern for maintainability and scalability:

### Backend Layers

1. **API Layer** (`api/`): HTTP interface
   - FastAPI routes and endpoints
   - Request/response validation with Pydantic
   - Authentication dependencies
   - Custom exception handlers

2. **Service Layer** (`service/`): Business logic
   - Coordinates between API and repository layers
   - Implements business rules
   - Transaction management

3. **Domain Layer** (`domain/`): Core business entities
   - Domain models and value objects
   - Async task queue configuration
   - Business logic that doesn't fit in services

4. **Repository Layer** (`repository/`): Data persistence
   - SQLAlchemy models (new mapped syntax)
   - Database migrations (Alembic)
   - Data access patterns

5. **Core Layer** (`core/`): Cross-cutting concerns
   - Configuration management
   - Database session handling
   - Logging and monitoring

### Key Design Principles

- **Async-First**: All I/O operations are async to prevent blocking
- **Long-Running Tasks**: Executed via Taskiq in separate worker process
- **Type Safety**: Full type hints in Python, TypeScript in frontend
- **Clean Separation**: Each layer has single responsibility
- **Error Handling**: Standardized exceptions with internal error codes

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Authentication Flow

1. **Signup**: POST `/api/auth/signup`
   - User provides email and password
   - Password is hashed with Argon2
   - User record created in database
   - JWT token returned in HTTP-only cookie

2. **Signin**: POST `/api/auth/signin`
   - User provides credentials
   - Credentials validated
   - JWT token returned in HTTP-only cookie

3. **Protected Routes**: Require valid JWT token
   - Token extracted from cookie
   - Token validated and decoded
   - User loaded from database
   - User object injected into route handler

4. **Signout**: POST `/api/auth/signout`
   - JWT cookie cleared

## Database Migrations

This template uses Alembic for database version control.

```bash
# Create a new migration
make migration MESSAGE="Add user profile table"

# Apply migrations manually
cd backend
python main.py upgrade-database

# Rollback last migration
python main.py downgrade
```

Migrations are automatically applied on backend startup in Docker.

## Environment Variables

See `backend/.env.example` for all available configuration options.

**Critical variables to change in production:**
- `JWT_SECRET_KEY`: Use a strong random string
- `POSTGRES_PASSWORD`: Use a strong password
- `SENTRY_DSN`: Add your Sentry project DSN
- `HTTPS_ENABLED`: Set to `true`

## Testing

```bash
# Run backend tests (when implemented)
cd backend
pytest

# Run frontend tests (when implemented)
cd frontend
npm test
```

## Production Deployment

1. Update environment variables for production
2. Set `HTTPS_ENABLED=true`
3. Configure proper secret keys
4. Set up SSL certificates (Let's Encrypt recommended)
5. Use production WSGI server (Gunicorn/Uvicorn workers)
6. Enable Sentry monitoring
7. Set up database backups
8. Configure CDN for frontend static assets

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://app-local.com/api/docs
- ReDoc: http://app-local.com/api/redoc

## Contributing

1. Follow the existing code structure and conventions
2. Add tests for new features
3. Update documentation as needed
4. Use type hints in Python code
5. Follow async/await patterns

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check existing documentation in `docs/`
2. Review API documentation at `/api/docs`
3. Open an issue in the repository
