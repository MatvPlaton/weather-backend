import sqlite3
from datetime import datetime
from threading import RLock
from typing import Optional, List

from domain import WeatherRepository, WeatherState


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

    def get_weather(self, time: datetime, city: str) -> Optional[WeatherState]:
        with self.lock:
            result = self.cursor.execute(
                """
                    SELECT temperature, feels_like, pressure, humidity
                    FROM weather
                    WHERE time = ? AND city = ?
                """,
                (round(time.timestamp() * 1000), city),
            ).fetchone()

            if result is not None:
                return WeatherState(
                    time,
                    city,
                    result["temperature"],
                    result["feels_like"],
                    result["pressure"],
                    result["humidity"],
                )

            return None
    
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
