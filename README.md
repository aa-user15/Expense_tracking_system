# Expense Tracker API

A lightweight FastAPI service for recording and managing personal expense transactions. The application exposes CRUD endpoints for transactions, includes basic duplicate prevention, and uses a service layer to keep the business logic separate from the HTTP layer.

## Overview

This project demonstrates a small but realistic microservice structure with:

- FastAPI for HTTP APIs and OpenAPI documentation
- SQLAlchemy ORM with SQLite persistence
- A dedicated service layer for business logic
- pytest-based regression and integration tests

## Features

- Create, list, retrieve, and delete expense transactions
- Validate incoming payloads with Pydantic
- Reject obvious duplicate transactions
- Paginate transaction lists
- Generate OpenAPI documentation automatically at /docs and /openapi.json

## Requirements

- Python 3.10+
- pip

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Local setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn main:app --reload
```

4. Open the interactive docs at:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## Environment variables

The application reads the following environment variable:

- DATABASE_URL: Optional database connection string. Defaults to a local SQLite database at ./expense_tracker.db.

Example:

```bash
$env:DATABASE_URL="sqlite:///./expense_tracker.db"
```

## API overview

### Health

- GET /health: Returns the health status of the service.

### Transactions

- POST /transactions: Create a transaction.
- GET /transactions: List transactions with pagination.
- GET /transactions/{transaction_id}: Retrieve a transaction by id.
- DELETE /transactions/{transaction_id}: Delete a transaction.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/transactions" \
  -H "Content-Type: application/json" \
  -d '{"description":"Coffee","amount":4.5,"category":"food"}'
```

## Testing

Run the test suite with:

```bash
pytest
```

Generate a coverage report with:

```bash
pytest --cov=. --cov-report=html
```

## Known limitations

- The application currently uses SQLite for local development and testing.
- Duplicate detection is intentionally simple and based on description, amount, category, and optional transaction date.
- The service layer focuses on the core CRUD workflow and does not yet include authentication, role-based access, or audit logging.
