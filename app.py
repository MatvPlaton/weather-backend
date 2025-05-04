from domain import WeatherState, ApiError, WeatherApi
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union

from notifications import send_notification


def create_app(weather_api: WeatherApi):
    app = FastAPI()
    clients = []

    class SuccessResponse(BaseModel):
        success: bool
        temperature: float
        feels_like: float
        pressure: int
        humidity: int

    class ErrorResponse(BaseModel):
        success: bool
        error: str

    @app.get("/weather/{city}", response_model=SuccessResponse, responses={
        500: {
            "model": ErrorResponse,
            "description": "Internal Server Error"
        }
    })
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
                status_code=500,
                content={
                    "success": False,
                    "error": msg
                }
            )

    @app.websocket("/ws/notify")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        clients.append(websocket)
        print('client attached')
        try:
            while True:
                await websocket.receive_text()
        except:
            clients.remove(websocket)

    @app.post('/notification-test')
    async def notification_test():
        print('clients: ' + str(len(clients)))
        for client in clients:
            await send_notification(client, "TEST NOTIFICATION")

    return app
