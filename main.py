import os

from dotenv import load_dotenv

from app import create_app
from domain_open_weather_map import OpenWeatherMapApi
from domain_sqlite import SqliteWeatherRepository, SqliteUserRepository
from domain_memory import InMemoryUserLoginRepository
from domain_wrapper import CachedWeatherApi, WeatherApiWithRepository

load_dotenv()
open_weather_map_token = os.getenv("OPEN_WEATHER_MAP_TOKEN")
telegram_service_authorization_token = os.getenv("TELEGRAM_SERVICE_AUTHORIZATION_TOKEN")

weather_repository = SqliteWeatherRepository("weather.db")

app = create_app(
    CachedWeatherApi(
        WeatherApiWithRepository(
            OpenWeatherMapApi(open_weather_map_token),
            weather_repository,
        ),
        30 * 60,
    ),
    weather_repository,
    SqliteUserRepository("users.db"),
    InMemoryUserLoginRepository(),
    telegram_service_authorization_token
)
