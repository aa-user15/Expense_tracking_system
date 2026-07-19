from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import Base, get_db
import main
from models import Transaction
from services.transaction_service import TransactionService


@pytest.fixture()
def client():
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
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


@pytest.fixture()
def service_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session


def test_root_and_health_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the Expense Tracker API"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"description": "Coffee", "amount": 4.5}, 201),
        ({"description": "Lunch", "amount": 7.0, "category": "food"}, 201),
    ],
)
def test_create_transaction_happy_paths(client, payload, expected_status):
    response = client.post("/transactions", json=payload)

    assert response.status_code == expected_status
    body = response.json()
    assert body["description"] == payload["description"]
    assert body["amount"] == payload["amount"]
    assert body["category"] == payload.get("category", "uncategorized")


@pytest.mark.parametrize(
    "payload",
    [
        {"amount": 4.5},
        {"description": "Coffee", "amount": "invalid"},
        {"description": "", "amount": 4.5},
    ],
)
def test_create_transaction_validation_errors(client, payload):
    response = client.post("/transactions", json=payload)

    assert response.status_code == 422


def test_list_transactions_returns_all_created_items(client):
    client.post("/transactions", json={"description": "A", "amount": 1, "category": "food"})
    client.post("/transactions", json={"description": "B", "amount": 2, "category": "food"})

    response = client.get("/transactions")
    assert response.status_code == 200
    items = response.json()
    assert [item["description"] for item in items] == ["B", "A"]


def test_get_transaction_returns_existing_item(client):
    created = client.post("/transactions", json={"description": "Taxi", "amount": 12.5, "category": "transport"})

    response = client.get(f"/transactions/{created.json()['id']}")
    assert response.status_code == 200
    assert response.json()["description"] == "Taxi"


def test_get_transaction_returns_404_for_missing_item(client):
    response = client.get("/transactions/999")
    assert response.status_code == 404


def test_delete_transaction_removes_item(client):
    created = client.post("/transactions", json={"description": "Coffee", "amount": 4.5, "category": "food"})

    delete_response = client.delete(f"/transactions/{created.json()['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/transactions")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_duplicate_transactions_are_rejected_when_payload_repeats(client):
    first = client.post("/transactions", json={"description": "Coffee", "amount": 4.5, "category": "food"})
    second = client.post("/transactions", json={"description": "Coffee", "amount": 4.5, "category": "food"})

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Duplicate transaction"


def test_duplicate_detection_with_missing_transaction_date_is_rejected(client):
    first = client.post(
        "/transactions",
        json={"description": "Coffee", "amount": 4.5, "category": "food", "transaction_date": None},
    )
    second = client.post(
        "/transactions",
        json={"description": "Coffee", "amount": 4.5, "category": "food", "transaction_date": None},
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_pagination_returns_expected_slice(client):
    client.post("/transactions", json={"description": "A", "amount": 1, "category": "food"})
    client.post("/transactions", json={"description": "B", "amount": 2, "category": "food"})
    client.post("/transactions", json={"description": "C", "amount": 3, "category": "food"})

    response = client.get("/transactions", params={"page": 2, "page_size": 1})
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["description"] == "B"


def test_transaction_service_crud_layer_works(service_session):
    service = TransactionService(service_session)

    created = service.create_transaction({"description": "Taxi", "amount": 12.5, "category": "transport"}, service_session)
    assert created.description == "Taxi"

    fetched = service.get_transaction(created.id, service_session)
    assert fetched.description == "Taxi"

    listed = service.list_transactions(service_session, page=1, page_size=10)
    assert len(listed) == 1

    service.delete_transaction(created.id, service_session)
    assert service.list_transactions(service_session, page=1, page_size=10) == []


def test_transaction_service_eager_loads_related_category(service_session):
    service = TransactionService(service_session)
    created = service.create_transaction({"description": "Bus", "amount": 3.5, "category": "transport"}, service_session)

    fetched = service.get_transaction(created.id, service_session)
    assert fetched.category_detail is not None
    assert fetched.category_detail.name == "transport"
