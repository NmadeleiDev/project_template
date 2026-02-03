"""
API Layer.

This module contains the API endpoints and API schemas for the application.

Structure:
- app.py: FastAPI application.
- base_schema.py: Base Pydantic model for the API.
- schemas.py: Pydantic models for the API.
- dependencies.py: Shared FastAPI dependencies (e.g. get_current_user).
- routes: Directory containing the API routes.

Note: Password hashing, JWT utilities, and custom exceptions are in the service layer.
"""

from api.app import app

__all__ = ["app"]
