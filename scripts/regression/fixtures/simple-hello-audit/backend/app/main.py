from fastapi import FastAPI

from app.api.hello import router as hello_router


app = FastAPI(title="Python hello API")
app.include_router(hello_router)
