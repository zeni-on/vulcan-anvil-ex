from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.services.hello_service import DefaultHelloService, HelloService


router = APIRouter()
_hello_service: HelloService = DefaultHelloService()


@router.get("/hello", response_class=PlainTextResponse)
def get_hello_response() -> PlainTextResponse:
    """PGM-001 / API-001 / IT-001: return the hello text response."""
    return PlainTextResponse(_hello_service.get_hello())
