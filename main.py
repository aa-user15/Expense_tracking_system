from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from db import get_db, init_db
from models import Transaction

# Create app instance
app = FastAPI(title="Expense Tracker API", description="This is a simple API for tracking expenses.", version="1.0.0")


@app.on_event("startup")
def startup_event():
    init_db()


class TransactionCreate(BaseModel):
    description: str
    amount: float
    category: str = "uncategorized"
    transaction_date: datetime | None = None


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
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    payload_data = payload.model_dump()
    if deduplicate_transaction(payload_data, db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate transaction")

    transaction_date = payload.transaction_date or datetime.utcnow()
    db_transaction = Transaction(
        description=payload.description,
        amount=payload.amount,
        category=payload.category,
        transaction_date=transaction_date,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


# retrieve all transactions
@app.get("/transactions", response_model=List[TransactionRead])
def list_transactions(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
):
    offset = (page - 1) * page_size
    return (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


# retrieve a single transaction by its ID
@app.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


# delete a transaction from the database if it exists
@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return None


def deduplicate_transaction(transaction_data, db_session):
    """
    Check if a transaction already exists.

    A duplicate transaction has the same description, amount,
    category, and transaction_date as an existing transaction.

    Return True if a duplicate exists.
    Return False otherwise.
    """
    if db_session is None:
        return False

    if hasattr(transaction_data, "__dict__"):
        transaction_data = transaction_data.__dict__

    if not isinstance(transaction_data, dict):
        return False

    description = transaction_data.get("description")
    amount = transaction_data.get("amount")
    category = transaction_data.get("category")
    transaction_date = transaction_data.get("transaction_date")

    if description is None or amount is None or category is None:
        return False

    filters = [
        Transaction.description == description,
        Transaction.amount == amount,
        Transaction.category == category,
    ]
    if transaction_date is not None:
        filters.append(Transaction.transaction_date == transaction_date)

    existing_transaction = db_session.query(Transaction).filter(*filters).first()

    return existing_transaction is not None














