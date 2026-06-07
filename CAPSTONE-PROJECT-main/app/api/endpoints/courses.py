from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import (
    create_course,
    delete_course,
    get_active_courses,
    get_course_by_id,
    update_course,
)

course_router = APIRouter()


@course_router.get("/", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    """Retrieve all active courses (public)."""
    return get_active_courses(db)


@course_router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Retrieve a course by ID (public)."""
    return get_course_by_id(db, course_id)


@course_router.post("/", response_model=CourseResponse, status_code=201)
def create(data: CourseCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Create a new course (admin only)."""
    return create_course(db, data)


@course_router.put("/{course_id}", response_model=CourseResponse)
def update(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Update course details (admin only)."""
    return update_course(db, course_id, data)


@course_router.delete("/{course_id}", status_code=204)
def delete(course_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Delete a course (admin only)."""
    delete_course(db, course_id)