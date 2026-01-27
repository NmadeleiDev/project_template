"""
Health check endpoint tests.

Tests for basic health check and ping endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_check(client: AsyncClient):
    """Test root endpoint returns OK."""
    response = await client.get("/api/")
    assert response.status_code == 200
    assert response.json() == "OK"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test /health endpoint returns OK."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == "OK"


@pytest.mark.asyncio
async def test_ping_endpoint(client: AsyncClient):
    """Test /ping endpoint returns pong."""
    response = await client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
