"""Home"""
from fastapi import APIRouter  # FastAPI router

from core.response import ajax_success  # Shared success response

router = APIRouter(tags=["index"])  # Module router without a prefix


@router.get("/")  # Public root route for health checks
def home():
    """Verify that the backend is running"""
    return ajax_success("The backend is running.")  # {code:200, msg}
