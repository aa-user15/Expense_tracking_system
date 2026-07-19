from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, Query, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from db import get_db, init_db
from models import Transaction
from services.transaction_service import TransactionService

# Create app instance
app = FastAPI(
    title="Expense Tracker API",
    description="A lightweight FastAPI service for creating, listing, retrieving, and deleting expense transactions.",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    init_db()


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)


class TransactionCreate(BaseModel):
    description: str
    amount: float
    category: str = "uncategorized"
    transaction_date: datetime | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("description must not be empty")
        return value


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    amount: float
    category: str
    transaction_date: datetime
    created_at: datetime


@app.get("/", tags=["health"])
def read_root():
    """Return a welcome message for the API root."""
    return {"message": "Welcome to the Expense Tracker API"}


@app.get("/health", tags=["health"])
def health_check():
    """Report the API health status for readiness checks."""
    return {"status": "healthy"}


@app.post(
    "/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"],
)
def create_transaction(
    payload: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    """Create a new expense transaction.

    The request body accepts a description, amount, optional category, and optional transaction date.
    If a transaction appears to be a duplicate of an existing record, the API returns a 409 Conflict response.
    """
    return service.create_transaction(payload.model_dump())


@app.get("/transactions", response_model=List[TransactionRead], tags=["transactions"])
def list_transactions(
    service: TransactionService = Depends(get_transaction_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
):
    """List transactions with simple pagination support.

    Results are ordered from newest to oldest so that paginated responses remain predictable for clients.
    """
    return service.list_transactions(page=page, page_size=page_size)


@app.get("/transactions/{transaction_id}", response_model=TransactionRead, tags=["transactions"])
def get_transaction(transaction_id: int, service: TransactionService = Depends(get_transaction_service)):
    """Retrieve a single transaction by its identifier.

    If the requested transaction does not exist, the endpoint returns a 404 Not Found response.
    """
    return service.get_transaction(transaction_id)


@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["transactions"])
def delete_transaction(transaction_id: int, service: TransactionService = Depends(get_transaction_service)):
    """Delete a transaction if it exists.

    A successful deletion returns 204 No Content. Missing transactions return 404 Not Found.
    """
    return service.delete_transaction(transaction_id)


def deduplicate_transaction(transaction_data, db_session):
    service = TransactionService(db_session)
    return service.deduplicate_transaction(transaction_data, db_session)




