from decimal import Decimal

import pytest
from httpx import AsyncClient


async def create_user(
    client: AsyncClient,
    email: str,
) -> int:
    response = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


async def create_wallet(
    client: AsyncClient,
    user_id: int,
) -> int:
    response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": "INR",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


async def deposit(
    client: AsyncClient,
    wallet_id: int,
    amount: str,
    key: str,
):
    return await client.post(
        "/api/v1/transactions/deposits",
        headers={"Idempotency-Key": key},
        json={
            "wallet_id": wallet_id,
            "amount": amount,
        },
    )


@pytest.mark.asyncio
async def test_get_transaction_by_id(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-get@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    create_response = await deposit(
        client,
        wallet_id,
        "500",
        "history-get-001",
    )

    transaction_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/transactions/{transaction_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/transactions/999999999"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_wallet_transaction_history(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-list@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    for index in range(3):
        response = await deposit(
            client,
            wallet_id,
            "100",
            f"history-list-{index}",
        )

        assert response.status_code == 201

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_wallet_transaction_pagination(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-pagination@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    for index in range(5):
        response = await deposit(
            client,
            wallet_id,
            "100",
            f"pagination-{index}",
        )

        assert response.status_code == 201

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "page": 1,
            "page_size": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_wallet_transaction_type_filter(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-filter@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    response = await deposit(
        client,
        wallet_id,
        "500",
        "filter-deposit-001",
    )

    assert response.status_code == 201

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "transaction_type": "DEPOSIT",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert all(
        item["transaction_type"] == "DEPOSIT"
        for item in data["items"]
    )


@pytest.mark.asyncio
async def test_wallet_transaction_status_filter(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-status@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    await deposit(
        client,
        wallet_id,
        "100",
        "status-filter-001",
    )

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "status": "COMPLETED",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_wallet_transaction_currency_filter(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-currency@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    await deposit(
        client,
        wallet_id,
        "100",
        "currency-filter-001",
    )

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "currency": "INR",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["currency"] == "INR"


@pytest.mark.asyncio
async def test_wallet_transaction_invalid_pagination(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "history-invalid-pagination@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "page": 0,
        },
    )

    assert response.status_code == 422

    response = await client.get(
        f"/api/v1/transactions/wallet/{wallet_id}",
        params={
            "page_size": 101,
        },
    )

    assert response.status_code == 422