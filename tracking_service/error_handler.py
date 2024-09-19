import psycopg2
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


# from main import app


def format_sqlalchemy_error(error):
    """
    Format SQLAlchemy error messages for better readability.
    """
    print("SQLAlchem error type:", type(error))
    try:
        if getattr(error, "orig") and isinstance(error.orig, psycopg2.Error):
            pg_error = error.orig
            return f"{pg_error.pgcode} - {pg_error.pgerror.strip()}"
    except Exception as e:
        print("format sql alchemy:", e)
    return str(error)


#
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(
#     request: Request,
#     exc: RequestValidationError,
# ) -> JSONResponse:
#     return JSONResponse(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         content=jsonable_encoder(
#             {
#                 "input_data": exc.body,
#                 "detail": exc.errors(),
#             }
#         ),
#     )
