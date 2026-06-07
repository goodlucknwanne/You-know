from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse
from app.schemas.course import CourseResponse


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    user: UserResponse
    course: CourseResponse

    model_config = {"from_attributes": True}


class EnrollmentSimple(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = {"from_attributes": True}