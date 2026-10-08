# LedgerFlow

LedgerFlow is a backend-focused digital wallet and distributed ledger system
built with FastAPI, PostgreSQL, SQLAlchemy, Redis, and Docker.

The project is being developed as a production-oriented backend system with a
focus on financial correctness, transaction safety, concurrency control,
idempotency, distributed coordination, and failure handling.

---

## Current Status

### Completed

#### Core Backend

- FastAPI application setup
- Dockerized development environment
- PostgreSQL integration
- Async SQLAlchemy
- Database health check
- Alembic migrations
- User model and API
- Wallet model and API
- Repository layer
- Service layer
- API exception handling
- Wallet uniqueness constraints
- Wallet currency validation
- Foreign key relationships
- Duplicate wallet protection
- Wallet retrieval and deletion

#### Transaction & Ledger System

- Deposit transactions
- Wallet-to-wallet transfers
- Atomic balance updates
- Ledger debit and credit entries
- Transaction status handling
- Transaction history
- Insufficient balance protection
- Same-wallet transfer protection
- Currency mismatch protection
- PostgreSQL row-level locking
- Deterministic wallet locking order
- Transaction rollback handling

#### Idempotency

- Idempotency keys for financial operations
- PostgreSQL idempotency constraints
- Redis-based distributed idempotency
- Duplicate request protection
- Cross-instance idempotency testing
- Concurrent duplicate request handling

#### Distributed Architecture

- Multiple FastAPI API instances
- Nginx load balancing
- Shared PostgreSQL state
- Shared Redis state
- Cross-instance transaction processing
- API instance failure testing
- API instance recovery testing
- PostgreSQL failure handling
- PostgreSQL recovery testing
- Redis failure handling

#### Testing

- Unit tests
- Integration tests
- Distributed integration tests
- Concurrent transaction tests
- Failure and recovery tests
- Idempotency tests
- Balance consistency tests

Current test suite:

```text
44 passed

## Architecture

```text

                    ┌─────────────┐

                    │   Client    │

                    └──────┬──────┘

                           │

                           ▼

                    ┌─────────────┐

                    │    Nginx    │

                    │ Load Balancer│

                    └──────┬──────┘

                           │

                  ┌────────┴────────┐

                  ▼                 ▼

             ┌─────────┐       ┌─────────┐

             │  API-1  │       │  API-2  │

             │ FastAPI │       │ FastAPI │

             └────┬────┘       └────┬────┘

                  │                 │

                  └────────┬────────┘

                           │

                ┌──────────┴──────────┐

                ▼                     ▼

          ┌───────────┐         ┌───────────┐

          │ PostgreSQL│         │   Redis   │

          │ Source of │         │Idempotency│

          │   Truth   │         │           │

          └───────────┘         └───────────┘


#####Key Engineering Features

* Async FastAPI + SQLAlchemy architecture
* PostgreSQL transactional wallet transfers
* Row-level locking for concurrent transactions
* Deterministic wallet locking to reduce deadlocks
* Redis-based distributed idempotency
* Database-level uniqueness constraints
* Nginx load balancing across multiple API instances
* Centralized database and Redis failure handling
* API instance failure and recovery handling
* Atomic balance and ledger updates


######Concurrency & Distributed Systems
LedgerFlow has been tested across multiple API instances.
50 concurrent transfers × ₹100

####Performance
Local Docker benchmark:

200 concurrent requests
~778 requests/second
100% success rate
0 concurrency conflicts

#####Tech Stack

Backend: Python, FastAPI, Pydantic, SQLAlchemy, asyncpg
Database: PostgreSQL, Alembic
Distributed: Redis, Nginx
Infrastructure: Docker, Docker Compose
Testing: Pytest, pytest-asyncio, HTTPX

####Roadmap

* Event-driven architecture
* Transactional outbox
* Message broker
* Idempotent event consumers
* Security hardening
* Extended load testing
* Production-readiness improvements

####Engineering Focus

LedgerFlow is a practical exploration of:

Transactions · Concurrency · Idempotency · Distributed Systems ·
Failure Handling · Financial Consistency · High-Throughput Backend Design