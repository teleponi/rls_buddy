import sys

import database
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from routers.auth import router as auth_router
from routers.user import router as user_router


def get_app():
    app = FastAPI(
        openapi_url="/users/openapi.json",
        docs_url="/users/docs",
        title="User Microservice",
    )

    app.include_router(auth_router)
    app.include_router(user_router)

    return app


logger.add(
    sys.stderr,
    format="<level>{level}</level> {time} {message}",
    colorize=True,
    level="INFO",
)

app = get_app()
database.init_db()


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
