from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import Base, get_db
import main
from models import Transaction
from services.transaction_service import TransactionService


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


def test_duplicate_inserts_are_rejected_when_transaction_date_is_missing():
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

    first_response = client.post(
        "/transactions",
        json={"description": "Coffee", "amount": 4.5, "category": "food"},
    )
    second_response = client.post(
        "/transactions",
        json={"description": "Coffee", "amount": 4.5, "category": "food"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    main.app.dependency_overrides.clear()


def test_transactions_support_pagination():
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

    client.post("/transactions", json={"description": "A", "amount": 1, "category": "food"})
    client.post("/transactions", json={"description": "B", "amount": 2, "category": "food"})
    client.post("/transactions", json={"description": "C", "amount": 3, "category": "food"})

    response = client.get("/transactions", params={"page": 2, "page_size": 1})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["description"] == "B"

    main.app.dependency_overrides.clear()


def test_transaction_service_handles_crud_operations():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        service = TransactionService(session)
        created = service.create_transaction(
            {"description": "Taxi", "amount": 12.5, "category": "transport"},
            session,
        )

        assert created.description == "Taxi"
        assert service.get_transaction(created.id, session).description == "Taxi"
        assert len(service.list_transactions(session, page=1, page_size=10)) == 1

        service.delete_transaction(created.id, session)
        assert service.list_transactions(session, page=1, page_size=10) == []


def test_transaction_service_loads_related_category_eagerly():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        service = TransactionService(session)
        created = service.create_transaction(
            {"description": "Bus", "amount": 3.5, "category": "transport"},
            session,
        )

        fetched = service.get_transaction(created.id, session)
        assert fetched.category_detail is not None
        assert fetched.category_detail.name == "transport"


def test_dependency_injection_provides_transaction_service():
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

    response = client.get("/transactions")
    assert response.status_code == 200

    service = main.get_transaction_service(next(override_get_db()))
    assert isinstance(service, TransactionService)

    main.app.dependency_overrides.clear()
