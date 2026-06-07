from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router

app = FastAPI(
    title="Course Enrollment Platform",
    description="A secure RESTful API for managing course enrollments with JWT authentication and RBAC.",
    version="1.0.0",
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


postgres password: 0707