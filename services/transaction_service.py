from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from models import Category, Transaction


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, payload: dict[str, Any], db: Session | None = None):
        if db is None:
            db = self.db

        if self.deduplicate_transaction(payload, db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate transaction")

        transaction_date = payload.get("transaction_date") or datetime.utcnow()
        category_name = payload.get("category", "uncategorized")
        category = db.query(Category).filter(Category.name == category_name).first()
        if category is None:
            category = Category(name=category_name)
            db.add(category)
            db.flush()

        db_transaction = Transaction(
            description=payload["description"],
            amount=payload["amount"],
            category=category_name,
            category_id=category.id,
            transaction_date=transaction_date,
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def list_transactions(self, db: Session | None = None, page: int = 1, page_size: int = 10):
        if db is None:
            db = self.db
        offset = (page - 1) * page_size
        return (
            db.query(Transaction)
            .options(joinedload(Transaction.category_detail))
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def get_transaction(self, transaction_id: int, db: Session | None = None):
        if db is None:
            db = self.db
        transaction = (
            db.query(Transaction)
            .options(joinedload(Transaction.category_detail))
            .filter(Transaction.id == transaction_id)
            .first()
        )
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction

    def delete_transaction(self, transaction_id: int, db: Session | None = None):
        if db is None:
            db = self.db
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        db.delete(transaction)
        db.commit()
        return None

    def deduplicate_transaction(self, transaction_data, db_session):
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
