import sqlite3
from datetime import datetime
from threading import RLock
from typing import Optional, List

from domain import WeatherRepository, WeatherState, User, UserRepository


class SqliteWeatherRepository(WeatherRepository):

    def __init__(self, file_name: str):
        self.lock = RLock()

        self.connection = sqlite3.connect(file_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather(
                time INTEGER,
                city TEXT,
                temperature REAL,
                feels_like REAL,
                pressure INT,
                humidity INT,
                PRIMARY KEY (time, city)
            )
            """
        )
        self.connection.commit()

    def get_weather_history(self, city: str, limit: int) -> List[WeatherState]:
        with self.lock:
            result = self.cursor.execute(
                """
                    SELECT time, temperature, feels_like, pressure, humidity
                    FROM weather
                    WHERE city = ?
                    ORDER BY time DESC
                    LIMIT ?
                """,
                (city, limit),
            )

            states = []
            for row in result:
                states.append(
                    WeatherState(
                        datetime.fromtimestamp(row[0] / 1000),
                        city,
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                    )
                )

            return states

    def save_weather(self, weather_state: WeatherState):
        with self.lock:
            self.cursor.execute(
                """
                    INSERT INTO weather(time, city, temperature,
                                        feels_like, pressure, humidity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    round(weather_state.time.timestamp() * 1000),
                    weather_state.city,
                    weather_state.temperature,
                    weather_state.feels_like,
                    weather_state.pressure,
                    weather_state.humidity,
                ),
            )
            self.connection.commit()


class SqliteUserRepository(UserRepository):

    def __init__(self, file_name: str):
        self.lock = RLock()

        self.connection = sqlite3.connect(file_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                telegram_id INTEGER,
                token TEXT UNIQUE,
                PRIMARY KEY (telegram_id)
            )
        """
        )
        self.connection.commit()

    def get_user(self, token: str) -> Optional[User]:
        with self.lock:
            result = self.cursor.execute(
                """
                    SELECT telegram_id
                    FROM user
                    WHERE token = ?
                """,
                (token),
            ).fetchone()

            if result is not None:
                return User(
                    result["telegram_id"],
                    token,
                )

            return None

    def save_user(self, telegram_id: int, token: str):
        with self.lock:
            self.cursor.execute(
                """
                    INSERT OR REPLACE INTO users(telegram_id, token)
                    VALUES(?, ?)
                """,
                (telegram_id, token),
            )
            self.connection.commit()
