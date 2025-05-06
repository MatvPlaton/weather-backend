from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import create_app
from domain import ApiError, WeatherApi, WeatherRepository, WeatherState, \
    UserRepository, User

@pytest.fixture
def mock_weather_api_success():
    mock = MagicMock(spec=WeatherApi)
    mock.get_weather.return_value = WeatherState(
        time=datetime.now(),
        city="London",
        temperature=20.5,
        feels_like=19.0,
        pressure=1015,
        humidity=65
    )
    return mock


@pytest.fixture
def mock_weather_api_error():
    mock = MagicMock(spec=WeatherApi)
    mock.get_weather.return_value = ApiError("City not found")
    return mock


@pytest.fixture
def mock_user_repository():
    mock = MagicMock(spec=UserRepository)
    mock.get_user.side_effect = lambda token: User(1, token)
    return mock


def test_get_weather_success(mock_weather_api_success, mock_user_repository):
    app = create_app(
        mock_weather_api_success, None, mock_user_repository, None, ""
    )
    client = TestClient(app)

    response = client.get("/weather", params={
        "user_token": "",
        "city": "London"
    })
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["temperature"] == 20.5
    assert data["feels_like"] == 19.0
    assert data["pressure"] == 1015
    assert data["humidity"] == 65


def test_get_weather_error(mock_weather_api_error, mock_user_repository):
    app = create_app(
        mock_weather_api_error, None, mock_user_repository, None, ""
    )
    client = TestClient(app)

    response = client.get("/weather", params={
        "user_token": "",
        "city": "London"
    })
    assert response.status_code == 500

    data = response.json()
    assert data["success"] is False
    assert "City not found" in data["error"]


@pytest.fixture
def mock_weather_api_invalid():
    mock = MagicMock(spec=WeatherApi)
    mock.get_weather.return_value = None
    return mock


def test_get_weather_invalid_response(mock_weather_api_invalid,
                                      mock_user_repository):
    app = create_app(
        mock_weather_api_invalid, None, mock_user_repository, None, ""
    )
    client = TestClient(app)

    response = client.get("/weather", params={
        "user_token": "",
        "city": "London"
    })
    assert response.status_code == 500

    data = response.json()
    assert data["success"] is False
    assert "Bad response from WeatherAPI" in data["error"]


@pytest.fixture
def mock_weather_repository():
    mock = MagicMock(spec=WeatherRepository)
    return mock


def test_get_weather_history_success(mock_weather_repository,
                                     mock_user_repository):
    mock_weather_repository.get_weather_history.return_value = [
        WeatherState(
            time=datetime(2024, 1, 1),
            city="London",
            temperature=10.0,
            feels_like=9.0,
            pressure=1020,
            humidity=70
        )
    ]
    app = create_app(
        None, mock_weather_repository, mock_user_repository, None, ""
    )
    client = TestClient(app)
    response = client.get("/weather/history", params={
        "user_token": "",
        "city": "London",
        "limit": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["history"]) == 1
    assert data["history"][0]["temperature"] == 10.0
    assert data["history"][0]["feels_like"] == 9.0
    assert data["history"][0]["pressure"] == 1020
    assert data["history"][0]["humidity"] == 70


def test_get_weather_history_failure(mock_weather_repository,
                                     mock_user_repository):
    mock_weather_repository.get_weather_history.side_effect = \
        Exception("Database error")
    app = create_app(
        None, mock_weather_repository, mock_user_repository, None, ""
    )
    client = TestClient(app)
    response = client.get("/weather/history", params={
        "user_token": "",
        "city": "London",
        "limit": 1,
    })

    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "Bad response from WeatherRepository: Database error" \
           in data["error"]
