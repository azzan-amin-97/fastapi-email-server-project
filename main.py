from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from app.api.api_v1.api import router as api_router

app = FastAPI(title='FastAPI Email Service',  description="An API Service created using Python Boto 3 and Amazon SES")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"result": exc.errors(),"status": False}),
    )


@app.get("/", tags=['Root Endpoint'])
async def root():
    return {"message": "Welcome to FastAPI Email Service!"}

app.include_router(api_router, prefix="/api")