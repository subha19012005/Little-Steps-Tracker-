from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.assessment import router as assessment_router

app = FastAPI(title="Little Steps Tracker - WHO Growth Assessment")


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _request: Request, error: RequestValidationError
) -> JSONResponse:
    detail = "; ".join(
        f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
        for item in error.errors()
    )
    return JSONResponse(status_code=400, content={"detail": detail})


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "WHO Growth Assessment API is running"}


app.include_router(assessment_router)