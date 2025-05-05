from typing import Union, List, Annotated

from fastapi import FastAPI, WebSocket, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

from domain import ApiError, WeatherApi, WeatherState, WeatherRepository, \
    UserRepository, UserLoginRepository
from notifications import send_notification


def create_app(weather_api: WeatherApi, weather_repository: WeatherRepository,
               user_repository: UserRepository,
               user_login_repository: UserLoginRepository,
               telegram_service_authorization_token: str):
    app = FastAPI()
    clients = []

    class WeatherResponse(BaseModel):
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

    class HistoryResponse(BaseModel):
        success: bool
        history: List[WeatherEntity]

    class EmptyResponse(BaseModel):
        success: bool

    class ErrorResponse(BaseModel):
        success: bool
        error: str

    forbidden_response = {
        "model": ErrorResponse,
        "description": "Forbidden"
    }
    not_found_response = {
        "model": ErrorResponse,
        "description": "Not Found"
    }
    error_response = {
        "model": ErrorResponse,
        "description": "Internal Server Error"
    }

    # Weather

    @app.get(
        "/weather/{city}",
        response_model=WeatherResponse,
        responses={
            500: error_response
        },
    )
    def get_weather(city: str) -> Union[WeatherResponse, ErrorResponse]:
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
        "/weather/history/{city}",
        response_model=HistoryResponse,
        responses={
            500: error_response
        },
    )
    def get_weather_history(city: str, limit: int) ->\
            Union[HistoryResponse, ErrorResponse]:
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

    # User

    @app.post(
        "/user/login",
        response_model=EmptyResponse,
        responses={
            500: error_response
        },
    )
    def user_login(token: str, callback_url: str):
        try:
            user_login_repository.add_user_login(token, callback_url)
            return {
                "success": True
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Bad response from UserLoginRepository: {e}"
                }
            )

    @app.post(
        "/user/successful_login",
        response_model=EmptyResponse,
        responses={
            403: forbidden_response,
            404: not_found_response,
            500: error_response,
        },
    )
    def user_successful_login(token: str, telegram_id: int, authorization_token: str):
        if authorization != telegram_service_authorization_token:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "Forbidden"
                }
            )

        try:
            callback_url = user_login_repository.delete_user_login()
            if callback_url is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": f"Token {token} Not Found"
                    }
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Bad response from UserLoginRepository: {e}"
                }
            )

        try:
            requests.get(
                callback_url,
                params={
                    "token": token,
                    "telegram_id": telegram_id,
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Bad response from {callback_url}: {e}"
                }
            )

        return {
            "success": True
        }

    # Notifications

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
