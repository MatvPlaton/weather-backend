from typing import Union, List

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from domain import ApiError, WeatherApi, WeatherState, WeatherRepository
from notifications import send_notification


def create_app(weather_api: WeatherApi, weather_repository: WeatherRepository):
    app = FastAPI()
    clients = []

    class SuccessResponse(BaseModel):
        success: bool
        temperature: float
        feels_like: float
        pressure: int
        humidity: int

    class WeatherEntity(BaseModel):
        time: float
        temperature: float
        feels_like: float
        pressure: int
        humidity: int

    class HistorySuccessResponse(BaseModel):
        success: bool
        history: List[WeatherEntity]

    class ErrorResponse(BaseModel):
        success: bool
        error: str

    @app.get(
        "/weather/{city}",
        response_model=SuccessResponse,
        responses={
            500: {
                "model": ErrorResponse,
                "description": "Internal Server Error"
            }
        },
    )
    def get_weather(city: str) -> Union[SuccessResponse, ErrorResponse]:
        weather = weather_api.get_weather(city)
        if isinstance(weather, WeatherState):
            return {
                "success": True,
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "pressure": weather.pressure,
                "humidity": weather.humidity,
            }
        else:
            msg = "Bad response from WeatherAPI"
            if isinstance(weather, ApiError):
                msg += ": " + weather.message
            return JSONResponse(
                status_code=500, content={"success": False, "error": msg}
            )

    @app.get(
        "/weather/history/{city}/{limit}",
        response_model=HistorySuccessResponse,
        responses={
            500: {
                "model": ErrorResponse,
                "description": "Internal Server Error"
            }
        },
    )
    def get_weather_history(city: str, limit: int) ->\
            Union[HistorySuccessResponse, ErrorResponse]:
        try:
            history = weather_repository.get_weather_history(city, limit)
            entities = list(
                map(
                    lambda weather: {
                        "time": weather.time.timestamp(),
                        "temperature": weather.temperature,
                        "feels_like": weather.feels_like,
                        "pressure": weather.pressure,
                        "humidity": weather.humidity
                    },
                    history
                )
            )
            return {
                "success": True,
                "history": entities
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Bad response from WeatherRepository: {e}"
                }
            )

    @app.websocket("/ws/notify")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        clients.append(websocket)
        print("client attached")
        try:
            while True:
                await websocket.receive_text()
        except Exception:
            clients.remove(websocket)

    @app.post("/notification-test")
    async def notification_test():
        print("clients: " + str(len(clients)))
        for client in clients:
            await send_notification(client, "TEST NOTIFICATION")

    return app
