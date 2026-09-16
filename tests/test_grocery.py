from fastapi.testclient import TestClient

from app.main import app
from app.api import grocery
from app.models.grocery import GroceryItem, GroceryList


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_parse_grocery_image(monkeypatch):
    async def mock_extract_grocery_list(
        image_bytes: bytes,
        content_type: str,
    ) -> GroceryList:
        assert image_bytes == b"fake-image"
        assert content_type == "image/jpeg"

        return GroceryList(
            items=[
                GroceryItem(
                    name="rice",
                    quantity=5,
                    unit="kg",
                    original_text="Rice 5kg",
                    confidence=0.97,
                ),
                GroceryItem(
                    name="milk",
                    quantity=2,
                    unit="packets",
                    original_text="Milk 2 packets",
                    confidence=0.95,
                ),
            ]
        )

    monkeypatch.setattr(
        grocery,
        "extract_grocery_list",
        mock_extract_grocery_list,
    )

    response = client.post(
        "/api/v1/grocery/parse",
        files={
            "image": (
                "grocery.jpg",
                b"fake-image",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "rice"
    assert data["items"][0]["quantity"] == 5
    assert data["items"][0]["unit"] == "kg"


def test_rejects_unsupported_file_type():
    response = client.post(
        "/api/v1/grocery/parse",
        files={
            "image": (
                "grocery.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400