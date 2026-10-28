import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["alex@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app, follow_redirects=False) as test_client:
        yield test_client


def test_root_redirects_to_static_page(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["alex@example.com"],
        }
    }


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up sam@example.com for Chess Club"}
    assert app_module.activities["Chess Club"]["participants"] == [
        "alex@example.com",
        "sam@example.com",
    ]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities["Chess Club"]["participants"] == ["alex@example.com"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed alex@example.com from Chess Club"}
    assert app_module.activities["Chess Club"]["participants"] == []


def test_remove_participant_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_404_when_not_signed_up(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert app_module.activities["Chess Club"]["participants"] == ["alex@example.com"]