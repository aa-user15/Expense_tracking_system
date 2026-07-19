from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, Query, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from db import get_db, init_db
from models import Transaction
from services.transaction_service import TransactionService

# Create app instance
app = FastAPI(title="Expense Tracker API", description="This is a simple API for tracking expenses.", version="1.0.0")


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


# Create a root endpoint and health check endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# create a new transaction for expense tracking system
@app.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, service: TransactionService = Depends(get_transaction_service)):
    return service.create_transaction(payload.model_dump())


# retrieve all transactions
@app.get("/transactions", response_model=List[TransactionRead])
def list_transactions(
    service: TransactionService = Depends(get_transaction_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
):
    return service.list_transactions(page=page, page_size=page_size)


# retrieve a single transaction by its ID
@app.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, service: TransactionService = Depends(get_transaction_service)):
    return service.get_transaction(transaction_id)


# delete a transaction from the database if it exists
@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, service: TransactionService = Depends(get_transaction_service)):
    return service.delete_transaction(transaction_id)


def deduplicate_transaction(transaction_data, db_session):
    service = TransactionService(db_session)
    return service.deduplicate_transaction(transaction_data, db_session)














