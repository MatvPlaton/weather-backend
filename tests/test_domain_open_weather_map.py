from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app import create_app
from domain import ApiError, WeatherApi, WeatherState, WeatherRepository, \
    UserRepository, UserLoginRepository

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


def test_get_weather_success(mock_weather_api_success):
    app = create_app(mock_weather_api_success,None,None,None,"")
    client = TestClient(app)

    response = client.get("/weather/London")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["temperature"] == 20.5
    assert data["feels_like"] == 19.0
    assert data["pressure"] == 1015
    assert data["humidity"] == 65


def test_get_weather_error(mock_weather_api_error):
    app = create_app(mock_weather_api_error,None,None,None,"")
    client = TestClient(app)

    response = client.get("/weather/London")
    assert response.status_code == 500

    data = response.json()
    assert data["success"] is False
    assert "City not found" in data["error"]


@pytest.fixture
def mock_weather_api_invalid():
    mock = MagicMock(spec=WeatherApi)
    mock.get_weather.return_value = None
    return mock


def test_get_weather_invalid_response(mock_weather_api_invalid):
    app = create_app(mock_weather_api_invalid,None,None,None,"")
    client = TestClient(app)

    response = client.get("/weather/London")
    assert response.status_code == 500

    data = response.json()
    assert data["success"] is False
    assert "Bad response from WeatherAPI" in data["error"]
