"""
API Exceptions.

This module defines all exceptions used in the API layer.

Exception Hierarchy:
    APIException (base)
    ├── ClientException (40000-49999)
    │   ├── BadRequestException (40000-40099)
    │   ├── UnauthorizedException (40100-40199)
    │   ├── ForbiddenException (40200-40299)
    │   └── NotFoundException (40400-40499)
    └── ServerException (50000-59999)

Error Code Ranges:
    40000-40099: Bad Request (400) - Invalid input, validation errors
    40100-40199: Unauthorized (401) - Authentication errors
    40200-40299: Forbidden (403) - Permission/authorization errors
    40400-40499: Not Found (404) - Resource not found errors
    50000-59999: Server Error (500) - Internal server errors

Usage:
    All exceptions must be defined in this file. To create a new exception:

    1. Choose appropriate error code range based on HTTP status
    2. Inherit from the appropriate base exception
    3. Set unique internal_code
    4. Provide clear detail message
    5. Add comprehensive docstring

    Example:
        class CustomException(BadRequestException):
            '''Raised when [condition].'''
            internal_code = 40002
            detail = "User-friendly error message"

Notes:
    - Each exception must have a unique internal_code
    - Frontend uses internal_code to parse and display errors
    - Never raise generic Exception or ValueError in API code
    - All API exceptions are automatically caught and formatted by FastAPI
"""

from fastapi import status


class APIException(Exception):
    """
    Base exception for all API exceptions.

    All custom API exceptions must inherit from this class.
    Provides structure for HTTP status codes, internal error codes,
    and human-readable error messages.

    Attributes:
        status_code: HTTP status code (e.g., 400, 401, 404, 500)
        internal_code: Unique error code for frontend parsing
        detail: Human-readable error message

    Example:
        try:
            raise UserAlreadyExistsException()
        except APIException as e:
            print(f"Error {e.internal_code}: {e.detail}")
    """

    status_code: int
    internal_code: int
    detail: str

    def __init__(self, detail: str | None = None):
        """
        Initialize exception.

        Args:
            detail: Optional custom error message to override default
        """
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


# =============================================================================
# CLIENT EXCEPTIONS (40000-49999)
# =============================================================================


class ClientException(APIException):
    """
    Base exception for all client errors (4xx status codes).

    Client errors indicate that the request was invalid or cannot be fulfilled
    due to client-side issues (invalid input, authentication, permissions, etc.).

    Status code range: 400-499
    Internal code range: 40000-49999
    """

    pass


# =============================================================================
# BAD REQUEST EXCEPTIONS (40000-40099)
# HTTP 400 - Invalid input, validation errors, malformed requests
# =============================================================================


class BadRequestException(ClientException):
    """
    Base exception for bad request errors.

    Used when the request is syntactically correct but semantically invalid,
    such as validation errors, malformed data, or business rule violations.

    HTTP Status: 400
    Internal code range: 40000-40099
    """

    status_code = status.HTTP_400_BAD_REQUEST
    internal_code = 40000
    detail = "Bad request"


class UserAlreadyExistsException(BadRequestException):
    """
    Raised when attempting to create a user with an email that already exists.

    This exception is thrown during user registration when the provided
    email address is already registered in the system.

    Example scenarios:
    - User tries to sign up with email that's already registered
    - Admin tries to create user account with duplicate email

    HTTP Status: 400
    Internal code: 40001

    Frontend handling:
    - Display: "This email is already registered"
    - Suggest: "Try logging in instead" or "Use a different email"
    """

    internal_code = 40001
    detail = "User with this email already exists"


# =============================================================================
# UNAUTHORIZED EXCEPTIONS (40100-40199)
# HTTP 401 - Authentication errors, invalid credentials, missing/invalid tokens
# =============================================================================


class UnauthorizedException(ClientException):
    """
    Base exception for authentication errors.

    Used when authentication is required but was not provided or is invalid.
    Indicates the user needs to authenticate (login) to access the resource.

    HTTP Status: 401
    Internal code range: 40100-40199

    Note: 401 means "unauthenticated" (not logged in), not "unauthorized" (lacking permission).
    For permission errors, use ForbiddenException (403).
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    internal_code = 40100
    detail = "Unauthorized"


class InvalidCredentialsException(UnauthorizedException):
    """
    Raised when user provides incorrect email or password during login.

    This exception is thrown during signin when the provided credentials
    don't match any user in the database, or when the password is incorrect.

    Example scenarios:
    - User enters wrong password
    - User enters email that doesn't exist
    - User enters correct email but wrong password

    HTTP Status: 401
    Internal code: 40101

    Security note:
    - Don't reveal whether email or password was wrong (prevents user enumeration)
    - Use generic message: "Invalid email or password"

    Frontend handling:
    - Display: "Invalid email or password"
    - Suggest: "Check your credentials and try again"
    - Offer: "Forgot password?" link
    """

    internal_code = 40101
    detail = "Invalid email or password"


class NotAuthenticatedException(UnauthorizedException):
    """
    Raised when user attempts to access protected resource without authentication.

    This exception is thrown when a user tries to access an endpoint that
    requires authentication but no JWT token was provided in the request.

    Example scenarios:
    - User accesses /api/user/me without being logged in
    - JWT cookie is missing from request
    - User's session has been cleared

    HTTP Status: 401
    Internal code: 40102

    Frontend handling:
    - Redirect to login page
    - Display: "Please log in to continue"
    - Save attempted URL to redirect back after login
    """

    internal_code = 40102
    detail = "Not authenticated"


class InvalidTokenException(UnauthorizedException):
    """
    Raised when JWT token is present but invalid or malformed.

    This exception is thrown when the JWT token cannot be decoded or
    validated, typically due to tampering, corruption, or format issues.

    Example scenarios:
    - JWT token has been tampered with
    - JWT signature is invalid
    - JWT format is malformed
    - JWT secret key has changed (invalidating old tokens)

    HTTP Status: 401
    Internal code: 40103

    Frontend handling:
    - Clear stored authentication state
    - Redirect to login page
    - Display: "Your session is invalid. Please log in again."
    """

    internal_code = 40103
    detail = "Invalid token"


class TokenExpiredException(UnauthorizedException):
    """
    Raised when JWT token has expired.

    This exception is thrown when a valid JWT token is provided but
    its expiration time has passed.

    Example scenarios:
    - User's session has timed out (default: 7 days)
    - JWT access token has exceeded JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    HTTP Status: 401
    Internal code: 40104

    Configuration:
    - Expiration time set via JWT_ACCESS_TOKEN_EXPIRE_MINUTES in .env
    - Default: 10080 minutes (7 days)

    Frontend handling:
    - Clear stored authentication state
    - Redirect to login page
    - Display: "Your session has expired. Please log in again."
    - Optionally implement refresh token flow
    """

    internal_code = 40104
    detail = "Token has expired"


class UserNotFoundException(UnauthorizedException):
    """
    Raised when JWT token is valid but user no longer exists.

    This exception is thrown when a JWT token contains a user ID
    that doesn't exist in the database (user was deleted after token issuance).

    Example scenarios:
    - User account deleted while token still valid
    - Database reset but tokens still in circulation
    - User ID in token doesn't match any user

    HTTP Status: 401
    Internal code: 40105

    Frontend handling:
    - Clear stored authentication state
    - Redirect to login page
    - Display: "Account not found. Please log in again."

    Backend note:
    - This is an edge case that shouldn't happen often
    - Consider logging this event for security monitoring
    """

    internal_code = 40105
    detail = "User not found"


# =============================================================================
# FORBIDDEN EXCEPTIONS (40200-40299)
# HTTP 403 - Permission errors, insufficient privileges
# =============================================================================


class ForbiddenException(ClientException):
    """
    Base exception for permission/authorization errors.

    Used when user is authenticated but doesn't have permission to access
    the requested resource or perform the requested action.

    HTTP Status: 403
    Internal code range: 40200-40299

    Note: 403 means "unauthorized" (lacking permission), not "unauthenticated".
    For authentication errors, use UnauthorizedException (401).

    Example usage:
        class InsufficientPermissionsException(ForbiddenException):
            '''Raised when user lacks required role.'''
            internal_code = 40201
            detail = "Insufficient permissions"
    """

    status_code = status.HTTP_403_FORBIDDEN
    internal_code = 40200
    detail = "Forbidden"


# Add specific 403 exceptions here as needed


# =============================================================================
# NOT FOUND EXCEPTIONS (40400-40499)
# HTTP 404 - Resource not found errors
# =============================================================================


class NotFoundException(ClientException):
    """
    Base exception for resource not found errors.

    Used when a requested resource (user, post, etc.) doesn't exist.

    HTTP Status: 404
    Internal code range: 40400-40499

    Example usage:
        class PostNotFoundException(NotFoundException):
            '''Raised when post is not found.'''
            internal_code = 40401
            detail = "Post not found"
    """

    status_code = status.HTTP_404_NOT_FOUND
    internal_code = 40400
    detail = "Not found"


# Add specific 404 exceptions here as needed


# =============================================================================
# SERVER EXCEPTIONS (50000-59999)
# HTTP 500 - Internal server errors
# =============================================================================


class ServerException(APIException):
    """
    Base exception for server errors.

    Used for unexpected errors that occur on the server side,
    such as database connection failures, external service errors, etc.

    HTTP Status: 500
    Internal code range: 50000-59999

    Note: These should be rare. Most errors should be client exceptions (4xx).

    Example usage:
        class DatabaseConnectionException(ServerException):
            '''Raised when database connection fails.'''
            internal_code = 50001
            detail = "Database connection error"
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    internal_code = 50000
    detail = "Internal server error"


# Add specific 500 exceptions here as needed


# =============================================================================
# EXCEPTION SUMMARY
# =============================================================================

"""
Current Exception Registry:

BAD REQUEST (400) - 40000-40099:
  40000: BadRequestException - Generic bad request
  40001: UserAlreadyExistsException - Email already registered

UNAUTHORIZED (401) - 40100-40199:
  40100: UnauthorizedException - Generic unauthorized
  40101: InvalidCredentialsException - Wrong email/password
  40102: NotAuthenticatedException - No JWT token provided
  40103: InvalidTokenException - JWT token invalid/malformed
  40104: TokenExpiredException - JWT token expired
  40105: UserNotFoundException - User from token not found

FORBIDDEN (403) - 40200-40299:
  40200: ForbiddenException - Generic forbidden
  (Add specific exceptions here)

NOT FOUND (404) - 40400-40499:
  40400: NotFoundException - Generic not found
  (Add specific exceptions here)

SERVER ERROR (500) - 50000-59999:
  50000: ServerException - Generic server error
  (Add specific exceptions here)

To add a new exception:
  1. Choose appropriate HTTP status code and range
  2. Find next available internal_code in range
  3. Create exception class inheriting from base
  4. Add comprehensive docstring
  5. Update this summary

Example:
  class InvalidEmailFormatException(BadRequestException):
      '''Raised when email format is invalid.'''
      internal_code = 40002
      detail = "Invalid email format"
"""
