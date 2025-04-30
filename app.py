from domain import WeatherState, ApiError, WeatherApi
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union


def create_app(weather_api: WeatherApi):
    app = FastAPI()

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

    return app
