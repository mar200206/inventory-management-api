import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_inventory.db"))
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def sample_product(**overrides):
    product = {
        "name": "Mechanical Keyboard",
        "sku": "KB-001",
        "quantity": 12,
        "price": 79.99,
        "description": "Compact keyboard",
    }
    product.update(overrides)
    return product


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_product(client):
    created = client.post("/products", json=sample_product())
    assert created.status_code == 201
    product = created.json()
    assert product["name"] == "Mechanical Keyboard"
    assert product["sku"] == "KB-001"
    assert product["id"] > 0

    fetched = client.get(f"/products/{product['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["sku"] == "KB-001"


def test_duplicate_sku_returns_conflict(client):
    client.post("/products", json=sample_product())
    response = client.post("/products", json=sample_product(name="Another Keyboard"))
    assert response.status_code == 409


def test_list_search_and_pagination(client):
    client.post("/products", json=sample_product())
    client.post(
        "/products",
        json=sample_product(name="USB-C Hub", sku="HUB-001", quantity=4, price=25.5),
    )

    assert len(client.get("/products").json()) == 2
    assert len(client.get("/products", params={"search": "USB"}).json()) == 1
    assert len(client.get("/products", params={"limit": 1}).json()) == 1


def test_update_product(client):
    created = client.post("/products", json=sample_product()).json()
    response = client.patch(
        f"/products/{created['id']}", json={"quantity": 7, "price": 69.5}
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 7
    assert response.json()["price"] == 69.5


def test_delete_product(client):
    created = client.post("/products", json=sample_product()).json()
    response = client.delete(f"/products/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/products/{created['id']}").status_code == 404


def test_validation_rejects_negative_quantity(client):
    response = client.post("/products", json=sample_product(quantity=-1))
    assert response.status_code == 422


def test_missing_product_returns_404(client):
    assert client.get("/products/999").status_code == 404
    assert client.delete("/products/999").status_code == 404


def test_patch_rejects_empty_payload(client):
    created = client.post("/products", json=sample_product()).json()
    response = client.patch(f"/products/{created['id']}", json={})
    assert response.status_code == 400
