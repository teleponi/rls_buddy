"""
Tracking Service - Main Module

Author: Bernd Fischer, 2024
"""

import sys

import database
import models
from database import engine
from events import start_consuming_events
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from routers.symptoms import router as symptoms_router
from routers.trackings import router as trackings_router
from routers.triggers import router as triggers_router


database.init_db()  # Tabellen anlegen


def get_app():
    app = FastAPI(
        openapi_url="/trackings/openapi.json",
        docs_url="/trackings/docs",
        redoc_url="/trackings/redoc",
        title="Tracking Microservice",
    )

    app.include_router(symptoms_router)
    app.include_router(triggers_router)
    app.include_router(trackings_router)

    return app


logger.remove()  # remove default logger
logger.add(
    sys.stderr,
    format="<level>{level}:</level> {module} {message}",
    colorize=True,
    level="INFO",
)

app = get_app()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    try:
        error_msg = [f"{err['loc'][-1]}:{err['msg']}" for err in exc.errors()]
    except Exception as e:
        error_msg = ["Validation error"]
        logger.error(f"Validation exception error: {e}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "input_data": exc.body,
                "detail": error_msg,
            }
        ),
    )


if __name__ == "__main__":
    database.init_db()

start_consuming_events()
