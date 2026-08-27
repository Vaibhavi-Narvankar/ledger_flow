from httpx import ASGITransport, AsyncClient

import pytest

from app.main import app


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/users",
            json={"email": "test@example.com"},
        )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
