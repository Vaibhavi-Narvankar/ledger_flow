import asyncio
import statistics
import time
import httpx


URL = "http://localhost:8000/api/v1/transactions/transfers"

SENDER_WALLET_ID = 4
RECEIVER_WALLET_ID = 5

CONCURRENCY_LEVELS = [10, 50, 100]


async def send_transfer(
    client: httpx.AsyncClient,
    request_number: int,
) -> tuple[int, float]:
    headers = {
        "Idempotency-Key": f"load-test-{request_number}",
    }

    payload = {
        "sender_wallet_id": SENDER_WALLET_ID,
        "receiver_wallet_id": RECEIVER_WALLET_ID,
        "amount": 1,
    }

    start = time.perf_counter()

    response = await client.post(
        URL,
        json=payload,
        headers=headers,
    )

    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


async def run_load_test(concurrency: int) -> None:
    print(f"\n{'=' * 60}")
    print(f"Concurrency: {concurrency}")
    print(f"{'=' * 60}")

    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        start = time.perf_counter()

        results = await asyncio.gather(
            *[
                send_transfer(client, i)
                for i in range(concurrency)
            ]
        )

        total_time = time.perf_counter() - start

    statuses = [status for status, _ in results]
    latencies = [latency for _, latency in results]

    successful = statuses.count(201)
    conflicts = statuses.count(409)

    print(f"Total requests : {concurrency}")
    print(f"Successful     : {successful}")
    print(f"409 responses  : {conflicts}")
    print(f"Other responses: {concurrency - successful - conflicts}")
    print(f"Total time     : {total_time:.4f}s")

    if latencies:
        print(f"Avg latency    : {statistics.mean(latencies):.4f}s")
        print(f"Min latency    : {min(latencies):.4f}s")
        print(f"Max latency    : {max(latencies):.4f}s")

    if total_time > 0:
        print(
            f"Throughput     : "
            f"{concurrency / total_time:.2f} requests/sec"
        )


async def main() -> None:
    for concurrency in CONCURRENCY_LEVELS:
        await run_load_test(concurrency)


asyncio.run(main())