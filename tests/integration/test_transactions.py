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
    currency: str = "INR",
) -> int:
    response = await client.post(
        "/api/v1/wallets",
        json={
            "user_id": user_id,
            "currency": currency,
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
        headers={
            "Idempotency-Key": key,
        },
        json={
            "wallet_id": wallet_id,
            "amount": amount,
        },
    )


async def transfer(
    client: AsyncClient,
    sender_wallet_id: int,
    receiver_wallet_id: int,
    amount: str,
    key: str,
):
    return await client.post(
        "/api/v1/transactions/transfers",
        headers={
            "Idempotency-Key": key,
        },
        json={
            "sender_wallet_id": sender_wallet_id,
            "receiver_wallet_id": receiver_wallet_id,
            "amount": amount,
        },
    )


@pytest.mark.asyncio
async def test_deposit(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "deposit@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    response = await deposit(
        client,
        wallet_id,
        "500",
        "deposit-test-001",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["receiver_wallet_id"] == wallet_id
    assert Decimal(data["amount"]) == Decimal("500")
    assert data["transaction_type"] == "DEPOSIT"
    assert data["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_deposit_updates_wallet_balance(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "deposit-balance@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    response = await deposit(
        client,
        wallet_id,
        "750",
        "deposit-balance-001",
    )

    assert response.status_code == 201

    wallet_response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert wallet_response.status_code == 200
    assert Decimal(wallet_response.json()["balance"]) == Decimal("750")


@pytest.mark.asyncio
async def test_transfer(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "transfer-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "transfer-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
    )

    await deposit(
        client,
        sender_wallet,
        "1000",
        "transfer-funding-001",
    )

    response = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "300",
        "transfer-test-001",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sender_wallet_id"] == sender_wallet
    assert data["receiver_wallet_id"] == receiver_wallet
    assert Decimal(data["amount"]) == Decimal("300")
    assert data["transaction_type"] == "TRANSFER"
    assert data["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_transfer_updates_both_balances(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "balance-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "balance-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
    )

    await deposit(
        client,
        sender_wallet,
        "1000",
        "balance-funding-001",
    )

    response = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "400",
        "balance-transfer-001",
    )

    assert response.status_code == 201

    sender = await client.get(
        f"/api/v1/wallets/{sender_wallet}"
    )

    receiver = await client.get(
        f"/api/v1/wallets/{receiver_wallet}"
    )

    assert Decimal(sender.json()["balance"]) == Decimal("600")
    assert Decimal(receiver.json()["balance"]) == Decimal("400")


@pytest.mark.asyncio
async def test_transfer_insufficient_balance(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "insufficient-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "insufficient-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
    )

    await deposit(
        client,
        sender_wallet,
        "100",
        "insufficient-funding-001",
    )

    response = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "101",
        "insufficient-transfer-001",
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_transfer_same_wallet(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "same-wallet@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    response = await transfer(
        client,
        wallet_id,
        wallet_id,
        "10",
        "same-wallet-001",
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_transfer_currency_mismatch(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "currency-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "currency-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
        "INR",
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
        "USD",
    )

    await deposit(
        client,
        sender_wallet,
        "1000",
        "currency-funding-001",
    )

    response = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "100",
        "currency-transfer-001",
    )

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_deposit_idempotency(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "deposit-idempotency@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    first = await deposit(
        client,
        wallet_id,
        "500",
        "deposit-idempotency-001",
    )

    second = await deposit(
        client,
        wallet_id,
        "500",
        "deposit-idempotency-001",
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["id"] == second.json()["id"]

    wallet = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert Decimal(wallet.json()["balance"]) == Decimal("500")


@pytest.mark.asyncio
async def test_deposit_idempotency_conflict(
    client: AsyncClient,
) -> None:
    user_id = await create_user(
        client,
        "deposit-idempotency-conflict@test.com",
    )

    wallet_id = await create_wallet(
        client,
        user_id,
    )

    first = await deposit(
        client,
        wallet_id,
        "500",
        "deposit-conflict-001",
    )

    assert first.status_code == 201

    second = await deposit(
        client,
        wallet_id,
        "600",
        "deposit-conflict-001",
    )

    assert second.status_code == 409


@pytest.mark.asyncio
async def test_transfer_idempotency(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "idempotency-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "idempotency-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
    )

    await deposit(
        client,
        sender_wallet,
        "1000",
        "idempotency-funding-001",
    )

    first = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "200",
        "transfer-idempotency-001",
    )

    second = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "200",
        "transfer-idempotency-001",
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["id"] == second.json()["id"]

    sender = await client.get(
        f"/api/v1/wallets/{sender_wallet}"
    )

    receiver = await client.get(
        f"/api/v1/wallets/{receiver_wallet}"
    )

    assert Decimal(sender.json()["balance"]) == Decimal("800")
    assert Decimal(receiver.json()["balance"]) == Decimal("200")


@pytest.mark.asyncio
async def test_transfer_idempotency_conflict(
    client: AsyncClient,
) -> None:
    sender_user = await create_user(
        client,
        "transfer-conflict-sender@test.com",
    )

    receiver_user = await create_user(
        client,
        "transfer-conflict-receiver@test.com",
    )

    sender_wallet = await create_wallet(
        client,
        sender_user,
    )

    receiver_wallet = await create_wallet(
        client,
        receiver_user,
    )

    await deposit(
        client,
        sender_wallet,
        "1000",
        "transfer-conflict-funding-001",
    )

    first = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "200",
        "transfer-conflict-001",
    )

    assert first.status_code == 201

    second = await transfer(
        client,
        sender_wallet,
        receiver_wallet,
        "300",
        "transfer-conflict-001",
    )

    assert second.status_code == 409