from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from api import router as api_router
from shared.exceptions import AppException

app = FastAPI()

app.include_router(api_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": exc.status_code},
    )
