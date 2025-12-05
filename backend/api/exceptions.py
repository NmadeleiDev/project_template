from fastapi import status


class APIException(Exception):
    """Base exception class for API exceptions"""

    status_code: int
    internal_code: int
    detail: str

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


# 40000 - 40099
class ClientException(APIException):
    pass


# 40000 - 40099
class BadRequestException(ClientException):
    status_code = status.HTTP_400_BAD_REQUEST
    internal_code = 40000
    detail = "Bad request"


class UserAlreadyExistsException(BadRequestException):
    """Raised when trying to create a user that already exists"""

    internal_code = 40001
    detail = "User with this email already exists"


# 40100 - 40199
class UnauthorizedException(ClientException):
    status_code = status.HTTP_401_UNAUTHORIZED
    internal_code = 40100
    detail = "Unauthorized"


class InvalidCredentialsException(UnauthorizedException):
    """Raised when email or password is invalid"""

    internal_code = 40101
    detail = "Invalid email or password"


class NotAuthenticatedException(UnauthorizedException):
    """Raised when user is not authenticated"""

    internal_code = 40102
    detail = "Not authenticated"


class InvalidTokenException(UnauthorizedException):
    """Raised when token is invalid"""

    internal_code = 40103
    detail = "Invalid token"


class TokenExpiredException(UnauthorizedException):
    """Raised when token has expired"""

    internal_code = 40104
    detail = "Token has expired"


class UserNotFoundException(UnauthorizedException):
    """Raised when user is not found"""

    internal_code = 40105
    detail = "User not found"


# 50000 - 59999
class ServerException(APIException):
    pass
