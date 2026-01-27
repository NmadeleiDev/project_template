"""
Service Layer.

This module contains business logic for the application.
Services coordinate between the API layer and repository layer,
implementing business rules and transaction management.

Structure:
- base_service.py: Base service class with common utilities
- auth_service.py: Authentication business logic
- user_service.py: User management business logic
"""

from service.auth_service import AuthService
from service.user_service import UserService

__all__ = ["AuthService", "UserService"]
