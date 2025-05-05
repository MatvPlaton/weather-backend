from datetime import datetime
from typing import Union

from domain import ApiError, WeatherApi, WeatherRepository, WeatherState


class WeatherApiWithRepository(WeatherApi):

    def __init__(self, wrapped: WeatherApi, repository: WeatherRepository):
        self.wrapped = wrapped
        self.repository = repository

    def get_weather(self, city: str) -> Union[WeatherState, ApiError]:
        weather = self.wrapped.get_weather(city)
        if isinstance(weather, WeatherState):
            self.repository.save_weather(weather)
        return weather


class CachedWeatherApi(WeatherApi):

    def __init__(self, wrapped: WeatherApi, cache_seconds: int):
        self.wrapped = wrapped
        self.cache_seconds = cache_seconds
        self.cache = {}

    def get_weather(self, city: str) -> Union[WeatherState, ApiError]:
        current_time = round(datetime.now().timestamp())

        cached = self.cache.get(city)
        if cached is not None:
            expire_time = cached["expire_time"]
            if current_time <= expire_time:
                return cached["entity"]

        weather = self.wrapped.get_weather(city)
        if isinstance(weather, WeatherState):
            self.cache[city] = {
                "expire_time": current_time + self.cache_seconds,
                "entity": weather,
            }

        return weather
