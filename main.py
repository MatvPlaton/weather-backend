import os

from dotenv import load_dotenv

from app import create_app
from domain_open_weather_map import OpenWeatherMapApi
from domain_sqlite import SqliteWeatherRepository
from domain_wrapper import CachedWeatherApi, WeatherApiWithRepository

load_dotenv()
open_weather_map_token = os.getenv("OPEN_WEATHER_MAP_TOKEN")

repository = SqliteWeatherRepository("database.db")

app = create_app(
    CachedWeatherApi(
        WeatherApiWithRepository(
            OpenWeatherMapApi(open_weather_map_token),
            repository,
        ),
        30 * 60,
    ),
    repository
)
