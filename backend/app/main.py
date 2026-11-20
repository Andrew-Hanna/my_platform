"""FastAPI application entry point. Routers are attached here; business logic lives in services."""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="LMS API")
app.include_router(health_router)
