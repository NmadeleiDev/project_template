---
name: backend-async-conventions
description: Enforces async/await patterns in API layer. Use when implementing API routes, ensuring no blocking operations occur, or moving long-running tasks to background workers.
---

# Backend Async Conventions

This skill defines critical async conventions that MUST be followed for ALL backend API layer code.

## When to Use

- When implementing any API route handler
- When adding database queries
- When making external API calls
- When processing files or images
- When sending emails
- When performing CPU-intensive operations
- When reviewing code for blocking operations

## Instructions

### Core Principle

**The API layer (`api/` directory) must be 100% async and NEVER contain code that could block the async event loop during request processing.**

### Allowed in API Layer

**Async I/O Operations** (correct patterns):
```python
# Database queries
await db.execute(select(User))
await db.commit()

# HTTP requests
await http_client.get(url)

# Redis operations
await redis.get(key)
```

**Fast CPU Operations** (< 1ms):
```python
# Password hashing (runs in thread pool via passlib)
hashed = get_password_hash(password)

# JWT operations (fast)
token = create_access_token(data)

# Pydantic validation (fast)
user_data = UserSchema(**data)
```

### Forbidden in API Layer

**Long-Running Operations** (> 100ms):
- Image/video processing
- PDF generation
- Large file operations
- Complex calculations

**External API Calls** (unpredictable timing):
- Third-party APIs that might be slow
- SMS/notification services

**Email Sending**:
- Takes 2-3 seconds per email

### Solution: Background Tasks

For ANY operation that:
- Takes > 100ms
- Has unpredictable timing
- Is CPU-intensive
- Involves external services

**Move it to the domain layer and execute via Taskiq tasks.**

**Correct Pattern:**

```python
# ✅ API route (fast response)
@router.post("/generate-report")
async def generate_report(user_id: str):
    await generate_report_task.kiq(user_id)
    return {"message": "Report generation started"}

# ✅ Domain task (can be slow)
# File: domain/tasks.py
@broker.task
async def generate_report_task(user_id: str):
    # Long-running operation runs in separate worker
    report_data = await fetch_report_data(user_id)
    pdf = generate_pdf(report_data)
    await store_report(user_id, pdf)
```

### Implementation Checklist

Before committing code, verify:
- [ ] All route handlers are `async def`
- [ ] All I/O uses `await`
- [ ] No synchronous file operations
- [ ] No long-running operations (> 100ms)
- [ ] No external API calls that might be slow
- [ ] No email sending (use background tasks)
- [ ] No image/video processing (use background tasks)
- [ ] No PDF generation (use background tasks)
- [ ] All CPU-intensive work moved to `domain/tasks.py`

### Why This Matters

Blocking the async loop causes:
- All requests to wait (not just the blocking one)
- Timeouts for other clients
- Poor scalability
- Degraded performance under load

### Quick Test

Before committing, ask:
1. "Could this operation take > 100ms?"
2. "Does this involve external services?"
3. "Is this CPU-intensive?"

If YES to any: Move to `domain/tasks.py` and use `@broker.task`.
