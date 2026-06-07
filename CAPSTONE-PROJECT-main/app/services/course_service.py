from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


def get_active_courses(db: Session) -> List[Course]:
    return db.query(Course).filter(Course.is_active == True).all()


def get_course_by_id(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )
    return course


def create_course(db: Session, data: CourseCreate) -> Course:
    existing = db.query(Course).filter(Course.code == data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course code '{data.code}' already exists",
        )
    course = Course(title=data.title, code=data.code, capacity=data.capacity, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: int, data: CourseUpdate) -> Course:
    course = get_course_by_id(db, course_id)
    if data.code and data.code != course.code:
        conflict = db.query(Course).filter(Course.code == data.code).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course code '{data.code}' already exists",
            )
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> None:
    course = get_course_by_id(db, course_id)
    db.delete(course)
    db.commit()