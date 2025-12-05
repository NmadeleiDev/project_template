"""
API Layer.

This module contains the API endpoints, API schemas and API exceptions for the application.

Structure:
- app.py: FastAPI application.
- base_schema.py: Base Pydantic model for the API.
- schemas.py: Pydantic models for the API.
- exceptions.py: Custom exceptions for the API.
- dependencies.py: Shared FastAPI dependencies (e.g. get_current_user).
- routes: Directory containing the API routes.
- security.py: Password hashing and JWT utilities for authentication.
"""

from api.app import app

__all__ = ["app"]
