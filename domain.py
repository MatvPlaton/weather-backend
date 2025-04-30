from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union


# Entities

class WeatherState:

    def __init__(
        self,
        time: datetime,
        city: str,
        temperature: float,
        feels_like: float,
        pressure: int,
        humidity: int
    ):
        self.time = time
        self.city = city
        self.temperature = temperature
        self.feels_like = feels_like
        self.pressure = pressure
        self.humidity = humidity


class ApiError:

    def __init__(self, message: str):
        self.message = message


# Services

class WeatherRepository(ABC):

    @abstractmethod
    def get_weather(self, time: datetime, city: str) -> Optional[WeatherState]:
        pass

    @abstractmethod
    def save_weather(self, weather_state: WeatherState):
        pass


class WeatherApi(ABC):

    @abstractmethod
    def get_weather(self, city: str) -> Union[WeatherState, ApiError]:
        pass
