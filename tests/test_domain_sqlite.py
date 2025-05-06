import pytest
from datetime import datetime, timedelta
import os
import contextlib

from domain import WeatherState, User
from domain_sqlite import SqliteWeatherRepository


@pytest.fixture
def weather_repository():
    with contextlib.suppress(FileNotFoundError):
        os.remove("tests/test.db")

    yield SqliteWeatherRepository("tests/test.db")

    with contextlib.suppress(FileNotFoundError):
        os.remove("tests/test.db")


@pytest.mark.skip
def assert_weather_eq(weather1, weather2):
    def normalized_time(weather):
        return datetime.fromtimestamp(
            round(weather.time.timestamp() * 1000) / 1000
        )

    assert normalized_time(weather1) == normalized_time(weather2)
    assert weather1.city == weather2.city
    assert weather1.temperature == weather2.temperature
    assert weather1.feels_like == weather2.feels_like
    assert weather1.pressure == weather2.pressure
    assert weather1.humidity == weather2.humidity


def test_weather_repository_save_weather(weather_repository):
    weather = WeatherState(
        time=datetime.now(),
        city="London",
        temperature=20.5,
        feels_like=19.0,
        pressure=1015,
        humidity=65
    )

    count = weather_repository.cursor.execute(
        "SELECT COUNT(*) FROM weather"
    ).fetchone()[0]
    assert count == 0

    weather_repository.save_weather(weather, User(1, ""))

    count = weather_repository.cursor.execute(
        "SELECT COUNT(*) FROM weather"
    ).fetchone()[0]
    assert count == 1

    result = weather_repository.cursor.execute(
        """
        SELECT time, city, temperature, feels_like, pressure, humidity
        FROM weather
        """
    ).fetchone()

    assert round(weather.time.timestamp() * 1000) == result[0]
    assert weather.city == result[1]
    assert weather.temperature == result[2]
    assert weather.feels_like == result[3]
    assert weather.pressure == result[4]
    assert weather.humidity == result[5]


def test_weather_repository_get_weather_history(weather_repository):
    weather1 = WeatherState(
        time=datetime.now() - timedelta(minutes=30),
        city="London",
        temperature=20.5,
        feels_like=19.0,
        pressure=1015,
        humidity=65
    )
    user1 = User(1, "")

    weather2 = WeatherState(
        time=datetime.now(),
        city="London",
        temperature=21.8,
        feels_like=21.2,
        pressure=1000,
        humidity=60
    )
    user2 = User(2, "")

    weather_repository.save_weather(weather1, user1)
    weather_repository.save_weather(weather2, user2)

    history = weather_repository.get_weather_history(5, "London")
    assert len(history) == 2
    assert_weather_eq(history[0], weather2)
    assert_weather_eq(history[1], weather1)

    history = weather_repository.get_weather_history(1, "London")
    assert len(history) == 1
    assert_weather_eq(history[0], weather2)

    history = weather_repository.get_weather_history(1, "Moscow")
    assert len(history) == 0

    history = weather_repository.get_weather_history(1, user1)
    assert len(history) == 1
    assert_weather_eq(history[0], weather1)
