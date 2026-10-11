import pytest
from fastapi.testclient import TestClient

import main
import mevent
from db import get_db

VALID_CHECK_IN = {
    "event_type": "check_in_depot",
    "timestamp": "2019-09-22T11:14:00Z",
    "extra_information": "Fiets meegenomen door handhaving.",
    "bike": {
        "brand": "Swapfiets",
        "frame_number": "12277588",
        "chip_number": "54513216",
        "license_plate": "44AGR4",
        "color": "blue",
        "description": "Blauwe swapfiets met fietstas.",
    },
    "depot_details": {
        "depot_id": "pf:42",
        "municipality_code": "GM0344",
        "city": "Utrecht",
        "name": "Kanaalweg",
    },
    "enforcement_details": {
        "city": "Houten",
        "municipality_code": "GM0321",
        "location_description": "Houten stations, fietsenstalling.",
        "free_text_reason": "Langer dan 28 dagen geparkeerd.",
    },
}


def fake_get_db():
    yield None


@pytest.fixture
def client():
    main.app.dependency_overrides[get_db] = fake_get_db
    yield TestClient(main.app)
    main.app.dependency_overrides.clear()


def test_openapi_is_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/event" in response.json()["paths"]


def test_event_persists_and_enqueues(client, monkeypatch):
    enqueued = []
    monkeypatch.setattr(
        mevent.Event,
        "insert",
        staticmethod(lambda conn, data: {"event_id": 1, "bike": data.bike.model_dump()}),
    )
    monkeypatch.setattr(main.output, "enqueue", enqueued.append)

    response = client.post("/event", json=VALID_CHECK_IN)

    assert response.status_code == 200
    assert response.json() == {"status": "created"}
    assert enqueued[0]["event_id"] == 1


def test_missing_required_field_returns_422(client):
    payload = dict(VALID_CHECK_IN)
    payload.pop("bike")

    response = client.post("/event", json=payload)

    assert response.status_code == 422
    assert "Incorrect JSON input" in response.json()["message"]


def test_check_in_without_enforcement_details_returns_422(client):
    payload = dict(VALID_CHECK_IN)
    payload.pop("enforcement_details")

    response = client.post("/event", json=payload)

    assert response.status_code == 422
    assert "Incorrect JSON input" in response.json()["message"]


def test_unknown_event_type_returns_422(client):
    payload = dict(VALID_CHECK_IN, event_type="something_else")

    response = client.post("/event", json=payload)

    assert response.status_code == 422
