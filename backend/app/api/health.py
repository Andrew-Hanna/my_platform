"""Health check endpoint, used by deployment and by the frontend to confirm the API is running."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return a simple status so callers can confirm the API responds."""
    return {"status": "ok"}
