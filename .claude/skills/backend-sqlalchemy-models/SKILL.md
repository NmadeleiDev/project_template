---
name: backend-sqlalchemy-models
description: Enforces SQLAlchemy 2.0 Mapped syntax for database models. Use when creating models, defining columns, adding relationships, or generating migrations.
---

# SQLAlchemy Models - New Mapped Syntax

This skill defines how to create database models using SQLAlchemy 2.0 Mapped syntax with proper type annotations.

## When to Use

- When creating new database models
- When adding columns to existing models
- When defining relationships between models
- When working with migrations
- When reviewing model definitions

## Instructions

### Core Principle

**All database models MUST use the new `Mapped[]` type annotation syntax introduced in SQLAlchemy 2.0.**

### Basic Model Structure

All models inherit from `BaseTableModel` which provides:
- `id: UUID` - Primary key
- `created_at: datetime` - Timestamp

```python
from sqlalchemy.orm import Mapped, mapped_column
from repository.base_model import BaseTableModel

class User(BaseTableModel):
    """User account model."""

    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
```

### Column Types

**Required String:**
```python
title: Mapped[str] = mapped_column()
email: Mapped[str] = mapped_column(unique=True, index=True)
```

**Optional Column (Nullable):**
```python
subtitle: Mapped[str | None] = mapped_column(default=None)
bio: Mapped[str | None] = mapped_column(default=None)
```

**Integer:**
```python
age: Mapped[int] = mapped_column()
score: Mapped[int | None] = mapped_column(default=None)
retry_count: Mapped[int] = mapped_column(default=0)
```

**Boolean:**
```python
is_active: Mapped[bool] = mapped_column(default=True)
is_verified: Mapped[bool] = mapped_column(default=False)
```

**DateTime:**
```python
from datetime import datetime

last_login: Mapped[datetime | None] = mapped_column(default=None)
deleted_at: Mapped[datetime | None] = mapped_column(default=None)
```

**UUID (Foreign Keys):**
```python
from uuid import UUID
from sqlalchemy import ForeignKey

author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
reviewer_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id"), default=None)
```

**Text (Large Text):**
```python
from sqlalchemy import Text

content: Mapped[str] = mapped_column(Text)
description: Mapped[str] = mapped_column(Text)
```

**JSON:**
```python
from sqlalchemy import JSON
from typing import Any

metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
settings: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
```

### Relationships

**One-to-Many:**
```python
from sqlalchemy.orm import relationship

class User(BaseTableModel):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(BaseTableModel):
    title: Mapped[str] = mapped_column()
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
```

**Many-to-Many:**
```python
from sqlalchemy import Table, Column, ForeignKey

post_tags = Table(
    "post_tags",
    BaseTableModel.metadata,
    Column("post_id", ForeignKey("post.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Post(BaseTableModel):
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

class Tag(BaseTableModel):
    name: Mapped[str] = mapped_column(unique=True)
    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )
```

### Migration Workflow

After creating or modifying models:

1. **Generate migration**: `make migration MESSAGE="Add BlogPost model"`
2. **Review migration**: Check `repository/migrations/versions/`
3. **Apply migration**: Automatic on backend startup

### Common Mistakes to Avoid

**❌ WRONG: Old SQLAlchemy syntax**
```python
class User(BaseTableModel):
    email = Column(String, unique=True)  # Old style
```

**✅ CORRECT: New mapped syntax**
```python
class User(BaseTableModel):
    email: Mapped[str] = mapped_column(unique=True)
```

**❌ WRONG: Incorrect optional syntax**
```python
from typing import Optional
bio: Mapped[Optional[str]] = mapped_column()  # Use | None
```

**✅ CORRECT: Use | None**
```python
bio: Mapped[str | None] = mapped_column(default=None)
```

### Documentation Requirements

Always add docstrings to models:

```python
class User(BaseTableModel):
    """
    User account model.

    Attributes:
        email: Unique user email (indexed for fast lookup)
        hashed_password: Argon2 hashed password
        is_active: Account active status
        posts: One-to-many relationship with Post model
    """
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")
```

### Checklist

- [ ] Always use `Mapped[]` type annotations
- [ ] Use `| None` for optional columns, never `Optional[]`
- [ ] Include `mapped_column()` for all fields
- [ ] Add indexes to frequently queried columns
- [ ] Document all models with comprehensive docstrings
- [ ] Use relationships for model associations
- [ ] Generate migrations after model changes
