"""
API Gateway for the Microservices Architecture

This module implements the API Gateway pattern for the microservices architecture
that includes user and tracking services. The API Gateway serves as the single entry
point for client requests, handling routing, proxying, and authorization. It forwards
requests to the appropriate microservices, aggregates results if necessary, and
applies CORS policies for secure cross-origin communication. The primary microservices
handled by this gateway are the User Service and the Tracking Service.

Key features:
- Proxy requests to the User Service and Tracking Service
- Health check endpoints for monitoring the gateway
- Swagger documentation proxying for individual microservices
- CORS middleware for cross-origin requests handling
"""

import logging
import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
TRACKING_SERVICE_URL = os.getenv("TRACKING_SERVICE_URL", "http://tracking-service:8002")

origins = ["*", "127.0.0.1:8000", "127.0.0.1:8001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"message": "API Gateway"}


@app.get("/frontend", response_class=HTMLResponse, include_in_schema=False)
async def get_frontend_prototype(request: Request) -> Response:
    context = {"request": request, "project_name": "RLS-BUDDY"}

    return templates.TemplateResponse("index.html", context)


@app.get("/health", status_code=200, include_in_schema=False)
def health_check() -> Response:
    return Response(status_code=200)


@app.get("/user-docs", include_in_schema=False)
async def proxy_user_docs():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/docs")
        return HTMLResponse(content=response.text)


@app.get("/tracking-docs", include_in_schema=False)
async def proxy_tracking_docs():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TRACKING_SERVICE_URL}/trackings/docs")
        return HTMLResponse(content=response.text)


@app.get("/tracking-redocs", include_in_schema=False)
async def proxy_tracking_redocs():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TRACKING_SERVICE_URL}/trackings/redoc")
        return HTMLResponse(content=response.text)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(
    request: Request,
    full_path: str,
) -> Response:
    """
    Proxies client requests to the appropriate microservice.

    Args:
        request (Request): The incoming HTTP request.
        full_path (str): The path determining the microservice.

    Returns:
        Response: The response from the proxied microservice.

    Raises:
        HTTPException 502: Raised if service not found or proxy request fails.
    """
    headers = dict(request.headers)
    params = dict(request.query_params)

    service_url = determine_service_url(full_path)
    if not service_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    url = f"{service_url}/{full_path}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=params,
                data=await request.body(),
            )
        except (httpx.RequestError, Exception) as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error in proxy request: {e}",
            )

        return Response(
            content=response.content,
            status_code=map_status_code(response.status_code),
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )


def map_status_code(status_code: int) -> int:
    """Map status codes for consistency across services."""
    d = {
        422: 400,  # Unprocessable Entity -> Bad Request
    }
    return d.get(status_code, status_code)


def determine_service_url(path: str) -> str:
    if path.startswith("users") or path.startswith("token"):
        return USER_SERVICE_URL
    elif path.startswith("trackings") or path.startswith("details"):
        return TRACKING_SERVICE_URL
    return None
