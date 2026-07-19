from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from models import Category, Transaction


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction_data: dict, db_session: Optional[Session] = None):
        session = db_session or self.db
        payload = dict(transaction_data)

        if self.deduplicate_transaction(payload, session):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate transaction")

        category_name = payload.get("category") or "uncategorized"
        category = session.query(Category).filter(Category.name == category_name).first()
        if category is None:
            category = Category(name=category_name)
            session.add(category)
            session.flush()

        transaction_date = payload.get("transaction_date")
        if transaction_date is None:
            transaction_date = datetime.utcnow()

        transaction = Transaction(
            description=payload["description"],
            amount=payload["amount"],
            category=category_name,
            category_id=category.id,
            transaction_date=transaction_date,
            created_at=datetime.utcnow(),
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction

    def list_transactions(self, db_session: Optional[Session] = None, page: int = 1, page_size: int = 10):
        session = db_session or self.db
        offset = (page - 1) * page_size
        return (
            session.query(Transaction)
            .options(joinedload(Transaction.category_detail))
            .order_by(desc(Transaction.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def get_transaction(self, transaction_id: int, db_session: Optional[Session] = None):
        session = db_session or self.db
        transaction = (
            session.query(Transaction)
            .options(joinedload(Transaction.category_detail))
            .filter(Transaction.id == transaction_id)
            .first()
        )
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return transaction

    def delete_transaction(self, transaction_id: int, db_session: Optional[Session] = None):
        session = db_session or self.db
        transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        session.delete(transaction)
        session.commit()
        return None

    def deduplicate_transaction(self, transaction_data: dict, db_session: Optional[Session] = None) -> bool:
        session = db_session or self.db

        description = transaction_data.get("description")
        amount = transaction_data.get("amount")
        category = transaction_data.get("category") or "uncategorized"
        transaction_date = transaction_data.get("transaction_date")

        query = session.query(Transaction).filter(
            Transaction.description == description,
            Transaction.amount == amount,
            Transaction.category == category,
        )

        if transaction_date is None:
            return query.first() is not None

        return query.filter(Transaction.transaction_date == transaction_date).first() is not None
