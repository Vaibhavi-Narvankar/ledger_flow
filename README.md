# LedgerFlow

LedgerFlow is a backend-focused digital wallet and ledger system built with
FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Docker.

The project is being developed as a production-oriented backend system with
a focus on clean architecture, data integrity, financial correctness,
transaction safety, and eventually high-throughput distributed ledger
processing.

---

## Current Status

### Completed

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
- Foreign key relationship between users and wallets
- Duplicate wallet protection
- Basic wallet retrieval and deletion

### In Progress

- Transaction system
- Ledger entries
- Atomic balance updates
- Concurrency control
- Idempotency
- Transaction history
- High-throughput processing
- Observability and monitoring

---

## Tech Stack

- **Python 3.14**
- **FastAPI**
- **Pydantic**
- **SQLAlchemy 2.x**
- **asyncpg**
- **PostgreSQL**
- **Alembic**
- **Docker**
- **Docker Compose**
- **Pytest**

---

## Architecture

LedgerFlow follows a layered backend architecture:

```text
Client
   │
   ▼
FastAPI Routes
   │
   ▼
Services
   │
   ▼
Repositories
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL