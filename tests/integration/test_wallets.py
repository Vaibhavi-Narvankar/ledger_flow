import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_wallet(client: AsyncClient) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-create@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201

    user_id = user_response.json()["id"]

    response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": "INR",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user_id
    assert data["currency"] == "INR"
    assert data["balance"] == "0E-8" or data["balance"] == "0.00000000"


@pytest.mark.asyncio
async def test_create_wallet_duplicate(
    client: AsyncClient,
) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-duplicate@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    payload = {
        "user_id": user_id,
        "currency": "INR",
    }

    first = await client.post("/api/v1/wallets", json=payload)
    second = await client.post("/api/v1/wallets", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_create_wallet_nonexistent_user(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": 999999999,
            "currency": "INR",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_wallet_unsupported_currency(
    client: AsyncClient,
) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-currency@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201

    user_id = user_response.json()["id"]

    response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": "XYZ",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_wallet(client: AsyncClient) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-get@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    create_response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": "INR",
        },
    )

    assert create_response.status_code == 201
    wallet_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == wallet_id


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/wallets/999999999"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_wallets(
    client: AsyncClient,
) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-list@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    for currency in ("INR", "USD"):
        response = await client.post(
            "/api/v1/wallets",
            json={
                "user_id": user_id,
                "currency": currency,
            },
        )

        assert response.status_code == 201

    response = await client.get(
        f"/api/v1/wallets/user/{user_id}"
    )

    assert response.status_code == 200

    wallets = response.json()

    assert len(wallets) == 2
    assert {wallet["currency"] for wallet in wallets} == {"INR", "USD"}


@pytest.mark.asyncio
async def test_delete_wallet(
    client: AsyncClient,
) -> None:
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "wallet-delete@test.com",
            "password": "Password123!",
        },
    )

    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    create_response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": "INR",
        },
    )

    assert create_response.status_code == 201
    wallet_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert get_response.status_code == 404