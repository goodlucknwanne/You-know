from typing import Optional
from pydantic import BaseModel, field_validator


class CourseCreate(BaseModel):
    title: str
    code: str
    capacity: int

    @field_validator("title", "code")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseResponse(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = {"from_attributes": True}