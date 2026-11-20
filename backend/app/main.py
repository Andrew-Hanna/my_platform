"""FastAPI application entry point. Routers are attached here; business logic lives in services."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import auth as auth_api
from app.api import users as users_api
from app.api.health import router as health_router
from app.errors import DomainError

app = FastAPI(title="LMS API")
app.include_router(health_router)
app.include_router(auth_api.router)
app.include_router(users_api.router)


@app.exception_handler(DomainError)
def domain_error_handler(request: Request, error: DomainError) -> JSONResponse:
    """Turn a rule violation into a JSON error with the right status code."""
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})
