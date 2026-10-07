import asyncio
from decimal import Decimal
from uuid import uuid4
import httpx
import pytest


API_1 = "http://api-1:8000"
API_2 = "http://api-2:8000"


@pytest.mark.asyncio
async def test_concurrent_transfer_idempotency_across_instances() -> None:
    async with httpx.AsyncClient() as client:
        # Create sender through API-1
        sender_user = await client.post(
            f"{API_1}/api/v1/users",
            json={
                "email": f"distributed-sender-{uuid4()}@test.com",
                "password": "Password123!",
            },
        )
        assert sender_user.status_code == 201

        sender_wallet = await client.post(
            f"{API_1}/api/v1/wallets",
            json={
                "user_id": sender_user.json()["id"],
                "currency": "INR",
            },
        )
        assert sender_wallet.status_code == 201

        sender_wallet_id = sender_wallet.json()["id"]

        # Create receiver through API-2
        receiver_user = await client.post(
            f"{API_2}/api/v1/users",
            json={
                "email": f"distributed-receiver-{uuid4()}@test.com",
                "password": "Password123!",
            },
        )
        assert receiver_user.status_code == 201

        receiver_wallet = await client.post(
            f"{API_2}/api/v1/wallets",
            json={
                "user_id": receiver_user.json()["id"],
                "currency": "INR",
            },
        )
        assert receiver_wallet.status_code == 201

        receiver_wallet_id = receiver_wallet.json()["id"]

        # Fund sender
        funding = await client.post(
            f"{API_1}/api/v1/transactions/deposits",
            headers={
                "Idempotency-Key": f"distributed-test-funding-{uuid4()}",
            },
            json={
                "wallet_id": sender_wallet_id,
                "amount": "1000",
            },
        )

        assert funding.status_code == 201

        payload = {
            "sender_wallet_id": sender_wallet_id,
            "receiver_wallet_id": receiver_wallet_id,
            "amount": "100",
        }

        headers = {
            "Idempotency-Key": f"distributed-concurrent-test-{uuid4()}",
        }

        # Same request hits both API instances concurrently
        response_1, response_2 = await asyncio.gather(
            client.post(
                f"{API_1}/api/v1/transactions/transfers",
                json=payload,
                headers=headers,
            ),
            client.post(
                f"{API_2}/api/v1/transactions/transfers",
                json=payload,
                headers=headers,
            ),
        )

        # Exactly one request must create the transaction.
        status_codes = sorted(
            [response_1.status_code, response_2.status_code]
        )

        assert status_codes == [201, 409]

        # Verify money moved exactly once.
        sender = await client.get(
            f"{API_1}/api/v1/wallets/{sender_wallet_id}"
        )

        receiver = await client.get(
            f"{API_2}/api/v1/wallets/{receiver_wallet_id}"
        )

        assert sender.status_code == 200
        assert receiver.status_code == 200

        assert Decimal(sender.json()["balance"]) == Decimal("900")
        assert Decimal(receiver.json()["balance"]) == Decimal("100")