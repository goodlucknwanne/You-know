from fastapi import FastAPI
from app.db.session import Base, engine
from app.api.endpoints.auth import auth_router
from app.api.endpoints.courses import course_router
from app.api.endpoints.enrollments import enrollment_router


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(course_router, prefix="/courses", tags=["Course"])
app.include_router(enrollment_router, prefix="/enrollments", tags=["Enrollment"])