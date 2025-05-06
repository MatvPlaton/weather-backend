from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union, List

# Entities


class WeatherState:

    def __init__(
        self,
        time: datetime,
        city: str,
        temperature: float,
        feels_like: float,
        pressure: int,
        humidity: int,
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


class User:

    def __init__(
        self,
        telegram_id: int,
        token: str
    ):
        self.telegram_id = telegram_id
        self.token = token

# Services


class WeatherRepository(ABC):

    @abstractmethod
    def get_weather_history(self, city: str, limit: int) -> List[WeatherState]:
        pass

    @abstractmethod
    def save_weather(self, weather_state: WeatherState):
        pass


class WeatherApi(ABC):

    @abstractmethod
    def get_weather(self, city: str) -> Union[WeatherState, ApiError]:
        pass


class UserRepository(ABC):

    @abstractmethod
    def get_user(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    def save_user(self, telegram_id: int, token: str):
        pass


class UserLoginRepository(ABC):

    @abstractmethod
    def add_user_login(self, token: str, callback_url: str):
        pass

    @abstractmethod
    def delete_user_login(self, token: str) -> bool:
        pass
