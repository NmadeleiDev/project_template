---
name: backend-exceptions
description: Centralizes exception definitions with unique error codes in api/exceptions.py. Use when raising errors, creating new exception types, or handling API errors with internal codes.
---

# Backend Exception Handling

This skill defines how to create and use exceptions in the backend with centralized definitions and unique error codes.

## When to Use

- When raising any exception in backend code
- When creating a new exception type
- When documenting error responses
- When frontend needs to parse specific error cases
- When reviewing API error handling

## Instructions

### Core Principle

**All exceptions that the backend raises MUST be defined and documented in `api/exceptions.py`.**

### Exception Hierarchy

```
APIException (base)
├── ClientException (40000-49999)
│   ├── BadRequestException (40000-40099)
│   ├── UnauthorizedException (40100-40199)
│   ├── ForbiddenException (40200-40299)
│   └── NotFoundException (40400-40499)
└── ServerException (50000-59999)
```

### Error Code Ranges

- **40000-40099**: Bad Request (400) - Client errors, invalid input
- **40100-40199**: Unauthorized (401) - Authentication errors
- **40200-40299**: Forbidden (403) - Permission errors
- **40400-40499**: Not Found (404) - Resource not found errors
- **50000-59999**: Server Error (500) - Internal server errors

### Creating New Exceptions

**Step 1: Choose Error Code Range**

Determine the appropriate HTTP status and error code range based on the error type.

**Step 2: Add to api/exceptions.py**

```python
class YourCustomException(BadRequestException):
    """
    Raised when [describe the specific condition].

    Example scenario:
    - User tries to [action] but [condition]
    """

    internal_code = 40002  # Next available code in range
    detail = "User-friendly error message"
```

**Step 3: Use in Code**

```python
from api.exceptions import YourCustomException

async def some_function():
    if invalid_condition:
        raise YourCustomException()

    # Can override default message
    if another_condition:
        raise YourCustomException(detail="Custom message")
```

### Exception Structure Requirements

Every exception must have:
1. **status_code**: HTTP status code
2. **internal_code**: Unique error code for frontend parsing
3. **detail**: Human-readable error message
4. **Docstring**: Description of when this exception is raised

### Document in Route Docstrings

```python
@router.post("/signup")
async def signup(data: SignUpRequest) -> AuthResponse:
    """
    Register new user account.

    Raises:
        UserAlreadyExistsException (40001): Email already registered
        InvalidEmailFormatException (40002): Email format is invalid
    """
    # Implementation...
```

### Frontend Error Handling

Frontend can parse errors using `internal_code`:

```typescript
try {
  await api.post('/auth/signup', data)
} catch (error) {
  if (error.internal_code === 40001) {
    // Handle "User already exists"
  } else if (error.internal_code === 40002) {
    // Handle "Invalid email format"
  }
}
```

### Rules

**DO:**
- Define all exceptions in `api/exceptions.py`
- Use specific exceptions (not generic ones)
- Include comprehensive docstrings
- Document exceptions in route docstrings
- Use internal codes for frontend parsing

**DON'T:**
- Raise generic `Exception` or `ValueError`
- Create exceptions outside `api/exceptions.py`
- Use duplicate internal codes
- Leave exceptions undocumented
- Raise HTTP exceptions directly

### Example Implementation

```python
# In api/exceptions.py
class InvalidEmailFormatException(BadRequestException):
    """
    Raised when email format is invalid.

    Example scenarios:
    - Email missing @ symbol
    - Email missing domain
    - Email contains invalid characters
    """
    internal_code = 40002
    detail = "Invalid email format"

# In service/auth_service.py
import re
from api.exceptions import InvalidEmailFormatException

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

async def signup_user(self, email: str, password: str):
    if not re.match(EMAIL_REGEX, email):
        raise InvalidEmailFormatException()
    # Continue...
```

### Checklist

Before using an exception:
- [ ] Exception is defined in `api/exceptions.py`
- [ ] Has unique `internal_code`
- [ ] Has appropriate `status_code`
- [ ] Has clear `detail` message
- [ ] Has comprehensive docstring
- [ ] Documented in route docstring where used
- [ ] Never raises generic `Exception` or `ValueError`
