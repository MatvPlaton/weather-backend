from datetime import datetime
from typing import Tuple, Union

import requests

from domain import ApiError, WeatherApi, WeatherState, User


class OpenWeatherMapApi(WeatherApi):

    def __init__(self, token: str):
        self.token = token
        self.city_to_lat_lon = {}

    def get_weather(self, city: str, user: User) -> \
            Union[WeatherState, ApiError]:
        lat_lon = self.__get_lat_lon(city)
        if isinstance(lat_lon, ApiError):
            return lat_lon

        try:
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat_lon[0],
                    "lon": lat_lon[1],
                    "appid": self.token,
                    "units": "metric",
                },
                timeout=3,
            )
        except requests.exceptions.RequestException as e:
            return ApiError(str(e))

        data = response.json()["main"]
        return WeatherState(
            datetime.now(),
            city,
            data["temp"],
            data["feels_like"],
            data["pressure"],
            data["humidity"],
        )

    def __get_lat_lon(self, city: str) -> Tuple[int, int]:
        lat_lon = self.city_to_lat_lon.get(city)
        if lat_lon is not None:
            return lat_lon

        try:
            response = requests.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={"q": city, "limit": 1, "appid": self.token},
                timeout=3,
            )
        except requests.exceptions.RequestException as e:
            return ApiError(str(e))

        data = response.json()[0]
        return (data["lat"], data["lon"])
