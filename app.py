from typing import Union, List

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid

from domain import ApiError, WeatherApi, WeatherState, WeatherRepository, \
    UserRepository, UserLoginRepository, User


# Responses

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

class UserResponse(BaseModel):
    success: bool
    telegram_id: int

class SuccessfulLoginResponse(BaseModel):
    success: bool
    callback_url: str

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


def create_app(
    weather_api: WeatherApi,
    weather_repository: WeatherRepository,
    user_repository: UserRepository,
    user_login_repository: UserLoginRepository,
    telegram_service_authorization_token: str
):
    app = FastAPI()

    # Weather

    add_get_weather_route(app, weather_api, user_repository)
    add_get_weather_history_route(app, weather_repository, user_repository)

    # User

    add_user_login_route(app, user_login_repository)
    add_user_successful_login_route(
        app,
        telegram_service_authorization_token,
        user_login_repository,
        user_repository
    )
    add_user_telegram_id_route(
        app,
        user_repository
    )

    return app


# Utils

def find_user(user_repository, token) -> Union[User, JSONResponse]:
    try:
        user = user_repository.get_user(token)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Bad response from UserRepository: {e}"
            }
        )

    if user is None:
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": "Bad token"
            }
        )

# Routes
# - Weather

def add_get_weather_route(
    app: FastAPI,
    weather_api: WeatherApi,
    user_repository: UserRepository
):
    @app.get(
        "/weather",
        response_model=WeatherResponse,
        responses={
            403: forbidden_response,
            500: error_response
        },
    )
    def get_weather(city: str, user_token: str) -> \
            Union[WeatherResponse, ErrorResponse]:
        user = find_user(user_repository, user_token)
        if isinstance(user, JSONResponse):
            return user

        weather = weather_api.get_weather(city, user)
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


def add_get_weather_history_route(
    app: FastAPI,
    weather_repository: WeatherRepository,
    user_repository: UserRepository
):
    @app.get(
        "/weather/history",
        response_model=HistoryResponse,
        responses={
            500: error_response
        },
    )
    def get_weather_history(city: str | None, limit: int, user_token: str) -> \
            Union[HistoryResponse, ErrorResponse]:
        user = find_user(user_repository, user_token)
        if isinstance(user, JSONResponse):
            return user

        try:
            history = weather_repository.get_weather_history(
                city if city is not None else user
            )
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

# - User

def add_user_login_route(
    app: FastAPI,
    user_login_repository: UserLoginRepository
):
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

def add_user_successful_login_route(
    app: FastAPI,
    telegram_service_authorization_token: str,
    user_login_repository: UserLoginRepository,
    user_repository: UserRepository
):
    @app.post(
        "/user/successful_login",
        response_model=SuccessfulLoginResponse,
        responses={
            403: forbidden_response,
            404: not_found_response,
            500: error_response,
        },
    )
    def user_successful_login(token: str, telegram_id: int,
                              authorization_token: str):
        if authorization_token != telegram_service_authorization_token:
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "Forbidden"
                }
            )

        try:
            callback_url = user_login_repository.delete_user_login(token)
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

        authorization_token = str(uuid.uuid4())
        try:
            user_repository.save_user(telegram_id, authorization_token)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Bad response from UserRepository: {e}"
                }
            )

        response = {
            "success": True,
            "callback_url": f"{callback_url}?token={token}&telegram_id=" +
                            f"{telegram_id}&authorization_token=" +
                            f"{authorization_token}",
        }

        return response


def add_user_telegram_id_route(
    app: FastAPI,
    user_repository: UserRepository
):

    @app.get(
        "/user/telegram_id",
        response_model=UserResponse,
        responses={
            403: forbidden_response,
            500: error_response,
        },
    )
    def user_telegram_id(user_token: str):
        user = find_user(user_token)
        if isinstance(user, JSONResponse):
            return user

        return {
            "success": True,
            "telegram_id": user.telegram_id
        }

    return app
