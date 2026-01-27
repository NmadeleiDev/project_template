"""
Base service class with common utilities.

Provides shared functionality for all service classes.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Base service class.

    All service classes should inherit from this base to maintain
    consistent patterns and access to database session.

    Attributes:
        db: Async database session for data access
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize base service.

        Args:
            db: Async database session
        """
        self.db = db
