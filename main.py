import os

from app import create_app
from domain_open_weather_map import OpenWeatherMapApi
from domain_sqlite import SqliteWeatherRepository
from domain_wrapper import CachedWeatherApi, WeatherApiWithRepository

open_weather_map_token = os.getenv("OPEN_WEATHER_MAP_TOKEN")

app = create_app(
    CachedWeatherApi(
        WeatherApiWithRepository(
            OpenWeatherMapApi(open_weather_map_token),
            SqliteWeatherRepository("database.db")
        ),
        30 * 60
    )
)
