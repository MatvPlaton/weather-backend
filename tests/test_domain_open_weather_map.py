import pytest
from unittest.mock import patch, MagicMock
import requests

from domain import ApiError, WeatherState, User
from domain_open_weather_map import OpenWeatherMapApi


@pytest.fixture
def api():
    return OpenWeatherMapApi("")


def mock_geo_response(*args, **kwargs):
    mock_response = MagicMock()
    mock_response.json.return_value = [{"lat": 50.23, "lon": 29.14}]
    return mock_response


def mock_weather_response(*args, **kwargs):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "main": {
            "temp": 20.5,
            "feels_like": 19.0,
            "pressure": 1015,
            "humidity": 65
        }
    }
    return mock_response


@patch("requests.get", side_effect=[
    mock_geo_response()
])
def test_get_lat_lon(mock_get, api):
    lat_lon = api._OpenWeatherMapApi__get_lat_lon("London")
    assert lat_lon == (50.23, 29.14)


@patch("requests.get", side_effect=[
    mock_geo_response(), mock_weather_response()
])
def test_get_weather_success(mock_get, api):
    weather = api.get_weather("London", User(1, ""))
    assert isinstance(weather, WeatherState)
    assert weather.city == "London"
    assert weather.temperature == 20.5
    assert weather.feels_like == 19.0
    assert weather.pressure == 1015
    assert weather.humidity == 65


@patch("requests.get", side_effect=[
    requests.exceptions.RequestException("Connection error")
])
def test_get_weather_request_exception(mock_get, api):
    weather = api.get_weather("London", User(1, ""))
    assert isinstance(weather, ApiError)
    assert "Connection error" in weather.message


@patch("requests.get", side_effect=[
    mock_geo_response(),
    requests.exceptions.RequestException("Connection error")
])
def test_get_weather_request_exception_2(mock_get, api):
    weather = api.get_weather("London", User(1, ""))
    assert isinstance(weather, ApiError)
    assert "Connection error" in weather.message
