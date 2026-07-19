from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import Base, get_db
import main
from models import Transaction


def test_transaction_model_has_expected_table_and_columns():
    assert Transaction.__tablename__ == "transactions"
    assert "description" in Transaction.__table__.columns.keys()
    assert "amount" in Transaction.__table__.columns.keys()
    assert "category" in Transaction.__table__.columns.keys()


def test_deduplicate_transaction_detects_existing_duplicate():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        existing_transaction = Transaction(
            description="Coffee",
            amount=4.5,
            category="food",
            transaction_date=datetime(2024, 1, 1, 10, 0, 0),
        )
        session.add(existing_transaction)
        session.commit()

        duplicate_payload = {
            "description": "Coffee",
            "amount": 4.5,
            "category": "food",
            "transaction_date": datetime(2024, 1, 1, 10, 0, 0),
        }
        assert main.deduplicate_transaction(duplicate_payload, session) is True

        different_payload = {
            "description": "Lunch",
            "amount": 4.5,
            "category": "food",
            "transaction_date": datetime(2024, 1, 1, 10, 0, 0),
        }
        assert main.deduplicate_transaction(different_payload, session) is False


def test_transaction_crud_endpoints_work():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    client = TestClient(main.app)

    response = client.post(
        "/transactions",
        json={"description": "Coffee", "amount": 4.5, "category": "food"},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["description"] == "Coffee"
    assert created["amount"] == 4.5

    response = client.get("/transactions")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1

    response = client.get(f"/transactions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["description"] == "Coffee"

    response = client.delete(f"/transactions/{created['id']}")
    assert response.status_code == 204

    response = client.get("/transactions")
    assert response.status_code == 200
    assert response.json() == []

    main.app.dependency_overrides.clear()
